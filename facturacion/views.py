from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFromToRangeFilter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

from .models import Factura, DetalleFactura, Pago
from .serializers import FacturaSerializer, DetalleFacturaSerializer, PagoSerializer
from .permissions import EsAdministradorOCajero


# ====================================================
# 🔹 FILTRO DE FACTURAS (por fecha, estado o cliente)
# ====================================================
class FacturaFilter(FilterSet):
    fecha_emision = DateFromToRangeFilter()

    class Meta:
        model = Factura
        fields = ['fecha_emision', 'estado_pago', 'cliente']


# ====================================================
# 🔹 FACTURA VIEWSET
# ====================================================
class FacturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar facturas.
    Solo accesible por Administrador y Cajero.
    """
    queryset = Factura.objects.all().order_by('-fecha_emision')
    serializer_class = FacturaSerializer
    permission_classes = [EsAdministradorOCajero]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = FacturaFilter
    search_fields = ['cliente__persona__nombre', 'cliente__persona__apellido_paterno']

    # ✅ Generar factura en PDF (visible sin token)
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def generar_pdf(self, request, pk=None):
        factura = self.get_object()

        # Crear buffer para el PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # ===========================
        # 🔹 ENCABEZADO DEL DOCUMENTO
        # ===========================
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, 780, "FACTURA DE COMPRA")

        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Número de Factura: {factura.factura_id}")

        # Mostrar nombre del cliente desde Persona
        if factura.cliente and factura.cliente.persona:
            nombre = factura.cliente.persona.nombre
            apellido = factura.cliente.persona.apellido_paterno
            p.drawString(100, 730, f"Cliente: {nombre} {apellido}")
        else:
            p.drawString(100, 730, "Cliente: No especificado")

        p.drawString(100, 710, f"Fecha de Emisión: {factura.fecha_emision}")
        p.drawString(100, 690, f"Estado de Pago: {factura.estado_pago}")

        # ===========================
        # 🔹 DETALLES DE PRODUCTOS
        # ===========================
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 660, "Detalles de productos:")
        p.setFont("Helvetica", 11)
        y = 640

        for detalle in factura.detalles.all():
            total_linea = detalle.precio_unitario * detalle.cantidad
            producto = detalle.producto.nombre if detalle.producto else "Producto eliminado"
            p.drawString(100, y, f"{producto} x {detalle.cantidad} = ${total_linea}")
            y -= 20
            if y < 80:  # Nueva página si se llena
                p.showPage()
                y = 750

        # ===========================
        # 🔹 TOTAL Y PIE DE PÁGINA
        # ===========================
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y - 10, f"Total de la factura: ${factura.total}")
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(100, y - 40, "Gracias por su compra.")
        p.showPage()
        p.save()

        # Retornar PDF en navegador
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename=\"factura.pdf\"'
        return response


# ====================================================
# 🔹 DETALLE FACTURA VIEWSET
# ====================================================
class DetalleFacturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar detalles de facturas.
    Solo accesible por Administrador y Cajero.
    """
    queryset = DetalleFactura.objects.all().order_by('-factura__fecha_emision')
    serializer_class = DetalleFacturaSerializer
    permission_classes = [EsAdministradorOCajero]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['factura', 'producto']
    search_fields = [
        'factura__cliente__persona__nombre',
        'factura__cliente__persona__apellido_paterno',
        'producto__nombre'
    ]


# ====================================================
# 🔹 PAGO VIEWSET
# ====================================================
class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pagos.
    Solo accesible por Administrador y Cajero.
    """
    queryset = Pago.objects.all().order_by('-fecha_pago')
    serializer_class = PagoSerializer
    permission_classes = [EsAdministradorOCajero]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['metodo_pago', 'fecha_pago', 'factura']
    search_fields = ['factura__cliente__persona__nombre', 'factura__cliente__persona__apellido_paterno']
