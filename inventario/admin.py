from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import CategoriaProducto, Producto, Inventario
from instalaciones.models import Sede


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
# FORMULARIO PRODUCTO
# -------------------------------
class ProductoForm(forms.ModelForm):
    """Formulario personalizado para Producto que incluye campo de sede"""
    sede = forms.ModelChoiceField(
        queryset=Sede.objects.all(),
        required=True,
        label="Sede para Inventario",
        help_text="Selecciona la sede donde se registrará este producto en inventario"
    )

    class Meta:
        model = Producto
        fields = '__all__'


# -------------------------------
# PRODUCTO ADMIN
# -------------------------------
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    form = ProductoForm
    list_display = ('producto_id', 'codigo', 'nombre', 'categoria', 'precio_unitario', 'stock_total_display', 'activo', 'acciones')
    search_fields = ('nombre', 'codigo')
    list_filter = ('activo', 'categoria')

    def stock_total_display(self, obj):
        """Muestra el stock total sumando todas las sedes"""
        stock = obj.stock_total
        if stock == 0:
            return format_html('<span style="color: red;">0</span>')
        elif stock < 10:
            return format_html('<span style="color: orange;">{}</span>', stock)
        return stock
    stock_total_display.short_description = 'Stock Total'

    def get_form(self, request, obj=None, **kwargs):
        """Pre-llena el campo sede con la sede actual del inventario al editar"""
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Si estamos editando (no creando)
            try:
                # Obtener el primer inventario asociado a este producto
                inventario = Inventario.objects.filter(producto=obj).first()
                if inventario:
                    form.base_fields['sede'].initial = inventario.sede
                    form.base_fields['sede'].help_text = f"Sede actual: {inventario.sede.nombre}. Cambiar solo si deseas mover el producto."
            except Exception as e:
                pass
        return form

    def save_model(self, request, obj, form, change):
        """
        Crea el inventario automáticamente cuando se crea un producto.
        """
        super().save_model(request, obj, form, change)

        # Obtener la sede del formulario
        sede = form.cleaned_data.get('sede')

        if not change and sede:
            # Si es creación, crea el inventario para la sede seleccionada con cantidad 0
            Inventario.objects.get_or_create(
                producto=obj,
                sede=sede,
                defaults={
                    'cantidad_actual': 0,
                    'cantidad_minima': 5,
                    'cantidad_maxima': 1000
                }
            )
            print(f"🆕 Inventario creado automáticamente para sede '{sede.nombre}': {obj.nombre}")

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
    list_display = ('inventario_id', 'get_codigo_producto', 'producto', 'sede', 'cantidad_actual', 'cantidad_minima', 'estado_stock_display', 'acciones')
    list_filter = ('sede', StockFilter)
    search_fields = ('producto__nombre', 'producto__codigo', 'sede__nombre')

    def estado_stock_display(self, obj):
        """Muestra el estado del stock con colores"""
        estado = obj.estado_stock
        colores = {
            'agotado': 'red',
            'critico': 'orange',
            'bajo': 'yellow',
            'normal': 'green',
            'excedido': 'blue'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colores.get(estado, 'black'),
            estado.upper()
        )
    estado_stock_display.short_description = 'Estado'

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
