from django import forms
from django.forms import inlineformset_factory
from .models import Venta, DetalleVenta
from despacho.models import Despacho
from produccion.models import Producto_venta


class VentaForm(forms.ModelForm):
    """Formulario para crear/editar ventas"""
    class Meta:
        model = Venta
        fields = ['despacho', 'estado', 'descuento', 'tanda', 'chofer']
        widgets = {
            'despacho': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_despacho'
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
            'despacho': 'Despacho origen',
            'estado': 'Estado de la venta',
            'descuento': 'Descuento (Bs.)',
            'tanda': 'Número de tanda',
            'chofer': 'Chofer asignado',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo despachos completados
        self.fields['despacho'].queryset = Despacho.objects.filter(
            estado='completada'
        ).select_related('sucursal').order_by('-fecha_creacion')
        
        # Personalizar la representación del despacho en el select
        self.fields['despacho'].label_from_instance = lambda obj: f"{obj.numero} - {obj.sucursal.nombre_sucursal}"


class DetalleVentaForm(forms.ModelForm):
    """Formulario para los detalles de venta"""
    class Meta:
        model = DetalleVenta
        fields = ['producto_venta', 'cantidad', 'precio_unitario']
        widgets = {
            'producto_venta': forms.Select(attrs={
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
            'producto_venta': 'Producto',
            'cantidad': 'Cantidad',
            'precio_unitario': 'Precio Unitario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo productos activos
        self.fields['producto_venta'].queryset = Producto_venta.objects.filter(activo=True)
        
        # Si es una instancia existente, calcular el subtotal
        if self.instance and self.instance.pk:
            self.initial['subtotal'] = self.instance.subtotal


# Formset para manejar múltiples detalles
DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    form=DetalleVentaForm,
    extra=1,  # Número de formularios vacíos adicionales
    can_delete=True,  # Permitir eliminar detalles
    min_num=1,  # Mínimo 1 detalle
    validate_min=True,
)


class VentaFiltroForm(forms.Form):
    """Formulario para filtros de búsqueda"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por número, chofer, tanda...'
        })
    )
    
    estado = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Venta.ESTADOS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    despacho = forms.ModelChoiceField(
        required=False,
        queryset=Despacho.objects.filter(estado='completada').select_related('sucursal'),
        empty_label='Todos los despachos',
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