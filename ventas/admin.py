from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import VentaProducto, DetalleVentaProducto


# -------------------------------
# INLINE DE DETALLE VENTA PRODUCTO
# -------------------------------
class DetalleVentaProductoInline(admin.TabularInline):
    model = DetalleVentaProducto
    extra = 0
    fields = ('producto', 'cantidad', 'precio_unitario', 'descuento', 'subtotal', 'total')
    readonly_fields = ('subtotal', 'total')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        # No permitir agregar detalles manualmente desde admin
        # Las ventas deben crearse desde el endpoint API
        return False


# -------------------------------
# ADMIN DE VENTA PRODUCTO
# -------------------------------
@admin.register(VentaProducto)
class VentaProductoAdmin(admin.ModelAdmin):
    inlines = [DetalleVentaProductoInline]

    list_display = (
        'venta_id',
        'cliente_nombre_display',
        'empleado_display',
        'sede',
        'metodo_pago',
        'subtotal',
        'total',
        'estado',
        'fecha_venta',
        'acciones'
    )

    list_filter = ('estado', 'metodo_pago', 'sede', 'fecha_venta')
    search_fields = (
        'venta_id',
        'cliente__persona__nombre',
        'cliente__persona__apellido_paterno',
        'empleado__email',
        'empleado__first_name',
        'empleado__last_name'
    )

    readonly_fields = (
        'venta_id',
        'subtotal',
        'iva',
        'total',
        'fecha_venta',
        'empleado',
        'estado'
    )

    fieldsets = (
        ('Información de la Venta', {
            'fields': ('venta_id', 'fecha_venta', 'estado')
        }),
        ('Relaciones', {
            'fields': ('cliente', 'empleado', 'sede')
        }),
        ('Detalles de Pago', {
            'fields': ('metodo_pago', 'subtotal', 'descuento_global', 'iva', 'total')
        }),
        ('Notas', {
            'fields': ('notas',),
            'classes': ('collapse',)
        }),
    )

    ordering = ('-fecha_venta',)
    date_hierarchy = 'fecha_venta'

    def cliente_nombre_display(self, obj):
        if obj.cliente and obj.cliente.persona:
            return f"{obj.cliente.persona.nombre} {obj.cliente.persona.apellido_paterno}"
        return "Cliente Anónimo"
    cliente_nombre_display.short_description = "Cliente"

    def empleado_display(self, obj):
        if obj.empleado:
            return obj.empleado.email
        return "—"
    empleado_display.short_description = "Cajero"

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Ver Ticket (PDF)" target="_blank">'
            '<img src="/static/admin/img/icon-yes.svg" alt="Ver Ticket PDF"></a>',
            f'/admin/ventas/ventaproducto/{obj.pk}/ticket/',
        )
    acciones.short_description = "Ticket"

    def has_add_permission(self, request):
        # No permitir crear ventas desde admin
        # Las ventas deben crearse desde el endpoint API
        return False

    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar ventas
        # Usar el endpoint de cancelación en su lugar
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:venta_id>/ticket/',
                self.admin_site.admin_view(self.ver_ticket_pdf),
                name='ventaproducto_ver_ticket',
            ),
        ]
        return custom_urls + urls

    def ver_ticket_pdf(self, request, venta_id):
        """Genera un ticket PDF para la venta"""
        venta = VentaProducto.objects.get(pk=venta_id)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Ticket Venta #{venta.venta_id}")

        # Encabezado
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, "GYM SYSTEM - Ticket de Venta")

        # Información general
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 710, f"Ticket #: {venta.venta_id}")

        cliente_str = "Cliente Anónimo"
        if venta.cliente and venta.cliente.persona:
            cliente_str = f"{venta.cliente.persona.nombre} {venta.cliente.persona.apellido_paterno}"
        pdf.drawString(50, 690, f"Cliente: {cliente_str}")

        if venta.empleado:
            pdf.drawString(50, 670, f"Cajero: {venta.empleado.email}")

        pdf.drawString(50, 650, f"Sede: {venta.sede.nombre}")
        pdf.drawString(50, 630, f"Fecha: {venta.fecha_venta.strftime('%d/%m/%Y %H:%M:%S')}")
        pdf.drawString(50, 610, f"Método de Pago: {venta.get_metodo_pago_display()}")

        # Detalles de productos
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, 580, "Productos:")
        pdf.setFont("Helvetica", 11)

        y = 560
        if venta.detalles.exists():
            for detalle in venta.detalles.all():
                producto_info = f"- {detalle.producto.nombre} x{detalle.cantidad}  @${detalle.precio_unitario}"
                pdf.drawString(60, y, producto_info)
                y -= 15

                if detalle.descuento > 0:
                    pdf.drawString(80, y, f"Descuento: -${detalle.descuento}")
                    y -= 15

                pdf.drawString(80, y, f"Subtotal: ${detalle.total}")
                y -= 20
        else:
            pdf.drawString(60, y, "Sin productos asociados.")
            y -= 20

        # Totales
        y -= 10
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, y, f"Subtotal: ${venta.subtotal}")
        y -= 20

        if venta.descuento_global > 0:
            pdf.drawString(50, y, f"Descuento Global: -${venta.descuento_global}")
            y -= 20

        pdf.drawString(50, y, f"IVA (16%): ${venta.iva}")
        y -= 20

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, f"TOTAL: ${venta.total}")

        # Footer
        pdf.setFont("Helvetica", 10)
        pdf.drawString(200, 50, "¡Gracias por su compra!")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)

        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_venta_{venta.venta_id}.pdf"'
        return response


