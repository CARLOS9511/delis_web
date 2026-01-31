from django.db import models
from sucursales.models import Sucursales
from django.utils import timezone

class Categoria(models.Model):
    CATEGORIA = [
        ('Tortas', 'Tortas'),
        ('Pasteles', 'Pasteles'),
        ('Contratos', 'Contratos'),
    ]
    nombre = models.CharField(max_length=20, choices=CATEGORIA, default='Tortas')
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre



class Producto(models.Model):
    # Diccionario con precios predefinidos por producto
    PRECIOS_PRODUCTOS = {
        '01Blanca 20p': {'compra': 140.00, 'venta':  140.00},
        '02Blanca 10p': {'compra': 100.00, 'venta':  100.00},
        '03Jaleada 20p': {'compra': 150.00, 'venta':  150.00},
        '04Jaleada 10p': {'compra': 105.00, 'venta':  105.00},
        '05Moca 20p': {'compra': 150.00, 'venta':  150.00},
        '06Moca 10p': {'compra': 105.00, 'venta':  105.00},
        '07Selva Negra20p': {'compra': 170.00, 'venta':  170.00},
        '08Selva Negra 10p': {'compra': 120.00, 'venta':  120.00},
        '09Tres Leches 20p': {'compra': 170.00, 'venta':  170.00},
        '10Tres Leches 10p': {'compra': 120.00, 'venta':  120.00},
        '11Maracuya 20p': {'compra': 170.00, 'venta':  170.00},
        '12Maracuya 10p': {'compra': 120.00, 'venta':  120.00},
        '13Chocomoca 20p': {'compra': 170.00, 'venta':  170.00},
        '14Chocomoca 10p': {'compra': 120.00, 'venta':  120.00},
        '15Chocodelis 20p': {'compra': 170.00, 'venta':  170.00},
        '16Chocodelis 10p': {'compra': 120.00, 'venta':  120.00},
        '17Porcion de Frutas': {'compra': 12.00, 'venta':  12.00},
        '18Porcion Moca': {'compra': 13.00, 'venta':  13.00},
        '19Porcion Selva Negra': {'compra': 14.00, 'venta':  14.00},
        '20Porcion 3 Leches': {'compra': 14.00, 'venta':  14.00},
        '21Porcion Maracuya': {'compra': 12.00, 'venta':  12.00},
        '22Porcion chocomooka': {'compra': 14.00, 'venta':  14.00},
        '23Porcion Chocodelis': {'compra': 14.00, 'venta':  14.00},
        '24Alfafor': {'compra': 7.00, 'venta':  7.00},
        '25Copas': {'compra': 15.00, 'venta':  15.00},
        '26Chesecake vaso': {'compra': 8.00, 'venta':  8.00},
        '27Mouse Copa': {'compra': 8.00, 'venta':  8.00},
        '28Mouse entero': {'compra': 50.00, 'venta':  50.00},
        '29Mil hojas': {'compra': 8.00, 'venta':  8.00},
        '30Brownie Chocolate': {'compra': 8.00, 'venta':  8.00},
        '31Aspic': {'compra': 85.00, 'venta':  85.00},
        '32Brownie Maracuya': {'compra': 8.00, 'venta':  8.00},
        '33Bomba': {'compra': 7.00, 'venta':  7.00},
        '34Brazo Gitano': {'compra': 45.00, 'venta':  45.00},
        '35Pie de manzana porc.': {'compra': 9.00, 'venta':  9.00},
        '36Pie de limon  porc.': {'compra': 9.00, 'venta':  9.00},
        '37Pie de piña porc.': {'compra': 9.00, 'venta':  9.00},
        '38Pie de frutas porc.': {'compra': 9.00, 'venta':  9.00},
        '39Pie de manzana ent.': {'compra': 55.00, 'venta':  55.00},
        '40Pie de limon ent.': {'compra': 55.00, 'venta':  55.00},
        '41Pie de piña  ent.': {'compra': 55.00, 'venta':  55.00},
        '42Pie de frutas ent.': {'compra': 55.00, 'venta':  55.00},
        '43Conitos': {'compra': 8.00, 'venta':  8.00},
        '44Cupcakes': {'compra': 7.00, 'venta':  7.00},
        '45Queque ': {'compra': 20.00, 'venta':  20.00},
        '46Muffy': {'compra': 7.00, 'venta':  7.00},
        '47Mini bomba': {'compra': 5.00, 'venta':  5.00},
        '48Rollo': {'compra': 20.00, 'venta':  20.00},
        '49Empanadas': {'compra': 5.00, 'venta':  5.00},
        '50Croisant': {'compra': 8.00, 'venta':  8.00},
        '51Pan Pizza': {'compra': 8.00, 'venta':  8.00},
        '52Blanca de 30p': {'compra': 240.00, 'venta':  240.00},

    }
    
    NOMBRE = [
        ('01Blanca 20p', '01Blanca 20p'),
        ('02Blanca 10p', '02Blanca 10p'),
        ('03Jaleada 20p', '03Jaleada 20p'),
        ('04Jaleada 10p', '04Jaleada 10p'),
        ('05Moca 20p', '05Moca 20p'),
        ('06Moca 10p', '06Moca 10p'),
        ('07Selva Negra20p', '07Selva Negra20p'),
        ('08Selva Negra 10p', '08Selva Negra 10p'),
        ('09Tres Leches 20p', '09Tres Leches 20p'),
        ('10Tres Leches 10p', '10Tres Leches 10p'),
        ('11Maracuya 20p', '11Maracuya 20p'),
        ('12Maracuya 10p', '12Maracuya 10p'),
        ('13Chocomoca 20p', '13Chocomoca 20p'),
        ('14Chocomoca 10p', '14Chocomoca 10p'),
        ('15Chocodelis 20p', '15Chocodelis 20p'),
        ('16Chocodelis 10p', '16Chocodelis 10p'),
        ('17Porcion de Frutas', '17Porcion de Frutas'),
        ('18Porcion Moca', '18Porcion Moca'),
        ('19Porcion Selva Negra', '19Porcion Selva Negra'),
        ('20Porcion 3 Leches', '20Porcion 3 Leches'),
        ('21Porcion Maracuya', '21Porcion Maracuya'),
        ('22Porcion chocomooka', '22Porcion chocomooka'),
        ('23Porcion Chocodelis', '23Porcion Chocodelis'),
        ('24Alfafor', '24Alfafor'),
        ('25Copas', '25Copas'),
        ('26Chesecake vaso', '26Chesecake vaso'),
        ('27Mouse Copa', '27Mouse Copa'),
        ('28Mouse entero', '28Mouse entero'),
        ('29Mil hojas', '29Mil hojas'),
        ('30Brownie Chocolate', '30Brownie Chocolate'),
        ('31Aspic', '31Aspic'),
        ('32Brownie Maracuya', '32Brownie Maracuya'),
        ('33Bomba', '33Bomba'),
        ('34Brazo Gitano', '34Brazo Gitano'),
        ('35Pie de manzana porc.', '35Pie de manzana porc.'),
        ('36Pie de limon  porc.', '36Pie de limon  porc.'),
        ('37Pie de piña porc.', '37Pie de piña porc.'),
        ('38Pie de frutas porc.', '38Pie de frutas porc.'),
        ('39Pie de manzana ent.', '39Pie de manzana ent.'),
        ('40Pie de limon ent.', '40Pie de limon ent.'),
        ('41Pie de piña  ent.', '41Pie de piña  ent.'),
        ('42Pie de frutas ent.', '42Pie de frutas ent.'),
        ('43Conitos', '43Conitos'),
        ('44Cupcakes', '44Cupcakes'),
        ('45Queque ', '45Queque '),
        ('46Muffy', '46Muffy'),
        ('47Mini bomba', '47Mini bomba'),
        ('48Rollo', '48Rollo'),
        ('49Empanadas', '49Empanadas'),
        ('50Croisant', '50Croisant'),
        ('51Pan Pizza', '51Pan Pizza'),
        ('52Blanca de 30p', '52Blanca de 30p'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200, choices=NOMBRE, default='01Blanca 20p')
    codigo_producto = models.IntegerField(default=1)
    categoria = models.ForeignKey('Categoria', on_delete=models.PROTECT)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(
        default=timezone.now,
        editable=False
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def save(self, *args, **kwargs):
        """
        Sobrescribir el método save para asignar precios automáticamente
        basándose en el producto seleccionado
        """
        # Si el producto existe en el diccionario, asignar precios automáticamente
        if self.nombre in self.PRECIOS_PRODUCTOS:
            precios = self.PRECIOS_PRODUCTOS[self.nombre]
            # Asignar precios solo si están en 0 o si es un producto nuevo
            if self.precio_compra == 0 or not self.pk:
                self.precio_compra = precios['compra']
            if self.precio_venta == 0 or not self.pk:
                self.precio_venta = precios['venta']
        
        super().save(*args, **kwargs)
    
    @property
    def tiene_stock(self):
        return self.stock > 0
    
    @property
    def stock_bajo(self):
        return 0 < self.stock <= self.stock_minimo
    
    @property
    def margen(self):
        """Calcula el margen de ganancia en porcentaje"""
        if self.precio_compra > 0:
            margen = ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
            return round(margen, 2)
        return 0
    
    @property
    def ganancia(self):
        """Calcula la ganancia en monto"""
        return self.precio_venta - self.precio_compra
    
    @property
    def valor_total_stock(self):
        """Calcula el valor total del stock"""
        return self.stock * self.precio_venta
#Producto para la venta

class Producto_venta(models.Model):
    sucursal_venta = models.ForeignKey(Sucursales, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    codigo_producto = models.IntegerField(default=1)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Producto venta"
        verbose_name_plural = "Productos ventas"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def tiene_stock(self):
        return self.stock > 0
    
    @property
    def stock_bajo(self):
        return 0 < self.stock <= self.stock_minimo