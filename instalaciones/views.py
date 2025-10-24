from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Sede, Espacio
from .serializers import SedeSerializer, EspacioSerializer


class SedeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las sedes del gimnasio.
    Permite crear, leer, actualizar y eliminar sedes.
    """
    queryset = Sede.objects.all()
    serializer_class = SedeSerializer
    permission_classes = [IsAuthenticated]


class EspacioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los espacios de las sedes.
    Permite crear, leer, actualizar y eliminar espacios.
    """
    queryset = Espacio.objects.all()
    serializer_class = EspacioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Opcionalmente filtra por sede si se proporciona el parámetro 'sede' en la query.
        """
        queryset = Espacio.objects.all()
        sede_id = self.request.query_params.get('sede', None)
        if sede_id is not None:
            queryset = queryset.filter(sede_id=sede_id)
        return queryset
