from django.db import models
from django.conf import settings
from despacho.models import Despacho
from produccion.models import Producto_venta

class Venta(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    despacho = models.ForeignKey(Despacho, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tanda = models.CharField(max_length=20, blank=True, null=True)
    chofer = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Venta {self.numero} - {self.despacho.sucursal}"
    
    def calcular_total(self):
        self.subtotal = sum(d.subtotal for d in self.detalles.all())
        self.total = self.subtotal - self.descuento
        self.save()


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto_venta = models.ForeignKey(Producto_venta, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
    
    def __str__(self):
        return f"{self.producto_venta.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        # CORREGIDO: era self.despacho, debe ser self.venta
        self.venta.calcular_total()