from django.contrib import admin
from .models import Despacho, DetalleDespacho,Pedidos,Saldos

# --- Inline para DetalleDespacho ---
class DetalleDespachoInline(admin.TabularInline):
    model = DetalleDespacho
    extra = 1  # cuántas filas vacías se muestran por defecto
    readonly_fields = ('subtotal',)
    #autocomplete_fields = ('producto',)  # mejora la búsqueda de productos

# --- Admin principal para Despacho ---
@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'sucursal', 'usuario', 'estado', 'total', 'fecha_creacion', 'tanda', 'chofer')
    list_filter = ('estado', 'sucursal', 'fecha_creacion')
    search_fields = ('numero', 'sucursal__nombre_sucursal', 'usuario__username', 'tanda', 'chofer')
    readonly_fields = ('fecha_creacion', 'subtotal', 'total')
    ordering = ('-fecha_creacion',)
    inlines = [DetalleDespachoInline]
    list_per_page = 20

    fieldsets = (
        ('Información General', {
            'fields': ('numero', 'sucursal', 'usuario', 'estado', 'tanda', 'chofer')
        }),
        ('Totales', {
            'fields': ('subtotal', 'descuento', 'total')
        }),
        ('Control', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',),
        }),
    )

# --- Admin para DetalleDespacho (opcional, si quieres verlo también separado) ---
@admin.register(DetalleDespacho)
class DetalleDespachoAdmin(admin.ModelAdmin):
    list_display = ('despacho', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    search_fields = ('despacho__numero', 'producto__nombre')
    list_filter = ('despacho__estado', 'producto')
    readonly_fields = ('subtotal',)
    ordering = ('despacho',)

##---- Pedidos y saldos
@admin.register(Pedidos)
class PedidosAdmin(admin.ModelAdmin):
    list_display = ('sucursal', 'producto', 'cantidad', 'usuario', 'fecha_creacion')
    list_filter = ('sucursal', 'producto')
    search_fields = ('sucursal', 'producto', 'cantidad')
    ordering = ('sucursal',)
    readonly_fields = ('fecha_creacion',)
    list_per_page = 20

    
@admin.register(Saldos)
class SaldosAdmin(admin.ModelAdmin):
    list_display = ('sucursal', 'producto', 'saldo_hoy', 'saldo_ayer', 'usuario', 'fecha_creacion')
    list_filter = ('sucursal', 'producto')
    search_fields = ('sucursal', 'producto')
    ordering = ('sucursal',)
    readonly_fields = ('fecha_creacion',)
    list_per_page = 20

