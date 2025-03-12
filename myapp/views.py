from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .models import Articulos, Mesas, Sector, Pedido, DetallePedido, Stock  # Cambiado a Articulos
from .forms import SectorForm, StockForm, ArticuloForm, PerfilUsuarioForm, PerfilUsuario, RegistroUsuarioForm
import json
from openpyxl import Workbook
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.serializers import serialize



# Vistas para Artículos
@login_required
def inicio(request):
    return render(request, 'pagina_inicio.html')

@login_required
def index(request):
    articulos_list = Articulos.objects.all()  # Cambiado a Articulos
    return render(request, 'index.html', {'articulos': articulos_list})

@login_required
def listar_articulos(request):
    vigente_seleccionado = request.GET.get('vigente', '')
    if vigente_seleccionado == 'True':
        articulos_list = Articulos.objects.filter(vigente=True)  # Cambiado a Articulos
    elif vigente_seleccionado == 'False':
        articulos_list = Articulos.objects.filter(vigente=False)  # Cambiado a Articulos
    else:
        articulos_list = Articulos.objects.all()  # Cambiado a Articulos
    return render(request, 'index.html', {
        'articulos': articulos_list,
        'vigente_seleccionado': vigente_seleccionado
    })

@login_required
def crear_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            articulo = form.save()
            Stock.objects.create(
                articulo=articulo,
                cantidad=0,
                minimo_stock=10,
                activo=True
            )
            messages.success(request, 'Artículo creado correctamente.')
            return redirect('listar_articulos')
    else:
        form = ArticuloForm()
    return render(request, 'crear_articulo.html', {'form': form})

@login_required
def modificar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulos, id=articulo_id)  # Cambiado a Articulos
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        marca = request.POST.get('marca')
        precio = request.POST.get('precio')
        vigente = request.POST.get('vigente') == 'True'
        imagen = request.FILES.get('imagen')

        articulo.nombre = nombre
        articulo.marca = marca
        articulo.precio = precio
        articulo.vigente = vigente

        if imagen:
            articulo.imagen = imagen

        articulo.save()
        messages.success(request, 'Artículo modificado correctamente.')
        return redirect('listar_articulos')

    return render(request, 'modificar_articulo.html', {'articulo': articulo})


# Vistas para Mesas
@login_required
def mesas(request):
    mesas_list = Mesas.objects.select_related('id_sector').all()
    sectores = Sector.objects.all()
    return render(request, 'mesas.html', {
        'mesas': mesas_list,
        'sectores': sectores
    })

@login_required
def insertar_mesa(request):
    if request.method == 'POST':
        numero_mesa = request.POST.get('numero_mesa')
        vigente = request.POST.get('vigente') == 'on'
        id_sector = request.POST.get('id_sector')

        Mesas.objects.create(
            numero_mesa=numero_mesa,
            vigente=vigente,
            id_sector=Sector.objects.get(id=id_sector)
        )
        return redirect('listar_mesas')

    return redirect('listar_mesas')

@login_required
def delete_mesa(request):
    if request.method == 'POST':
        id_mesa = request.POST.get('id_mesa')
        mesa = get_object_or_404(Mesas, id=id_mesa)
        mesa.vigente = False
        mesa.save()
        return redirect('listar_mesas')

    return redirect('listar_mesas')

@login_required
def modificar_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesas, id=mesa_id)
    if request.method == 'POST':
        numero_mesa = request.POST.get('numero_mesa')
        vigente = request.POST.get('vigente') == 'on'
        id_sector = request.POST.get('id_sector')

        mesa.numero_mesa = numero_mesa
        mesa.vigente = vigente
        mesa.id_sector = Sector.objects.get(id=id_sector)
        mesa.save()

        messages.success(request, 'Mesa modificada correctamente.')
        return redirect('listar_mesas')

    sectores = Sector.objects.all()
    return render(request, 'mesas.html', {
        'mesa': mesa,
        'sectores': sectores,
    })


@login_required
def crear_pedido(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            id_mesa = request.POST.get('id_mesa')
            carrito_data = json.loads(request.POST.get('carrito_data'))
            
            # Verificar que se haya seleccionado una mesa
            if not id_mesa:
                messages.error(request, 'Debe seleccionar una mesa.')
                return redirect('pagina_pedidos')

            # Obtener la mesa
            try:
                mesa = Mesas.objects.get(id=id_mesa)
            except Mesas.DoesNotExist:
                messages.error(request, 'La mesa seleccionada no existe.')
                return redirect('pagina_pedidos')

            # Crear el pedido
            pedido = Pedido.objects.create(
                id_mesa=mesa,
                cantidad_item=len(carrito_data),
                subtotal=0.0  # El subtotal se actualizará después
            )

            # Crear los detalles del pedido y descontar el stock
            for articulo_id, item in carrito_data.items():
                try:
                    articulo = Articulos.objects.get(id=articulo_id)
                    stock = Stock.objects.get(articulo=articulo)

                    # Verificar si hay suficiente stock
                    if stock.cantidad < item['cantidad']:
                        messages.error(request, f'No hay suficiente stock para {articulo.nombre}.')
                        pedido.delete()  # Eliminar el pedido si no hay suficiente stock
                        return redirect('pagina_pedidos')

                    # Descontar el stock
                    stock.cantidad -= item['cantidad']
                    stock.save()

                    # Crear el detalle del pedido
                    DetallePedido.objects.create(
                        pedido=pedido,
                        articulo=articulo,
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio'],
                        precio_final=item['precio'] * item['cantidad']
                    )
                except Articulos.DoesNotExist:
                    messages.error(request, f'El artículo con ID {articulo_id} no existe.')
                    pedido.delete()  # Eliminar el pedido si el artículo no existe
                    return redirect('pagina_pedidos')
                except Stock.DoesNotExist:
                    messages.error(request, f'No se encontró el stock para {articulo.nombre}.')
                    pedido.delete()  # Eliminar el pedido si no hay stock
                    return redirect('pagina_pedidos')

            # Actualizar el subtotal del pedido
            pedido.actualizar_subtotal()

            # Mensaje de éxito
            messages.success(request, 'Pedido confirmado correctamente.')
            return redirect('pagina_pedidos')

        except Exception as e:
            # Manejar errores
            messages.error(request, f'Error al crear el pedido: {str(e)}')
            return redirect('pagina_pedidos')

    return render(request, 'pagina_articulos.html')

@login_required
def listar_pedidos(request):
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    pedidos_list = Pedido.objects.all()
    if estado:
        pedidos_list = pedidos_list.filter(estado=estado)
    if fecha_inicio:
        pedidos_list = pedidos_list.filter(fecha_pedido__gte=fecha_inicio)
    if fecha_fin:
        pedidos_list = pedidos_list.filter(fecha_pedido__lte=fecha_fin)

    # Convertir los detalles de cada pedido en una lista de diccionarios
    for pedido in pedidos_list:
        detalles = pedido.detalles.all().values(
            'id', 'articulo__nombre', 'cantidad', 'precio_unitario', 'precio_final'
        )
        pedido.detalles_json = list(detalles)  # Convertir QuerySet a lista de diccionarios

    return render(request, 'listar_pedidos.html', {
        'pedidos': pedidos_list,
        'estado_seleccionado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })


@login_required
def vista_pedidos_cocina(request):
    # Filtrar solo los pedidos con estado "pendiente"
    pedidos = Pedido.objects.filter(estado='pendiente').order_by('-fecha_pedido')

    # Preparar los datos para la plantilla
    pedidos_data = []
    for pedido in pedidos:
        detalles = pedido.detalles.all().values('articulo__nombre', 'cantidad', 'articulo__imagen')
        pedidos_data.append({
            'mesa': pedido.id_mesa.numero_mesa,
            'detalles': list(detalles)
        })

    return render(request, 'vista_pedidos_cocina.html', {
        'pedidos': pedidos_data
    })

@login_required
def vista_pedidos_cocina_json(request):
    pedidos = Pedido.objects.filter(estado='pendiente').order_by('-fecha_pedido')
    pedidos_data = []

    for pedido in pedidos:
        detalles = pedido.detalles.all().values('articulo__nombre', 'cantidad')
        pedidos_data.append({
            'mesa': pedido.id_mesa.numero_mesa,
            'detalles': list(detalles)
        })

    return JsonResponse({'pedidos': pedidos_data})

@login_required
def cambiar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(pedido.ESTADO_CHOICES).keys():
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'El estado del pedido {pedido.id} ha sido actualizado a {pedido.get_estado_display()}.')
        else:
            messages.error(request, 'Estado no válido.')
    return redirect('listar_pedidos')

def comprobante_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    detalles = pedido.detalles.all()
    return render(request, 'comprobante_pedido.html', {'pedido': pedido, 'detalles': detalles})


@login_required
def exportar_pedidos_excel(request):
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    pedidos_list = Pedido.objects.all()
    if estado:
        pedidos_list = pedidos_list.filter(estado=estado)
    if fecha_inicio:
        pedidos_list = pedidos_list.filter(fecha_pedido__gte=fecha_inicio)
    if fecha_fin:
        pedidos_list = pedidos_list.filter(fecha_pedido__lte=fecha_fin)

    wb = Workbook()
    ws = wb.active
    ws.title = "Pedidos"
    ws.append(["ID Pedido", "Mesa", "Fecha", "Subtotal", "Estado"])

    for pedido in pedidos_list:
        ws.append([
            pedido.id,
            f"Mesa {pedido.id_mesa.numero_mesa} - Sector {pedido.id_mesa.id_sector.nombre}",
            pedido.fecha_pedido,
            pedido.subtotal,
            pedido.get_estado_display(),
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=pedidos.xlsx'
    wb.save(response)
    return response

@login_required
def obtener_detalles_pedido(request, pedido_id):
    detalles = DetallePedido.objects.filter(pedido_id=pedido_id).values(
        'id', 'articulo__nombre', 'cantidad', 'precio_unitario', 'precio_final'
    )
    return JsonResponse(list(detalles), safe=False)

# Vistas para Sectores
@login_required
def listar_sectores(request):
    sectores = Sector.objects.all()
    form = SectorForm()
    return render(request, 'listar_sectores.html', {
        'sectores': sectores,
        'form': form,
    })

@login_required
def crear_sector(request):
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sector creado correctamente.')
        else:
            messages.error(request, 'Error al crear el sector. Verifica los datos.')
        return redirect('listar_sectores')

@login_required
def modificar_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    if request.method == 'POST':
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sector modificado correctamente.')
        else:
            messages.error(request, 'Error al modificar el sector. Verifica los datos.')
        return redirect('listar_sectores')

@login_required
def eliminar_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    sector.delete()
    messages.success(request, 'Sector eliminado correctamente.')
    return redirect('listar_sectores')


# Vistas para Stocks
@login_required
def listar_stocks(request):
    stocks = Stock.objects.all().select_related('articulo')
    return render(request, 'listar_stock.html', {'stocks': stocks})

@login_required
def modificar_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, 'Stock modificado correctamente.')
        else:
            messages.error(request, 'Error al modificar el stock. Verifica los datos.')
        return redirect('listar_stock')





def inicio_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            
            # Redirigir al usuario a la URL especificada en el parámetro "next"
            next_url = request.POST.get('next', '/')  # Si no hay "next", redirigir a la página principal
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        # Pasar el parámetro "next" al contexto del formulario
        next_url = request.GET.get('next', '/')
    return render(request, 'inicio_sesion.html', {'next': next_url})

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('inicio_sesion')

@login_required
def gestionar_perfil(request):
    # Obtener el perfil del usuario actual, o crearlo si no existe
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('gestionar_perfil')
    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(request, 'gestionar_perfil.html', {'form': form, 'perfil': perfil})

def editar_perfil(request, id):
    perfil = get_object_or_404(PerfilUsuario, id=id)
    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = PerfilUsuarioForm(instance=perfil)
    return render(request, 'editar_perfil.html', {'form': form})

def listar_usuarios(request):
    # Obtener todos los perfiles de usuario con su información relacionada
    perfiles = PerfilUsuario.objects.select_related('usuario').all()
    return render(request, 'listar_usuarios.html', {'perfiles': perfiles})

def registro(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():  # Verificar si el usuario ya existe
                messages.error(request, 'El nombre de usuario ya está en uso. Por favor, elige otro.')
            else:
                form.save()  # Guardar el usuario en la base de datos
                messages.success(request, f'Cuenta creada para {username}. ¡Ahora puedes iniciar sesión!')
                return redirect('inicio_sesion')  # Redirigir a la página de inicio de sesión
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro.html', {'form': form})


def pagina(request):
    numero_mesa = request.GET.get('mesa')  # Captura el parámetro 'mesa' de la URL
    try:
        mesa = Mesas.objects.get(numero_mesa=numero_mesa)  # Obtén la mesa por su número
    except Mesas.DoesNotExist:
        mesa = None  # Si no existe, asigna None

    context = {
        'articulos': Articulos.objects.all(),
        'mesas': Mesas.objects.all(),
        'mesa': mesa,  # Pasa la instancia de la mesa al contexto
    }
    return render(request, 'pagina_articulos.html', context)