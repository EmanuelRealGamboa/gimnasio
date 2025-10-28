from django.core.exceptions import ValidationError
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.forms.models import BaseInlineFormSet
from .models import Venta, PasarelaPago, DetallePasarela
from inventario.models import Producto


# -------------------------------
# FILTRO DE BÚSQUEDA
# -------------------------------
class BuscadorFilter(admin.SimpleListFilter):
    title = 'Buscar por'
    parameter_name = 'buscador_tipo'

    def lookups(self, request, model_admin):
        return [
            ('nombre', 'Nombre'),
            ('codigo', 'Código'),
        ]

    def queryset(self, request, queryset):
        valor = request.GET.get('q')
        tipo = self.value()
        if valor and tipo == 'nombre':
            return queryset.filter(producto__nombre__icontains=valor)
        elif valor and tipo == 'codigo':
            return queryset.filter(producto__codigo__icontains=valor)
        return queryset


# -------------------------------
# ADMIN DE VENTAS
# -------------------------------
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('venta_id', 'codigo_producto', 'nombre_producto', 'cantidad', 'total', 'estado')
    list_filter = (BuscadorFilter,)
    search_fields = ('producto__nombre', 'producto__codigo')

    def codigo_producto(self, obj):
        try:
            return obj.producto.codigo
        except Exception:
            return "—"
    codigo_producto.short_description = "Código del Producto"

    def nombre_producto(self, obj):
        try:
            return obj.producto.nombre
        except Exception:
            return "—"
    nombre_producto.short_description = "Nombre del Producto"

    def save_model(self, request, obj, form, change):
        # 🔸 Validar cantidad válida
        if not obj.cantidad or obj.cantidad <= 0:
            messages.error(request, "⚠️ Debes ingresar una cantidad válida antes de guardar la venta.")
            return

        # 🔸 Validar producto seleccionado
        if not obj.producto_id:
            messages.error(request, "⚠️ Debes seleccionar un producto antes de guardar la venta.")
            return

        super().save_model(request, obj, form, change)
        obj.estado = "PENDIENTE"
        obj.save(update_fields=['estado'])
        


# -------------------------------
# INLINE FORMSET DE DETALLE PASARELA
# -------------------------------
class DetallePasarelaInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        # ⚠️ Validar que se agregue al menos un producto
        if not any(form.cleaned_data and not form.cleaned_data.get('DELETE', False) for form in self.forms):
            raise ValidationError("⚠️ Debes agregar al menos un producto antes de guardar la pasarela.")


# -------------------------------
# INLINE DE DETALLE DE PASARELA
# -------------------------------
class DetallePasarelaInline(admin.TabularInline):
    model = DetallePasarela
    formset = DetallePasarelaInlineFormSet
    extra = 1
    fields = ('producto',)  # 👈 solo se muestra el producto, ocultamos cantidad y total
    readonly_fields = ()
    can_delete = True

    def get_formset(self, request, obj=None, **kwargs):
        """
        Oculta los campos 'cantidad' y 'total' en el formulario del inline,
        pero permite que se procesen internamente al guardar.
        """
        formset = super().get_formset(request, obj, **kwargs)
        if 'cantidad' in formset.form.base_fields:
            formset.form.base_fields['cantidad'].widget = admin.widgets.AdminHiddenInput()
        if 'total' in formset.form.base_fields:
            formset.form.base_fields['total'].widget = admin.widgets.AdminHiddenInput()
        return formset


# -------------------------------
# ADMIN DE PASARELA DE PAGO
# -------------------------------
@admin.register(PasarelaPago)
class PasarelaPagoAdmin(admin.ModelAdmin):
    inlines = [DetallePasarelaInline]
    list_display = (
        'pasarela_id',
        'metodo_pago',
        'fecha_pago',
        'productos_asociados',
        'total_general',
        'acciones'
    )
    search_fields = ('metodo_pago',)
    ordering = ('-fecha_pago',)
    exclude = ('total_general',)

    def productos_asociados(self, obj):
        productos = [f"{detalle.producto.nombre} (${detalle.total})" for detalle in obj.detalles.all()]
        return ", ".join(productos) if productos else "Sin productos"
    productos_asociados.short_description = "Productos"

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Ver Ticket (PDF)" target="_blank">'
            '<img src="/static/admin/img/icon-yes.svg" alt="Ver Ticket PDF"></a>',
            f'/admin/ventas/pasarelapago/{obj.pk}/ticket/',
        )
    acciones.short_description = "Ver Ticket"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pasarela_id>/ticket/',
                self.admin_site.admin_view(self.ver_ticket_pdf),
                name='pasarela_ver_ticket',
            ),
        ]
        return custom_urls + urls

    def ver_ticket_pdf(self, request, pasarela_id):
        pasarela = PasarelaPago.objects.get(pk=pasarela_id)
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setTitle(f"Ticket Pasarela #{pasarela.pasarela_id}")

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(200, 750, "GYM SYSTEM - Ticket de Pago")

        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 710, f"ID Pasarela: {pasarela.pasarela_id}")
        pdf.drawString(50, 690, f"Método de Pago: {pasarela.metodo_pago}")
        pdf.drawString(50, 670, f"Fecha: {pasarela.fecha_pago.strftime('%d/%m/%Y %H:%M:%S')}")

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(50, 640, "Detalles del Pago:")
        pdf.setFont("Helvetica", 11)
        y = 620
        if pasarela.detalles.exists():
            for detalle in pasarela.detalles.all():
                pdf.drawString(60, y, f"- {detalle.producto.nombre} (x{detalle.cantidad})  ${detalle.total}")
                y -= 20
        else:
            pdf.drawString(60, y, "Sin productos asociados.")
            y -= 20

        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(50, y - 10, f"Total General: ${pasarela.total_general}")

        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_pasarela_{pasarela.pasarela_id}.pdf"'
        return response

    def save_related(self, request, form, formsets, change):
        """
        Guarda los detalles de pasarela y actualiza el total,
        sin volver a restar stock (ya se hace en el modelo DetallePasarela).
        """
        super().save_related(request, form, formsets, change)
        pasarela = form.instance

        # Recalcular total general sin tocar el stock
        total_general = sum(detalle.total for detalle in pasarela.detalles.all())
        pasarela.total_general = total_general
        pasarela.save(update_fields=['total_general'])

        
