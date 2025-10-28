from django.contrib import admin
from django.utils.html import format_html
from .models import Factura, DetalleFactura, Pago


# -------------------------------
# 🔹 FACTURA ADMIN (vista + imprimir PDF)
# -------------------------------
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('factura_id', 'cliente_name', 'fecha_emision', 'total', 'estado_pago', 'acciones')  # 👈 cambiado
    list_filter = ('estado_pago', 'fecha_emision')
    search_fields = ('cliente_name',)  # 👈 cambiado
    ordering = ('-fecha_emision',)

    # === BOTONES DE ACCIÓN ===
    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-changelink.svg" alt="Editar"></a>'
            '<a href="{}" title="Eliminar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-deletelink.svg" alt="Eliminar"></a>'
            '<a href="{}" title="Ver Factura" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-viewlink.svg" alt="Ver Factura"></a>'
            '<a href="{}" title="Imprimir Factura (PDF)" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-yes.svg" alt="Imprimir PDF"></a>',
            f'/admin/facturacion/factura/{obj.pk}/change/',      
            f'/admin/facturacion/factura/{obj.pk}/delete/',
            f'/admin/facturacion/factura/{obj.pk}/change/',
            f'/api/facturacion/facturas/{obj.factura_id}/generar_pdf/',  
        )

    acciones.short_description = "Acciones"
    acciones.allow_tags = True


# -------------------------------
# 🔹 DETALLE FACTURA ADMIN
# -------------------------------
@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('detalle_id', 'factura', 'producto', 'cantidad', 'precio_unitario', 'acciones')
    list_filter = ('producto',)
    search_fields = ('factura__cliente_name',)  # 👈 cambiado
    ordering = ('-factura__fecha_emision',)

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-changelink.svg" alt="Editar"></a>'
            '<a href="{}" title="Eliminar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-deletelink.svg" alt="Eliminar"></a>'
            '<a href="{}" title="Ver Producto" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-viewlink.svg" alt="Ver Producto"></a>',
            f'/admin/facturacion/detallefactura/{obj.pk}/change/',
            f'/admin/facturacion/detallefactura/{obj.pk}/delete/',
            f'/admin/inventario/producto/{obj.producto.pk}/change/' if obj.producto else '#',
        )

    acciones.short_description = "Acciones"
    acciones.allow_tags = True


# -------------------------------
# 🔹 PAGO ADMIN (vista + imprimir PDF)
# -------------------------------
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('pago_id', 'factura', 'monto', 'metodo_pago', 'fecha_pago', 'acciones')
    list_filter = ('metodo_pago', 'fecha_pago')
    search_fields = ('factura__cliente_name',)  # 👈 cambiado
    ordering = ('-fecha_pago',)

    # === BOTONES DE ACCIÓN ===
    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-changelink.svg" alt="Editar"></a>'
            '<a href="{}" title="Eliminar" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-deletelink.svg" alt="Eliminar"></a>'
            '<a href="{}" title="Ver Pago" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-viewlink.svg" alt="Ver Pago"></a>'
            '<a href="{}" title="Imprimir Factura (PDF)" style="margin-right:8px;">'
            '<img src="/static/admin/img/icon-yes.svg" alt="Factura PDF"></a>',
            f'/admin/facturacion/pago/{obj.pk}/change/',     
            f'/admin/facturacion/pago/{obj.pk}/delete/',
            f'/admin/facturacion/pago/{obj.pk}/change/',
            f'/api/facturacion/facturas/{obj.factura.factura_id}/generar_pdf/',  
        )

    acciones.short_description = "Acciones"
    acciones.allow_tags = True
