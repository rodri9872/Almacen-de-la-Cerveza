from django import forms
from .models import Sector, Stock, articulos, PerfilUsuario
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User



class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
        }

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['cantidad', 'minimo_stock', 'activo']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimo_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ArticuloForm(forms.ModelForm):
    cantidad_inicial = forms.IntegerField(
        label="Cantidad Inicial",
        min_value=0,
        initial=0,  # Stock inicial por defecto
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    minimo_stock = forms.IntegerField(
        label="Mínimo de Stock",
        min_value=0,
        initial=10,  # Mínimo de stock por defecto
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = articulos
        fields = ['nombre', 'marca', 'precio', 'imagen', 'cantidad_inicial', 'minimo_stock']

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
