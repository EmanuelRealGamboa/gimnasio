from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import CategoriaProducto, Producto, Inventario


# -------------------------------
# FORMULARIO INVENTARIO
# -------------------------------
class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = '__all__'
        # ❌ Se quitó el readonly para permitir modificar cantidad_actual
        widgets = {
            'cantidad_actual': forms.NumberInput(attrs={'min': 0}),
        }

    class Media:
        js = ('admin/js/inventario_auto_stock.js',)


# -------------------------------
# FILTRO DE STOCK
# -------------------------------
class StockFilter(admin.SimpleListFilter):
    title = _('Stock')
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return (
            ('todos', _('Todos')),
            ('con_stock', _('Con stock')),
            ('sin_stock', _('Sin stock')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'con_stock':
            if hasattr(queryset.model, 'stock'):
                return queryset.filter(stock__gt=0)
            return queryset.filter(cantidad_actual__gt=0)
        elif self.value() == 'sin_stock':
            if hasattr(queryset.model, 'stock'):
                return queryset.filter(stock__lte=0)
            return queryset.filter(cantidad_actual__lte=0)
        return queryset


# -------------------------------
# CATEGORÍA PRODUCTO ADMIN
# -------------------------------
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'acciones')
    search_fields = ('nombre',)

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar"><img src="/static/admin/img/icon-changelink.svg"></a>'
            '<a href="{}" title="Eliminar"><img src="/static/admin/img/icon-deletelink.svg" style="margin-left:8px;"></a>',
            f'/admin/inventario/categoriaproducto/{obj.pk}/change/',
            f'/admin/inventario/categoriaproducto/{obj.pk}/delete/',
        )
    acciones.short_description = "Acciones"


# -------------------------------
# PRODUCTO ADMIN
# -------------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('producto_id', 'codigo', 'nombre', 'categoria', 'precio_unitario', 'stock', 'acciones')
    search_fields = ('nombre', 'codigo')
    list_filter = (StockFilter,)

    def save_model(self, request, obj, form, change):
        """
        ✅ Sincroniza el inventario automáticamente cuando se crea o edita un producto.
        """
        super().save_model(request, obj, form, change)

        try:
            inventario = Inventario.objects.get(producto=obj)
            inventario.cantidad_actual = obj.stock  # 🔄 Sincroniza stock
            inventario.save(update_fields=['cantidad_actual'])
            print(f"✅ Inventario actualizado desde admin: {obj.nombre} → {obj.stock}")
        except Inventario.DoesNotExist:
            Inventario.objects.create(
                producto=obj,
                cantidad_actual=obj.stock,
                minimo=5
            )
            print(f"🆕 Inventario creado automáticamente desde admin: {obj.nombre}")

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar"><img src="/static/admin/img/icon-changelink.svg"></a>'
            '<a href="{}" title="Eliminar"><img src="/static/admin/img/icon-deletelink.svg" style="margin-left:8px;"></a>'
            '<a href="{}" title="Ver Producto"><img src="/static/admin/img/icon-viewlink.svg" style="margin-left:8px;"></a>',
            f'/admin/inventario/producto/{obj.pk}/change/',
            f'/admin/inventario/producto/{obj.pk}/delete/',
            f'/admin/inventario/producto/{obj.pk}/change/',
        )
    acciones.short_description = "Acciones"


# -------------------------------
# INVENTARIO ADMIN
# -------------------------------
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    form = InventarioForm
    list_display = ('inventario_id', 'get_codigo_producto', 'producto', 'sede', 'cantidad_actual', 'minimo', 'acciones')
    list_filter = (StockFilter,)
    search_fields = ('producto__nombre', 'producto__codigo')

    def get_codigo_producto(self, obj):
        return obj.producto.codigo or "-"
    get_codigo_producto.short_description = 'Código'

    def acciones(self, obj):
        return format_html(
            '<a href="{}" title="Editar"><img src="/static/admin/img/icon-changelink.svg"></a>'
            '<a href="{}" title="Eliminar"><img src="/static/admin/img/icon-deletelink.svg" style="margin-left:8px;"></a>'
            '<a href="{}" title="Ver Inventario"><img src="/static/admin/img/icon-viewlink.svg" style="margin-left:8px;"></a>',
            f'/admin/inventario/inventario/{obj.pk}/change/',
            f'/admin/inventario/inventario/{obj.pk}/delete/',
            f'/admin/inventario/inventario/{obj.pk}/change/',
        )
    acciones.short_description = "Acciones"
