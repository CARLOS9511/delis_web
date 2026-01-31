from django.db import models

class Sucursales(models.Model):
    nombre_sucursal = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"
        ordering = ['nombre_sucursal']
    
    def __str__(self):
        return f"{self.nombre_sucursal} - {self.ciudad}"