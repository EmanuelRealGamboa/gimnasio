document.addEventListener("DOMContentLoaded", function () {
    console.log("🧾 Script detallefactura_auto_precio.js cargado correctamente");

    const productoSelect = document.querySelector('select[id*="producto"], select[name*="producto"]');
    const precioInput = document.querySelector('input[id*="precio_unitario"], input[name*="precio_unitario"]');

    if (!productoSelect || !precioInput) {
        console.log("⚠️ Campos no encontrados en el formulario de DetalleFactura");
        return;
    }

    productoSelect.addEventListener("change", function () {
        const productoId = this.value;
        if (!productoId) {
            precioInput.value = "";
            return;
        }

        console.log("🔎 Consultando precio del producto:", productoId);

        fetch(`/api/inventario/productos/${productoId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.precio_unitario !== undefined) {
                    precioInput.value = data.precio_unitario;
                    console.log("💰 Precio actualizado:", data.precio_unitario);
                } else {
                    precioInput.value = 0;
                    console.log("⚠️ Producto sin precio válido");
                }
            })
            .catch(error => {
                console.error("❌ Error al obtener el precio:", error);
                precioInput.value = 0;
            });
    });
});
