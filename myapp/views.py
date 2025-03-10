from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from .models import articulos, Mesas, Sector, Pedido, DetallePedido, Stock
from django.shortcuts import redirect, get_object_or_404   
from django.contrib import messages
import json
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .forms import SectorForm, StockForm, ArticuloForm, RegistroForm
from openpyxl import Workbook 
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib import messages


# Create your views here.

def HolaMundo(request, username):
    print (username)
    return HttpResponse('Hola %s' % username)

def index(request):
    articulo = articulos.objects.all()  # Obtener todos los artículos
    return render(request, 'index.html', {
        'articulo': articulo  # Pasar los datos consultados, no el modelo
    })

def crear_articulo(request):
    if request.method == 'POST':
        form = ArticuloForm(request.POST, request.FILES)  # Maneja el archivo de imagen
        if form.is_valid():
            # Guardar el artículo
            articulo = form.save()

            # Crear un registro de stock asociado al artículo
            Stock.objects.create(
                articulo=articulo,
                cantidad=0,  # Stock inicial (puedes cambiarlo según tus necesidades)
                minimo_stock=10,  # Mínimo de stock por defecto
                activo=True  # Por defecto, el stock está activo
            )

            # Mensaje de éxito
            messages.success(request, 'Artículo creado correctamente.')

            # Redirigir a la lista de artículos
            return redirect('listar_articulos')  # Cambia 'listar_articulos' por la URL correcta
    else:
        form = ArticuloForm()

    return render(request, 'crear_articulo.html', {'form': form})

def listar_articulos(request):
    # Obtener el estado seleccionado del formulario (si existe)
    vigente_seleccionado = request.GET.get('vigente', '')

    # Filtrar los artículos según el estado
    if vigente_seleccionado == 'True':
        articulo = articulos.objects.filter(vigente=True)
    elif vigente_seleccionado == 'False':
        articulo = articulos.objects.filter(vigente=False)
    else:
        articulo = articulos.objects.all()

    # Pasar los artículos y el estado seleccionado a la plantilla
    context = {
        'articulo': articulo,  # Asegúrate de que el nombre coincida con el usado en la plantilla
        'vigente_seleccionado': vigente_seleccionado
    }
    return render(request, 'index.html', context)

def pagina(request):
    articulo = articulos.objects.all()  # Obtener todos los artículos
    return render(request, 'pagina_articulos.html', {
        'articulo': articulo  # Pasar los datos consultados, no el modelo
    })

def mesas(request):
    mesas = Mesas.objects.select_related('id_sector').all()
    sectores = Sector.objects.all()
    return render(request, 'mesas.html', {
        'mesas': mesas,
        'sectores': sectores
    })



def insertar_mesa(request):
    if request.method == 'POST':
        numero_mesa = request.POST.get('numero_mesa')
        vigente = request.POST.get('vigente') == 'on'  # Convertir checkbox a booleano
        id_sector = request.POST.get('id_sector')

        # Crear nueva mesa
        Mesas.objects.create(
            numero_mesa=numero_mesa,
            vigente=vigente,
            id_sector=Sector.objects.get(id=id_sector)
        )

        return redirect('alta_mesas')  # Cambia esto al nombre de la vista principal
    
    # Si no es POST, redirigir al formulario o vista de alta
    return redirect('listar_mesas')  # Cambia esto según la vista que quieras mostrar

def crear_pedido(request):
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            id_mesa = request.POST.get('id_mesa')
            carrito_data = json.loads(request.POST.get('carrito_data'))

            # Verificar si la mesa existe
            mesa = Mesas.objects.get(id=id_mesa)

            # Crear el pedido
            pedido = pedido.objects.create(
                id_mesa=mesa,
                cantidad_item=len(carrito_data),
                subtotal=0.0
            )

            # Crear los detalles del pedido
            for articulo_id, item in carrito_data.items():
                articulo = articulos.objects.get(id=articulo_id)
                DetallePedido.objects.create(
                    pedido=pedido,
                    articulo=articulo,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    precio_final=item['precio'] * item['cantidad']
                )

            # Actualizar el subtotal del pedido
            pedido.actualizar_subtotal()

            messages.success(request, 'Pedido creado correctamente.')
            return redirect('pagina_pedidos')  # Redirigir a la lista de pedidos

        except Exception as e:
            messages.error(request, f'Error al crear el pedido: {str(e)}')
            return redirect('pagina_pedidos')

    return render(request, 'pagina_articulos.html')


def delete_mesa(request):
    if request.method == 'POST':
        id_mesa = request.POST.get('id_mesa')  # Obtenemos el número de mesa
        
        # Buscar la mesa específica y marcarla como no vigente
        mesa = get_object_or_404(Mesas, id=id_mesa)  # Usamos el ID de la mesa
        mesa.vigente = False  # Cambiar el estado de vigencia
        mesa.save()  # Guardar los cambios

        return redirect('baja_mesas')  # Cambia esto al nombre de la vista principal
    
    # Si no es POST, redirigir a la vista de listado
    return redirect('listar_mesas')  # Cambia esto según la vista que quieras mostrar


def detalle_mesa(request, mesa_id):
    mesa = get_object_or_404(Mesas, id=mesa_id)
    return render(request, 'pagina_articulos.html', {'mesa': mesa})

def modificar_mesa(request, mesa_id):
    # Obtener la mesa que se va a modificar
    mesa = get_object_or_404(Mesas, id=mesa_id)

    if request.method == 'POST':
        # Procesar el formulario enviado
        numero_mesa = request.POST.get('numero_mesa')
        vigente = request.POST.get('vigente') == 'on'  # 'on' si el checkbox está marcado
        id_sector = request.POST.get('id_sector')

        # Actualizar los campos de la mesa
        mesa.numero_mesa = numero_mesa
        mesa.vigente = vigente
        mesa.id_sector = Sector.objects.get(id=id_sector)  # Obtener el objeto Sector
        mesa.save()

        # Mostrar un mensaje de éxito
        messages.success(request, 'Mesa modificada correctamente.')

        # Redirigir a la página de mesas
        return redirect('listar_mesas')  # Cambia 'nombre_de_la_url_mesas' por la URL correcta

    # Si no es POST, mostrar el formulario con los datos actuales
    sectores = Sector.objects.all()  # Obtener todos los sectores para el select
    return render(request, 'mesas.html', {
        'mesa': mesa,
        'sectores': sectores,
    })

def modificar_articulo(request, articulo_id):
    articulo = get_object_or_404(articulos, id=articulo_id)

    if request.method == 'POST':
        # Procesar el formulario enviado
        nombre = request.POST.get('nombre')
        marca = request.POST.get('marca')
        precio = request.POST.get('precio')
        vigente = request.POST.get('vigente') == 'True'
        imagen = request.FILES.get('imagen')  # Obtener la imagen del formulario

        # Actualizar los campos del artículo
        articulo.nombre = nombre
        articulo.marca = marca
        articulo.precio = precio
        articulo.vigente = vigente

        # Actualizar la imagen solo si se proporciona una nueva
        if imagen:
            articulo.imagen = imagen

        articulo.save()

        # Mostrar un mensaje de éxito
        messages.success(request, 'Artículo modificado correctamente.')

        # Redirigir a la página de artículos
        return redirect('listar_articulos')  # Cambia 'listar_articulos' por la URL correcta

    # Si no es POST, mostrar el formulario con los datos actuales
    return render(request, 'modificar_articulo.html', {
        'articulo': articulo,
    })

def menu(request):
    articulos = articulos.objects.all()
    mesas = Mesas.objects.all()  # Obtener todas las mesas
    return render(request, 'menu.html', {'articulos': articulos, 'mesas': mesas})

def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar-sesion/')  # Redirigir a la página de inicio



class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'registro.html'
    success_url = reverse_lazy('inicio_sesion')

    def form_valid(self, form):
        messages.success(self.request, '¡Registro exitoso! Por favor, inicia sesión.')
        return super().form_valid(form)
    
def inicio_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.username}!')
            return redirect('articulos')  # Cambia 'articulos' por la URL correcta
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'inicio_sesion.html')


def listar_pedidos(request):
    # Obtener los parámetros de búsqueda
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar los pedidos
    pedidos = Pedido.objects.all()
    if estado:
        pedidos = pedidos.filter(estado=estado)
    if fecha_inicio:
        pedidos = pedidos.filter(fecha_pedido__gte=fecha_inicio)
    if fecha_fin:
        pedidos = pedidos.filter(fecha_pedido__lte=fecha_fin)

    # Pasar los pedidos y los filtros al contexto
    context = {
        'pedidos': pedidos,
        'estado_seleccionado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'listar_pedidos.html', context)

def exportar_pedidos_excel(request):
    # Obtener los parámetros de búsqueda
    estado = request.GET.get('estado', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    # Filtrar los pedidos
    pedidos = Pedido.objects.all()
    if estado:
        pedidos = pedidos.filter(estado=estado)
    if fecha_inicio:
        pedidos = pedidos.filter(fecha_pedido__gte=fecha_inicio)
    if fecha_fin:
        pedidos = pedidos.filter(fecha_pedido__lte=fecha_fin)

    # Crear un libro de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Pedidos"

    # Agregar encabezados
    ws.append(["ID Pedido", "Mesa", "Fecha", "Subtotal", "Estado"])

    # Agregar datos
    for pedido in pedidos:
        ws.append([
            pedido.id,
            f"Mesa {pedido.id_mesa.numero_mesa} - Sector {pedido.id_mesa.id_sector.nombre}",
            pedido.fecha_pedido,
            pedido.subtotal,
            pedido.get_estado_display(),
        ])

    # Guardar el archivo en la respuesta
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=pedidos.xlsx'
    wb.save(response)

    return response


def cambiar_estado_pedido(request, pedido_id):  # Asegúrate de que el parámetro sea "pedidos_id"
    pedido = get_object_or_404(Pedido, id=pedido_id)  # Usar "pedidos_id" aquí
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        if nuevo_estado in dict(pedido.ESTADO_CHOICES).keys():
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f'El estado del pedido {pedido.id} ha sido actualizado a {pedido.get_estado_display()}.')
        else:
            messages.error(request, 'Estado no válido.')
    
    return redirect('listar_pedidos')


# Listar todos los sectores
def listar_sectores(request):
    sectores = Sector.objects.all()
    form = SectorForm()  # Formulario para crear un nuevo sector
    return render(request, 'listar_sectores.html', {
        'sectores': sectores,
        'form': form,  # Pasamos el formulario al contexto
    })

def crear_sector(request):
    if request.method == 'POST':
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sector creado correctamente.')
        else:
            messages.error(request, 'Error al crear el sector. Verifica los datos.')
        return redirect('listar_sectores')

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
    
# Eliminar un sector
def eliminar_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    sector.delete()
    messages.success(request, 'Sector eliminado correctamente.')
    return redirect('listar_sectores')

# Listar todos los stocks
def listar_stocks(request):
    stocks = Stock.objects.all().select_related('articulo')
    return render(request, 'listar_stock.html', {'stocks': stocks})

# Modificar el stock de un artículo
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