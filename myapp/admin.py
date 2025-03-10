from django.contrib import admin
from .models  import Articulos, Mesas, Sector, Pedido, DetallePedido, Stock

admin.site.register(Articulos)
admin.site.register(Mesas)
admin.site.register(Sector)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'id_mesa', 'fecha_pedido', 'cantidad_item', 'subtotal')

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido', 'articulo', 'cantidad', 'precio_unitario', 'precio_final')
# Register your models here.

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    # Campos que se mostrarán en la lista de registros
    list_display = ('articulo', 'cantidad', 'minimo_stock', 'activo', 'fecha_modificacion')
    
    # Campos por los que se puede filtrar
    list_filter = ('activo', 'fecha_modificacion')
    
    # Campos por los que se puede buscar
    search_fields = ('articulo__nombre',)
    
    # Campos editables directamente en la lista
    list_editable = ('cantidad', 'minimo_stock', 'activo')
    
    # Ordenar por fecha de modificación (el más reciente primero)
    ordering = ('-fecha_modificacion',)
    
    # Campos que se mostrarán en el formulario de edición
    fieldsets = (
        ('Información del Artículo', {
            'fields': ('articulo',),
        }),
        ('Gestión de Stock', {
            'fields': ('cantidad', 'minimo_stock', 'activo'),
        }),
    )

