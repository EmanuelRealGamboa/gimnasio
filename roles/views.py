from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Rol
from rest_framework import serializers


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']


class RolListView(APIView):
    """
    Endpoint para listar todos los roles disponibles.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
