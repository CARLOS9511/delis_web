# produccion/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Producto, Categoria
from datetime import datetime,time
from django.utils import timezone
from datetime import timedelta
# ==================== LISTA DE PRODUCTOS ====================

@login_required
def lista_productos(request):
    """Vista para listar productos creados HOY con filtros"""
    hoy = timezone.localdate()
    inicio = timezone.make_aware(datetime.combine(hoy, time.min))
    fin = timezone.make_aware(datetime.combine(hoy, time.max))
    productos = Producto.objects.filter(
        fecha_creacion__range=(inicio, fin)
    )
    # Filtro de búsqueda
    buscar = request.GET.get('buscar', '')
    if buscar:
        productos = productos.filter(
            Q(codigo__icontains=buscar) | 
            Q(nombre__icontains=buscar)
        )

    # Filtro de categoría
    categoria_id = request.GET.get('categoria', '')
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    # Filtro de estado
    estado = request.GET.get('estado', '')
    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    elif estado == 'stock_bajo':
        productos = [p for p in productos if p.stock_bajo]
    elif estado == 'sin_stock':
        productos = productos.filter(stock=0)

    # Ordenamiento
    orden = request.GET.get('orden', 'nombre')
    if orden == 'nombre':
        productos = productos.order_by('nombre')
    elif orden == 'precio_compra':
        productos = productos.order_by('precio_compra')
    elif orden == 'precio_venta':
        productos = productos.order_by('precio_venta')

    # Estadísticas (TODOS los productos, no solo hoy)
    todos_productos = Producto.objects.all()
    total_productos = todos_productos.count()
    productos_activos = todos_productos.filter(activo=True).count()
    stock_total = sum(p.stock for p in todos_productos)
    productos_stock_bajo = sum(1 for p in todos_productos if p.stock_bajo)

    categorias = Categoria.objects.filter(activo=True)

    context = {
        'productos': productos,
        'categorias': categorias,
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'stock_total': stock_total,
        'productos_stock_bajo': productos_stock_bajo,
    }

    return render(request, 'produccion/lista_productos.html', context)

# ==================== DETALLE PRODUCTO ====================
@login_required
def detalle_producto(request, pk):
    """Ver detalle de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    context = {
        'producto': producto,
    }
    
    return render(request, 'produccion/detalle_productos.html', context)


# ==================== CREAR PRODUCTO ====================
@login_required
def crear_producto(request):
    """Vista para crear un nuevo producto"""
    categorias = Categoria.objects.filter(activo=True)
    nombres_productos = Producto.NOMBRE
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria')
            stock = int(request.POST.get('stock', 0))
            stock_minimo = int(request.POST.get('stock_minimo', 5))
            
            # Generar código automáticamente
            now = datetime.now()
            dia = now.strftime('%d')
            mes = now.strftime('%m')
            anio = now.strftime('%Y')
            nombre_corto = nombre.replace(' ', '')[:10]  # Primeros 10 caracteres sin espacios
            codigo = f"P{dia}{mes}{anio}-{nombre_corto}"
            
            # Generar codigo_producto (día de la semana: 1=Lunes, 7=Domingo)
            codigo_producto = now.isoweekday()  # 1=Lunes, 2=Martes, ..., 7=Domingo
            
            # Verificar si el código ya existe (por si acaso)
            contador = 1
            codigo_base = codigo

            codigo = f"{codigo_base}-{codigo_producto}"
            # while Producto.objects.filter(codigo=codigo).exists():
            #     codigo = f"{codigo_base}-{codigo_producto}"
            #     contador += 1
            #messages.error(request, f'❌ Error al crear el producto: {str(e)}')
            if Producto.objects.filter(codigo=codigo).exists():
                messages.error(
                    request,
                    "f'❌ Este producto ya se creó, no se puede duplicar. Seleccione otro producto."
                )


            # Obtener categoría
            categoria = None
            if categoria_id:
                categoria = Categoria.objects.get(id=categoria_id)
            
            # Crear el producto
            producto = Producto.objects.create(
                codigo=codigo,
                nombre=nombre,
                codigo_producto=codigo_producto,
                categoria=categoria,
                stock=stock,
                stock_minimo=stock_minimo
            )
            
            messages.success(request, f'✅ Producto "{producto.nombre}" creado exitosamente con código: {codigo}')
            return redirect('produccion:detalle', pk=producto.id)
            
        except Exception as e:
            messages.error(request, f'❌ Error al crear el producto: {str(e)}')
    
    context = {
        'categorias': categorias,
        'nombres_productos': nombres_productos,
    }
    return render(request, 'produccion/crear_producto.html', context)

# ==================== EDITAR PRODUCTO ====================
@login_required
def editar_producto(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            codigo = request.POST.get('codigo', '').strip()
            nombre = request.POST.get('nombre', '').strip()
            categoria_id = request.POST.get('categoria')
            stock = request.POST.get('stock', 0)
            stock_minimo = request.POST.get('stock_minimo', 5)
            precio_compra = request.POST.get('precio_compra')
            precio_venta = request.POST.get('precio_venta')
            activo = request.POST.get('activo') == 'on'
            
            # Validaciones
            if not codigo or not nombre:
                messages.error(request, '⚠️ El código y nombre son obligatorios')
                return redirect('produccion:editar', pk=pk)
            
            # Verificar código duplicado (excepto el actual)
            if Producto.objects.filter(codigo=codigo).exclude(pk=pk).exists():
                messages.error(request, f'❌ Ya existe otro producto con el código {codigo}')
                return redirect('produccion:editar', pk=pk)
            
            # Actualizar producto
            producto.codigo = codigo
            producto.nombre = nombre
            producto.stock = int(stock)
            producto.stock_minimo = int(stock_minimo)
            producto.activo = activo
            
            # Actualizar categoría
            if categoria_id:
                try:
                    producto.categoria = Categoria.objects.get(id=categoria_id)
                except Categoria.DoesNotExist:
                    messages.error(request, '❌ Categoría no encontrada')
                    return redirect('produccion:editar', pk=pk)
            else:
                producto.categoria = None
            
            # Actualizar precios si fueron modificados
            if precio_compra:
                producto.precio_compra = float(precio_compra)
            if precio_venta:
                producto.precio_venta = float(precio_venta)
            
            producto.save()
            
            messages.success(request, f'✅ Producto "{producto.nombre}" actualizado exitosamente')
            return redirect('produccion:detalle', pk=producto.id)
            
        except Exception as e:
            messages.error(request, f'❌ Error al actualizar producto: {str(e)}')
            return redirect('produccion:editar', pk=pk)
    
    # GET - Mostrar formulario con datos actuales
    categorias = Categoria.objects.filter(activo=True)
    nombres_productos = Producto.NOMBRE
    
    context = {
        'producto': producto,
        'categorias': categorias,
        'nombres_productos': nombres_productos,
    }
    return render(request, 'produccion/editar_producto.html', context)


# ==================== ELIMINAR PRODUCTO ====================
@login_required
def eliminar_producto(request, pk):
    """Vista para eliminar (desactivar) un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            # No eliminamos físicamente, solo desactivamos
            producto.activo = False
            producto.save()
            
            messages.success(request, f'✅ Producto "{producto.nombre}" desactivado exitosamente')
            return redirect('produccion:lista')
            
        except Exception as e:
            messages.error(request, f'❌ Error al eliminar: {str(e)}')
            return redirect('produccion:detalle', pk=pk)
    
    context = {
        'producto': producto
    }
    return render(request, 'produccion/eliminar_producto.html', context)


# ==================== LISTA DE CATEGORÍAS ====================
@login_required
def lista_categorias(request):
    """Lista todas las categorías"""
    categorias = Categoria.objects.filter(activo=True)
    
    # Contar productos por categoría
    for categoria in categorias:
        categoria.total_productos = categoria.producto_set.filter(activo=True).count()
    
    context = {
        'categorias': categorias
    }
    return render(request, 'produccion/lista_categorias.html', context)


# ==================== APIs JSON ====================

@login_required
def api_productos(request):
    """API: Lista de productos en JSON"""
    productos = Producto.objects.filter(activo=True).select_related('categoria').values(
        'id', 
        'codigo', 
        'nombre',
        'precio_compra',
        'precio_venta', 
        'stock',
        'stock_minimo',
        'categoria__nombre',
        'activo'
    )
    
    return JsonResponse(list(productos), safe=False)


@login_required
def api_producto_detalle(request, pk):
    """API: Detalle de un producto"""
    try:
        producto = Producto.objects.get(pk=pk, activo=True)
        
        data = {
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
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
            'margen': producto.margen,
            'ganancia': float(producto.ganancia),
            'activo': producto.activo,
        }
        
        return JsonResponse(data)
        
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)


@login_required
def api_obtener_precio(request, pk):
    """API: Obtener precio de un producto por ID"""
    try:
        producto = Producto.objects.get(pk=pk)
        
        return JsonResponse({
            'success': True,
            'id': producto.id,
            'nombre': producto.nombre,
            'precio_compra': float(producto.precio_compra),
            'precio_venta': float(producto.precio_venta),
            'stock': producto.stock,
        })
        
    except Producto.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Producto no encontrado'
        }, status=404)


@login_required
def api_buscar_productos(request):
    """API: Buscar productos por nombre o código"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'productos': []})
    
    productos = Producto.objects.filter(
        Q(nombre__icontains=query) | Q(codigo__icontains=query),
        activo=True
    ).select_related('categoria')[:10]
    
    resultados = [{
        'id': p.id,
        'codigo': p.codigo,
        'nombre': p.nombre,
        'precio_compra': float(p.precio_compra),
        'precio_venta': float(p.precio_venta),
        'stock': p.stock,
        'categoria': p.categoria.nombre if p.categoria else None,
    } for p in productos]
    
    return JsonResponse({'productos': resultados})


# ==================== ACTIVAR/DESACTIVAR PRODUCTO ====================
@login_required
@require_POST
def toggle_producto(request, pk):
    """Vista para activar/desactivar un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    try:
        producto.activo = not producto.activo
        producto.save()
        
        estado = "activado" if producto.activo else "desactivado"
        messages.success(request, f'✅ Producto "{producto.nombre}" {estado} exitosamente')
        
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    
    return redirect('produccion:detalle', pk=pk)


# ==================== AJUSTAR STOCK ====================
@login_required
def ajustar_stock(request, pk):
    """Vista para ajustar el stock de un producto"""
    producto = get_object_or_404(Producto, pk=pk)
    
    if request.method == 'POST':
        try:
            accion = request.POST.get('accion')  # 'agregar' o 'quitar'
            cantidad = int(request.POST.get('cantidad', 0))
            
            if cantidad <= 0:
                messages.error(request, '⚠️ La cantidad debe ser mayor a 0')
                return redirect('produccion:detalle', pk=pk)
            
            if accion == 'agregar':
                producto.stock += cantidad
                messages.success(
                    request, 
                    f'✅ Se agregaron {cantidad} unidades. Stock actual: {producto.stock}'
                )
            elif accion == 'quitar':
                if producto.stock < cantidad:
                    messages.error(
                        request, 
                        f'❌ Stock insuficiente. Disponible: {producto.stock}, Solicitado: {cantidad}'
                    )
                    return redirect('produccion:detalle', pk=pk)
                
                producto.stock -= cantidad
                messages.success(
                    request, 
                    f'✅ Se quitaron {cantidad} unidades. Stock actual: {producto.stock}'
                )
            else:
                messages.error(request, '❌ Acción no válida')
                return redirect('produccion:detalle', pk=pk)
            
            producto.save()
            return redirect('produccion:detalle', pk=pk)
            
        except ValueError:
            messages.error(request, '❌ Cantidad inválida')
            return redirect('produccion:detalle', pk=pk)
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('produccion:detalle', pk=pk)
    
    context = {
        'producto': producto
    }
    return render(request, 'produccion/ajustar_stock.html', context)
##333333333333excel

def importar_excel_view(request):
    """Vista para mostrar el formulario de importación"""
    return render(request, 'produccion/importar_excel.html')

from django.views.decorators.http import require_http_methods
@require_http_methods(["POST"])
def importar_excel(request):
    """
    Vista para procesar la importación de datos desde Excel
    """
    try:
        # Obtener datos JSON
        data = json.loads(request.body)
        productos_data = data.get('productos', [])
        
        if not productos_data:
            return JsonResponse({
                'success': False,
                'error': 'No se recibieron datos para importar'
            })
        
        created_count = 0
        errors = []
        
        # Procesar cada producto
        for idx, producto_data in enumerate(productos_data, start=1):
            try:
                # Validar datos requeridos
                codigo = producto_data.get('codigo', '').strip()
                nombre = producto_data.get('nombre', '').strip()
                
                if not codigo or not nombre:
                    errors.append(f"Fila {idx}: Código y nombre son requeridos")
                    continue
                
                # Verificar si el código ya existe
                if Producto.objects.filter(codigo=codigo).exists():
                    errors.append(f"Fila {idx}: El código '{codigo}' ya existe")
                    continue
                
                # Verificar si el nombre está en la lista de nombres válidos
                nombres_validos = [n[0] for n in Producto.NOMBRE]
                if nombre not in nombres_validos:
                    errors.append(f"Fila {idx}: El nombre '{nombre}' no es válido")
                    continue
                
                # Obtener categoría
                categoria = None
                categoria_nombre = producto_data.get('categoria', '').strip()
                if categoria_nombre:
                    try:
                        categoria = Categoria.objects.get(nombre=categoria_nombre)
                    except Categoria.DoesNotExist:
                        errors.append(f"Fila {idx}: Categoría '{categoria_nombre}' no existe")
                        continue
                
                # Generar codigo_producto (día de la semana)
                now = datetime.now()
                codigo_producto = now.isoweekday()
                
                # Crear el producto
                producto = Producto.objects.create(
                    codigo=codigo,
                    nombre=nombre,
                    codigo_producto=codigo_producto,
                    categoria=categoria,
                    precio_compra=producto_data.get('precio_compra', 0),
                    precio_venta=producto_data.get('precio_venta', 0),
                    stock=producto_data.get('stock', 0),
                    stock_minimo=producto_data.get('stock_minimo', 5)
                )
                
                created_count += 1
                
            except Exception as e:
                errors.append(f"Fila {idx}: {str(e)}")
                continue
        
        # Preparar respuesta
        if created_count > 0:
            response_data = {
                'success': True,
                'created': created_count,
                'message': f'Se importaron {created_count} productos exitosamente'
            }
            
            if errors:
                response_data['warnings'] = errors
                response_data['message'] += f'. {len(errors)} registros con errores.'
            
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': 'No se pudo importar ningún producto',
                'details': errors
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Error al procesar los datos JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        })


def descargar_plantilla_excel(request):
    """
    Vista para descargar una plantilla de Excel vacía
    """
    import csv
    from django.http import HttpResponse
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="plantilla_productos.csv"'
    
    writer = csv.writer(response, delimiter='\t')
    
    # Escribir encabezados
    writer.writerow(['codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta', 'stock', 'stock_minimo'])
    
    # Escribir ejemplos
    writer.writerow(['PROD001', 'Blanca 20p', 'Tortas', '140.00', '140.00', '10', '5'])
    writer.writerow(['PROD002', 'Moca 10p', 'Tortas', '105.00', '105.00', '15', '5'])
    writer.writerow(['PROD003', 'Selva Negra 20p', 'Tortas', '170.00', '170.00', '8', '5'])
    
    return response