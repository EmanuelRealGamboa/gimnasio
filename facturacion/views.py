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


# -------------------------
# 🔹 Filtro de facturas
# -------------------------
class FacturaFilter(FilterSet):
    fecha_emision = DateFromToRangeFilter()

    class Meta:
        model = Factura
        fields = ['fecha_emision', 'estado_pago', 'cliente_name']  # 👈 actualizado


# -------------------------
# 🔹 FACTURA VIEWSET
# -------------------------
class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all().order_by('-fecha_emision')
    serializer_class = FacturaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = FacturaFilter
    search_fields = ['cliente_name']  # 👈 actualizado

    # ✅ Generar factura en PDF (visible sin token)
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def generar_pdf(self, request, pk=None):
        factura = self.get_object()

        # Crear buffer para el PDF
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(200, 780, "FACTURA DE COMPRA")

        p.setFont("Helvetica", 12)
        p.drawString(100, 750, f"Número de Factura: {factura.factura_id}")
        p.drawString(100, 730, f"Cliente: {factura.cliente_name}")  # 👈 actualizado
        p.drawString(100, 710, f"Fecha de Emisión: {factura.fecha_emision}")
        p.drawString(100, 690, f"Estado de Pago: {factura.estado_pago}")

        # Detalles de la factura
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, 660, "Detalles de productos:")
        p.setFont("Helvetica", 11)
        y = 640
        for detalle in factura.detalles.all():
            total_linea = detalle.precio_unitario * detalle.cantidad
            p.drawString(100, y, f"{detalle.producto} x {detalle.cantidad} = ${total_linea}")
            y -= 20

        # Total
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y - 10, f"Total de la factura: ${factura.total}")

        # Cierre del PDF
        p.showPage()
        p.save()
        buffer.seek(0)

        # ✅ Mostrar PDF en el navegador (no descargar)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="factura.pdf"'
        return response


# -------------------------
# 🔹 DETALLE FACTURA VIEWSET
# -------------------------
class DetalleFacturaViewSet(viewsets.ModelViewSet):
    queryset = DetalleFactura.objects.all()
    serializer_class = DetalleFacturaSerializer


# -------------------------
# 🔹 PAGO VIEWSET (sin informe PDF)
# -------------------------
class PagoViewSet(viewsets.ModelViewSet):
    queryset = Pago.objects.all().order_by('-fecha_pago')
    serializer_class = PagoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['metodo_pago', 'fecha_pago']
    search_fields = ['factura__cliente_name']  # 👈 actualizado
