from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from despacho.models import Saldos
from despacho.api.serializers import SaldosSerializer

class SaldosViewSet(viewsets.ModelViewSet):
    queryset = Saldos.objects.all()
    serializer_class = SaldosSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def todos(self, request):
        """Endpoint para obtener TODOS los datos registrados de saldos"""
        try:
            # Obtener todos los saldos con relaciones
            saldos = Saldos.objects.select_related('sucursal', 'usuario').all()
            
            # Serializar los datos
            serializer = SaldosSerializer(saldos, many=True)
            
            # Estadísticas adicionales
            stats = {
                'total_registros': saldos.count(),
                'total_saldo_hoy': saldos.aggregate(total=Sum('saldo_hoy'))['total'] or 0,
                'total_saldo_ayer': saldos.aggregate(total=Sum('saldo_ayer'))['total'] or 0,
                'sucursales_unicas': saldos.values('sucursal__nombre').distinct().count(),
                'productos_unicos': saldos.values('producto').distinct().count()
            }
            
            return Response({
                'success': True,
                'message': f'Se encontraron {stats["total_registros"]} registros de saldos',
                'data': serializer.data,
                'estadisticas': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error al obtener los datos: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def por_sucursal(self, request):
        """Endpoint para obtener saldos agrupados por sucursal"""
        try:
            sucursal_id = request.query_params.get('sucursal_id')
            
            queryset = Saldos.objects.select_related('sucursal', 'usuario')
            
            if sucursal_id:
                queryset = queryset.filter(sucursal_id=sucursal_id)
            
            serializer = SaldosSerializer(queryset, many=True)
            
            return Response({
                'success': True,
                'data': serializer.data,
                'total_registros': queryset.count()
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error: {str(e)}',
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Endpoint para obtener un resumen de saldos"""
        try:
            # Resumen por producto
            resumen_productos = Saldos.objects.values('producto').annotate(
                total_hoy=Sum('saldo_hoy'),
                total_ayer=Sum('saldo_ayer'),
                cantidad_registros=Count('id')
            ).order_by('-total_hoy')
            
            # Resumen por sucursal
            resumen_sucursales = Saldos.objects.values('sucursal__nombre').annotate(
                total_hoy=Sum('saldo_hoy'),
                total_ayer=Sum('saldo_ayer'),
                cantidad_registros=Count('id')
            ).order_by('-total_hoy')
            
            return Response({
                'success': True,
                'resumen_productos': list(resumen_productos),
                'resumen_sucursales': list(resumen_sucursales),
                'total_general': {
                    'saldo_hoy_total': Saldos.objects.aggregate(total=Sum('saldo_hoy'))['total'] or 0,
                    'saldo_ayer_total': Saldos.objects.aggregate(total=Sum('saldo_ayer'))['total'] or 0,
                    'registros_total': Saldos.objects.count()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error en el resumen: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)