# Generated by Django 5.0.7 on 2025-01-09 02:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_articulos'),
    ]

    operations = [
        migrations.AddField(
            model_name='articulos',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes_articulos/'),
        ),
    ]
