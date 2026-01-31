from rest_framework import serializers
from ..models import Saldos

class SaldosSerializer(serializers.ModelSerializer):
    sucursal_nombre = serializers.CharField(source='sucursal.nombre', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = Saldos
        fields = [
            'id',
            'sucursal',
            'sucursal_nombre',
            'producto',
            'saldo_hoy',
            'saldo_ayer',
            'usuario',
            'usuario_username',
            'fecha_creacion',
        ]
