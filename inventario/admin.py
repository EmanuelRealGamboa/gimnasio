from django.contrib import admin
from django import forms
from .models import CategoriaProducto, Producto, Inventario

# ==== FORMULARIO PERSONALIZADO ====
class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = '__all__'
        widgets = {
            'cantidad_actual': forms.NumberInput(attrs={'readonly': 'readonly'}),
        }

    class Media:
        js = ('admin/js/inventario_auto_stock.js',)  

# ==== ADMIN ====
@admin.register(CategoriaProducto)
class CategoriaProductoAdmin(admin.ModelAdmin):
    list_display = ('categoria_producto_id', 'nombre')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('producto_id', 'nombre', 'categoria', 'precio_unitario', 'stock')
    search_fields = ('nombre',)
    list_filter = ('categoria',)


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    form = InventarioForm
    list_display = ('inventario_id', 'producto', 'sede', 'cantidad_actual', 'minimo')
    search_fields = ('producto__nombre',)
    list_filter = ('sede',)

    class Media:
        js = ('admin/js/inventario_auto_stock.js',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "producto":
            productos_en_inventario = Inventario.objects.values_list('producto_id', flat=True)
            kwargs["queryset"] = Producto.objects.exclude(producto_id__in=productos_en_inventario)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
