# inventario/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Producto_insumo, Categoria

# ========================================
# VISTAS HTML
# ========================================

def lista_productos(request):
    """Lista todos los productos"""
    productos = Producto_insumo.objects.filter(activo=True).select_related('categoria')
    
    # Filtros
    categoria_id = request.GET.get('categoria')
    buscar = request.GET.get('buscar')
    
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    
    if buscar:
        productos = productos.filter(nombre__icontains=buscar)
    
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'inventario/lista_productos.html', context)


def detalle_producto(request, pk):
    """Muestra detalle de un producto"""
    producto = get_object_or_404(Producto_insumo, pk=pk)
    context = {
        'producto': producto
    }
    return render(request, 'inventario/detalle_producto.html', context)


def lista_categorias(request):
    """Lista todas las categorías"""
    categorias = Categoria.objects.filter(activo=True)
    
    # Contar productos por categoría
    for categoria in categorias:
        categoria.total_productos = categoria.producto_set.filter(activo=True).count()
    
    context = {
        'categorias': categorias
    }
    return render(request, 'inventario/lista_categorias.html', context)


# ========================================
# APIs JSON
# ========================================

def api_productos(request):
    """API: Lista de productos en JSON"""
    productos = Producto_insumo.objects.filter(activo=True).values(
        'id', 
        'codigo', 
        'nombre', 
        'descripcion',
        'precio_compra',
        'precio_venta', 
        'stock',
        'stock_minimo',
        'categoria__nombre'
    )
    
    return JsonResponse(list(productos), safe=False)


def api_producto_detalle(request, pk):
    """API: Detalle de un producto"""
    try:
        producto = Producto_insumo.objects.get(pk=pk, activo=True)
        
        data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': {
                'id': producto.categoria.id if producto.categoria else None,
                'nombre': producto.categoria.nombre if producto.categoria else None,
            },
            'precio_compra': float(producto.precio_compra),
            'precio_venta': float(producto.precio_venta),
            'stock': producto.stock,
            'stock_minimo': producto.stock_minimo,
            'tiene_stock': producto.tiene_stock,
            'stock_bajo': producto.stock_bajo,
            'activo': producto.activo,
        }
        
        return JsonResponse(data)
        
    except Producto_insumo.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)