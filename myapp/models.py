from django.db import models
from django.contrib.auth.models import User

# Modelo para los artículos
class articulos(models.Model):
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=200, default='')
    precio = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)
    vigente = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to='imagenes_articulos/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - Marca: {self.marca}"

# Modelo para los sectores
class Sector(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

# Modelo para las mesas
class Mesas(models.Model):
    numero_mesa = models.IntegerField()
    id_sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        related_name='mesas'
    )
    vigente = models.BooleanField(default=True)
    qr_codigo = models.ImageField(upload_to='qrs/', null=True, blank=True)

    def __str__(self):
        return f"Mesa {self.numero_mesa} - Sector: {self.id_sector.nombre}"

# Modelo para los pedidos
class Pedido(models.Model):
    # Opciones para el estado del pedido
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregado', 'Entregado'),
        ('cobrado', 'Cobrado'),
    ]

    id_mesa = models.ForeignKey(
        Mesas,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha_pedido = models.DateField(auto_now_add=True)
    cantidad_item = models.IntegerField(default=0)
    subtotal = models.DecimalField(max_digits=100, decimal_places=2, default=0.0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')  # Nuevo campo

    def __str__(self):
        return f"Pedido {self.id} - Mesa {self.id_mesa.numero_mesa}"

    def actualizar_subtotal(self):
        self.subtotal = sum(detalle.precio_final for detalle in self.detalles.all())
        self.save()

# Modelo para los detalles de los pedidos
class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    articulo = models.ForeignKey(
        articulos,
        on_delete=models.CASCADE,
        related_name='detalles_pedido'
    )
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    precio_final = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle {self.id} - Pedido {self.pedido.id}"

    def save(self, *args, **kwargs):
        self.precio_final = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

# Modelo para el stock de los artículos
class Stock(models.Model):
    articulo = models.OneToOneField(
        articulos,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name='Artículo'
    )
    cantidad = models.IntegerField(
        default=0,
        verbose_name='Cantidad disponible'
    )
    fecha_modificacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de modificación'
    )
    minimo_stock = models.IntegerField(
        default=10,
        verbose_name='Mínimo de stock'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    def __str__(self):
        return f"Stock de {self.articulo.nombre} - Cantidad: {self.cantidad}"

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stocks'
        ordering = ['-fecha_modificacion']

# Modelo para el perfil de usuario
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name='Usuario'
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de nacimiento'
    )

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuarios'
