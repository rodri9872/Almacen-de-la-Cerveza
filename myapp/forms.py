from django import forms
from .models import Sector, Stock, Articulos, PerfilUsuario
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
        model = Articulos
        fields = ['nombre', 'marca', 'precio', 'imagen', 'cantidad_inicial', 'minimo_stock']


class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['telefono', 'direccion', 'fecha_nacimiento']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            
        }
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():  # Verificar si el usuario ya existe
            raise forms.ValidationError('El nombre de usuario ya está en uso. Por favor, elige otro.')
        return username