from django.db import models
from django.conf import settings
from sucursales.models import Sucursales
from produccion.models import Producto

#from django.utils import timezone
from django.utils.timezone import localtime

class Despacho(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]
    
    numero = models.CharField(max_length=50, unique=True)
    sucursal = models.ForeignKey(Sucursales, on_delete=models.PROTECT)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tanda = models.CharField(max_length=20,blank=True,null=True)
    chofer = models.CharField(max_length=20,blank=True,null=True)
    
    class Meta:
        verbose_name = "Despacho"
        verbose_name_plural = "Despachos"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Despacho {self.numero} - {self.sucursal.nombre_sucursal}"
    
    # ✅ AGREGAR ESTE MÉTODO
    def save(self, *args, **kwargs):
        """Auto-genera el número de despacho si no existe"""
        if not self.numero:
            # Fecha actual en formato YYYYMMDD
            fecha_hoy = localtime().strftime("%y%m%d")
            
            ultimo = Despacho.objects.order_by('-id').first()
            if ultimo and ultimo.id:
                nuevo_num = ultimo.id + 1
            else:
                nuevo_num = 1
            self.numero = f"{fecha_hoy}-T{nuevo_num:02d}"
        
        super().save(*args, **kwargs)
    
    def calcular_total(self):
        self.subtotal = sum(d.subtotal for d in self.detalles.all())
        self.total = self.subtotal - self.descuento
        self.save()


class DetalleDespacho(models.Model):
    despacho = models.ForeignKey(Despacho, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Detalle de Despacho"
        verbose_name_plural = "Detalles de Despacho"
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)
        #self.despacho.calcular_total()

class Pedidos(models.Model):
    sucursal = models.ForeignKey(Sucursales, on_delete=models.PROTECT)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['sucursal']
    
    def __str__(self):
        return f"{self.sucursal} - {self.producto}"


##  areglar saldo hoy y saldo ayer

class Saldos(models.Model):
    # Lista de productos para saldos como tuplas (valor, etiqueta)
    PRODUCTOS_SALDOS = [
        ('Blanca 20p', 'Blanca 20p'),
        ('Blanca 10p', 'Blanca 10p'),
        ('Jaleada 20p', 'Jaleada 20p'),
        ('Jaleada 10p', 'Jaleada 10p'),
        ('Moca 20p', 'Moca 20p'),
        ('Moca 10p', 'Moca 10p'),
        ('Selva Negra20p', 'Selva Negra20p'),
        ('Selva Negra 10p', 'Selva Negra 10p'),
        ('Tres Leches 20p', 'Tres Leches 20p'),
        ('Tres Leches 10p', 'Tres Leches 10p'),
        ('Maracuya 20p', 'Maracuya 20p'),
        ('Maracuya 10p', 'Maracuya 10p'),
        ('Chocomoca 20p', 'Chocomoca 20p'),
        ('Chocomoca 10p', 'Chocomoca 10p'),
        ('Chocodelis 20p', 'Chocodelis 20p'),
        ('Chocodelis 10p', 'Chocodelis 10p'),
        ('Porcion de Frutas', 'Porcion de Frutas'),
        ('Porcion Moca', 'Porcion Moca'),
        ('Porcion Selva Negra', 'Porcion Selva Negra'),
        ('Porcion 3 Leches', 'Porcion 3 Leches'),
        ('Porcion Maracuya', 'Porcion Maracuya'),
        ('Porcion chocomooka', 'Porcion chocomooka'),
        ('Porcion Chocodelis', 'Porcion Chocodelis'),
        ('Alfafor', 'Alfafor'),
        ('Copas', 'Copas'),
        ('Chesecake vaso', 'Chesecake vaso'),
        ('Mouse Copa', 'Mouse Copa'),
        ('Mouse entero', 'Mouse entero'),
        ('Mil hojas', 'Mil hojas'),
        ('Brownie Chocolate', 'Brownie Chocolate'),
        ('Brownie  Quinua', 'Brownie  Quinua'),
        ('Brownie Maracuya', 'Brownie Maracuya'),
        ('Bomba', 'Bomba'),
        ('Brazo Gitano', 'Brazo Gitano'),
        ('Pie de manzana porc.', 'Pie de manzana porc.'),
        ('Pie de limon  porc.', 'Pie de limon  porc.'),
        ('Pie de piña porc.', 'Pie de piña porc.'),
        ('Pie de frutas porc.', 'Pie de frutas porc.'),
        ('Pie de manzana ent.', 'Pie de manzana ent.'),
        ('Pie de limon ent.', 'Pie de limon ent.'),
        ('Pie de piña  ent.', 'Pie de piña  ent.'),
        ('Pie de frutas ent.', 'Pie de frutas ent.'),
        ('Conitos', 'Conitos'),
        ('Cupcakes', 'Cupcakes'),
        ('Queque ', 'Queque '),
        ('Muffy', 'Muffy'),
        ('Mini bomba', 'Mini bomba'),
        ('Rollo', 'Rollo'),
        ('Empanadas', 'Empanadas'),
        ('Croisant', 'Croisant'),
        ('Pan Pizza', 'Pan Pizza'),
        ('Blanca de 30p', 'Blanca de 30p'),
    ]
    
    sucursal = models.ForeignKey(Sucursales, on_delete=models.PROTECT)
    producto = models.CharField(max_length=50, choices=PRODUCTOS_SALDOS)
    saldo_hoy = models.IntegerField()
    saldo_ayer = models.IntegerField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Saldo"
        verbose_name_plural = "Saldos"
        ordering = ['sucursal', 'producto']
    
    def __str__(self):
        return f"{self.sucursal} - {self.producto}"
    
    @classmethod
    def obtener_lista_productos(cls):
        """Retorna la lista de productos como lista simple"""
        return [producto[0] for producto in cls.PRODUCTOS_SALDOS]