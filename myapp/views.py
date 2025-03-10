from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import articulos, Mesas, Sector, Pedido, DetallePedido, Stock
from .forms import SectorForm, StockForm, ArticuloForm, RegistroForm
import json
from openpyxl import Workbook


# Vistas para Artículos
def index(request):
    articulos_list = articulos.objects.all()  # Obtener todos los artículos
    return render(request, 'index.html', {'articulos': articulos_list})


def listar_articulos(request):
    vigente_seleccionado = request.GET.get('vigente', '')
    if vigente_seleccionado == 'True':
        articulos_list = articulos.objects.filter(vigente=True)
    elif vigente_seleccionado == 'False':
        articulos_list = articulos.objects.filter(vigente=False)
    else:
        articulos_list = articulos.objects.all()
    return render(request, 'index.html', {
        'articulos': articulos_list,
        'vigente_seleccionado': vigente_seleccionado
    })


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


def modificar_articulo(request, articulo_id):
    articulo = get_object_or_404(articulos, id=articulo_id)
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
def mesas(request):
    mesas_list = Mesas.objects.select_related('id_sector').all()
    sectores = Sector.objects.all()
    return render(request, 'mesas.html', {
        'mesas': mesas_list,
        'sectores': sectores
    })


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


def delete_mesa(request):
    if request.method == 'POST':
        id_mesa = request.POST.get('id_mesa')
        mesa = get_object_or_404(Mesas, id=id_mesa)
        mesa.vigente = False
        mesa.save()
        return redirect('listar_mesas')

    return redirect('listar_mesas')


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


# Vistas para Pedidos
def crear_pedido(request):
    if request.method == 'POST':
        try:
            id_mesa = request.POST.get('id_mesa')
            carrito_data = json.loads(request.POST.get('carrito_data'))
            mesa = Mesas.objects.get(id=id_mesa)

            pedido = Pedido.objects.create(
                id_mesa=mesa,
                cantidad_item=len(carrito_data),
                subtotal=0.0
            )

            for articulo_id, item in carrito_data.items():
                articulo = articulos.objects.get(id=articulo_id)
                DetallePedido.objects.create(
                    pedido=pedido,
                    articulo=articulo,
                    cantidad=item['cantidad'],
                    precio_unitario=item['precio'],
                    precio_final=item['precio'] * item['cantidad']
                )

            pedido.actualizar_subtotal()
            messages.success(request, 'Pedido creado correctamente.')
            return redirect('pagina_pedidos')

        except Exception as e:
            messages.error(request, f'Error al crear el pedido: {str(e)}')
            return redirect('pagina_pedidos')

    return render(request, 'pagina_articulos.html')


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

    return render(request, 'listar_pedidos.html', {
        'pedidos': pedidos_list,
        'estado_seleccionado': estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })


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


# Vistas para Sectores
def listar_sectores(request):
    sectores = Sector.objects.all()
    form = SectorForm()
    return render(request, 'listar_sectores.html', {
        'sectores': sectores,
        'form': form,
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


def eliminar_sector(request, sector_id):
    sector = get_object_or_404(Sector, id=sector_id)
    sector.delete()
    messages.success(request, 'Sector eliminado correctamente.')
    return redirect('listar_sectores')


# Vistas para Stocks
def listar_stocks(request):
    stocks = Stock.objects.all().select_related('articulo')
    return render(request, 'listar_stock.html', {'stocks': stocks})


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


# Vistas de Autenticación
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
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'inicio_sesion.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('inicio_sesion')