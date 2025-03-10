from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import RegistroView  # Importar la vista basada en clases
urlpatterns = [
    path ('', views.index, name='articulos'),
    path ('listar_articulos', views.listar_articulos, name='listar_articulos'),
    path('articulos/crear', views.crear_articulo, name='crear_articulo'),
    path ('mesas', views.mesas, name='listar_mesas'),
    path('alta_mesa', views.insertar_mesa, name='alta_mesas'),
    path('baja_mesa', views.delete_mesa, name='baja_mesas'),
    path('mesas/modificar/<int:mesa_id>', views.modificar_mesa, name='modificar_mesa'),
    path('pagina_articulos_inicio', views.pagina, name='pagina_pedidos'),
    path('articulos/modificar/<int:articulo_id>', views.modificar_articulo, name='modificar_articulo'),
    path('pedidos', views.insertar_mesa, name='pedidos'),
    path('pagina_articulos', views.crear_pedido, name='crear_pedidos'),
    path('iniciar-sesion/', views.inicio_sesion, name='inicio_sesion'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('iniciar-sesion-cerrar', views.cerrar_sesion, name='inicio_sesion'),
    path('listar_pedidos/', views.listar_pedidos, name='listar_pedidos'),
    path('pedidos/cambiar_estado/<int:pedido_id>', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
    path('sectores/', views.listar_sectores, name='listar_sectores'),
    path('sectores/crear/', views.crear_sector, name='crear_sector'),
    path('sectores/modificar/<int:sector_id>', views.modificar_sector, name='modificar_sector'),
    path('sectores/eliminar/<int:sector_id>', views.eliminar_sector, name='eliminar_sector'),
    path('stocks/', views.listar_stocks, name='listar_stock'),
    path('stocks/modificar/<int:stock_id>', views.modificar_stock, name='modificar_stock'),
    path('pedidos/exportar', views.exportar_pedidos_excel, name='exportar_pedidos_excel'),
    path('documento_prueba', views.listar_stocks, name='documento'),


    

    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
