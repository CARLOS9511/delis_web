# reportes/views.py

from django.shortcuts import render
from django.db.models import Sum, Count
from produccion.models import Producto, Categoria
from sucursales.models import Sucursales
from despacho.models import Despacho, DetalleDespacho  # O venta.models si tu app se llama 'venta'

def dashboard(request):
    """Dashboard principal con estadísticas"""
    
    # Estadísticas generales
    total_productos = Producto.objects.count()
    total_sucursales = Sucursales.objects.count()
    total_despachos = Despacho.objects.count()
    
    # Stock
    stock_total = Producto.objects.aggregate(total=Sum('stock'))['total'] or 0
    productos_sin_stock = Producto.objects.filter(stock=0).count()
    productos_stock_bajo = Producto.objects.filter(stock__lt=10, stock__gt=0)
    
    # Estado de Despachos
    despachos_completadas = Despacho.objects.filter(estado='completada').count()
    despachos_pendientes = Despacho.objects.filter(estado='pendiente').count()
    despachos_canceladas = Despacho.objects.filter(estado='cancelada').count()
    
    # Total despachado
    total_despachado = Despacho.objects.filter(
        estado='completada'
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Últimos despachos
    despachos_recientes = Despacho.objects.all().select_related('sucursal').order_by('-fecha_creacion')[:10]
    
    # Productos más enviados
    productos_mas_despachados = DetalleDespacho.objects.values(
        'producto__nombre'
    ).annotate(
        total_despachado=Sum('cantidad')
    ).order_by('-total_despachado')[:5]
    
    context = {
        'total_productos': total_productos,
        'total_sucursales': total_sucursales,
        'total_despachos': total_despachos,
        'stock_total': stock_total,
        'productos_sin_stock': productos_sin_stock,
        'productos_stock_bajo': productos_stock_bajo,
        'despachos_completadas': despachos_completadas,
        'despachos_pendientes': despachos_pendientes,
        'despachos_canceladas': despachos_canceladas,
        'total_despachado': total_despachado,
        'despachos_recientes': despachos_recientes,
        'productos_mas_despachados': productos_mas_despachados,
    }
    
    return render(request, 'reportes/dashboard.html', context)

def reporte_despachos(request):
    """Reporte de despachos"""
    despachos = Despacho.objects.all().order_by('-fecha_creacion')
    
    context = {
        'despachos': despachos
    }
    return render(request, 'reportes/reporte_despachos.html', context)


def reporte_ventas(request):
    """Reporte de ventas"""
    ventas = Despacho.objects.all().order_by('-fecha_creacion')
    
    context = {
        'ventas': ventas
    }
    return render(request, 'reportes/reporte_ventas.html', context)


def reporte_inventario(request):
    """Reporte de inventario"""
    productos = Producto.objects.all().select_related('categoria')
    
    context = {
        'productos': productos
    }
    return render(request, 'reportes/reporte_inventario.html', context)