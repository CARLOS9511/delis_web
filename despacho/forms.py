from django import forms
from django.forms import inlineformset_factory
from .models import Despacho, DetalleDespacho
from sucursales.models import Sucursales
from produccion.models import Producto


class DespachoForm(forms.ModelForm):
    """Formulario para crear/editar despachos"""
    class Meta:
        model = Despacho
        fields = ['sucursal', 'estado', 'descuento', 'tanda', 'chofer']
        widgets = {
            'sucursal': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'estado': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descuento': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'value': '0'
            }),
            'tanda': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tanda-1'
            }),
            'chofer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del chofer'
            }),
        }
        labels = {
            'sucursal': 'Sucursal destino',
            'estado': 'Estado del despacho',
            'descuento': 'Descuento (Bs.)',
            'tanda': 'Número de tanda',
            'chofer': 'Chofer asignado',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo sucursales activas
        self.fields['sucursal'].queryset = Sucursales.objects.filter(activo=True)


class DetalleDespachoForm(forms.ModelForm):
    """Formulario para los detalles de despacho"""
    class Meta:
        model = DetalleDespacho
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={
                'class': 'form-select producto-select',
                'required': True
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control cantidad-input',
                'min': '1',
                'value': '1',
                'required': True
            }),
            'precio_unitario': forms.NumberInput(attrs={
                'class': 'form-control precio-input',
                'step': '0.01',
                'min': '0',
                'readonly': True,
                'required': True
            }),
        }
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos
        self.fields['producto'].queryset = Producto.objects.filter(activo=True)
        
        # Si es una instancia existente, calcular el subtotal
        if self.instance and self.instance.pk:
            self.initial['subtotal'] = self.instance.subtotal


# Formset para manejar múltiples detalles
DetalleDespachoFormSet = inlineformset_factory(
    Despacho,
    DetalleDespacho,
    form=DetalleDespachoForm,
    extra=1,  # Número de formularios vacíos adicionales
    can_delete=True,  # Permitir eliminar detalles
    min_num=1,  # Mínimo 1 detalle
    validate_min=True,
)


class DespachoFiltroForm(forms.Form):
    """Formulario para filtros de búsqueda"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número, sucursal, chofer...'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Despacho.ESTADOS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    sucursal = forms.ModelChoiceField(
        required=False,
        queryset=Sucursales.objects.filter(activo=True),
        empty_label='Todas las sucursales',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )