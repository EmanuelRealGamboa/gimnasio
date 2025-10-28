document.addEventListener("DOMContentLoaded", function () {
    console.log("Script inventario_auto_stock.js cargado correctamente");

  
    const productoSelect = document.querySelector('select[id*="producto"], select[name*="producto"]');
    const cantidadInput = document.querySelector('input[id*="cantidad_actual"], input[name*="cantidad_actual"]');

    if (!productoSelect || !cantidadInput) {
        console.log(" Campos no encontrados");
        return;
    }

   
    productoSelect.addEventListener("change", function () {
        const productoId = this.value;
        if (!productoId) {
            cantidadInput.value = "";
            return;
        }

        console.log(" Consultando stock de producto:", productoId);

      
        fetch(`/api/inventario/get_stock_producto/${productoId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.stock !== undefined) {
                    cantidadInput.value = data.stock;
                    console.log(" Stock actualizado visualmente:", data.stock);
                } else {
                    cantidadInput.value = 0;
                    console.log(" Producto sin stock");
                }
            })
            .catch(error => {
                console.error(" Error al obtener el stock:", error);
                cantidadInput.value = 0;
            });
    });
});
