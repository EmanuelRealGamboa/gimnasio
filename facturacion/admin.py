from django.contrib import admin
from .models import Factura, DetalleFactura, Pago

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('factura_id', 'cliente_id', 'fecha_emision', 'total', 'estado_pago')
    list_filter = ('estado_pago', 'fecha_emision')
    search_fields = ('cliente_id',)

@admin.register(DetalleFactura)
class DetalleFacturaAdmin(admin.ModelAdmin):
    list_display = ('detalle_id', 'factura', 'producto', 'cantidad', 'precio_unitario')
    list_filter = ('producto',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('pago_id', 'factura', 'monto', 'metodo_pago', 'fecha_pago')
    list_filter = ('metodo_pago', 'fecha_pago')
