import qrcode
from django.db.models.signals import post_save
from django.dispatch import receiver
from io import BytesIO
from django.core.files import File
from .models import Mesas

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files import File
from io import BytesIO
import qrcode

@receiver(post_save, sender=Mesas)
def generate_qr_code(sender, instance, created, **kwargs):
    if created:  # Solo generar el QR si es una nueva mesa, no si es una actualización
        # Generar la URL para la mesa
        base_url = "http://127.0.0.1:8000/admin/myapp/mesas/"  # Cambia esto por la URL base de tu sitio
        url = f"{base_url}/{instance.id}"  # URL única para la mesa

        # Contenido del QR (incluyendo la URL)
        qr_content = f"{url}\nMesa: {instance.numero_mesa}, Sector: {instance.id_sector.nombre}"

        # Generar el código QR
        qr = qrcode.make(qr_content)

        # Guardar QR como archivo en memoria
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)

        # Asignar el archivo al campo qr_codigo de la mesa
        filename = f"mesa_{instance.numero_mesa}_qr.png"
        instance.qr_codigo.save(filename, File(buffer), save=False)  # No guardamos el modelo aún

        # Guardar los cambios en el modelo sin causar recursión
        instance.save(update_fields=["qr_codigo"])  # Solo actualizamos el campo qr_codigo

