import api from './api';

class InventarioService {
  // ==================== CATEGORÍAS ====================

  // Obtener todas las categorías
  getCategorias(params = {}) {
    return api.get('/inventario/categorias/', { params });
  }

  // Obtener una categoría por ID
  getCategoria(id) {
    return api.get(`/inventario/categorias/${id}/`);
  }

  // Crear una nueva categoría
  createCategoria(data) {
    return api.post('/inventario/categorias/', data);
  }

  // Actualizar una categoría existente
  updateCategoria(id, data) {
    return api.put(`/inventario/categorias/${id}/`, data);
  }

  // Eliminar una categoría
  deleteCategoria(id) {
    return api.delete(`/inventario/categorias/${id}/`);
  }

  // ==================== PRODUCTOS ====================

  // Obtener todos los productos
  getProductos(params = {}) {
    return api.get('/inventario/productos/', { params });
  }

  // Obtener un producto por ID
  getProducto(id) {
    return api.get(`/inventario/productos/${id}/`);
  }

  // Crear un nuevo producto
  createProducto(data) {
    return api.post('/inventario/productos/', data);
  }

  // Actualizar un producto existente
  updateProducto(id, data) {
    return api.put(`/inventario/productos/${id}/`, data);
  }

  // Eliminar un producto
  deleteProducto(id) {
    return api.delete(`/inventario/productos/${id}/`);
  }

  // ==================== INVENTARIO ====================

  // Obtener todo el inventario
  getInventario(params = {}) {
    return api.get('/inventario/inventario/', { params });
  }

  // Obtener un registro de inventario por ID
  getInventarioItem(id) {
    return api.get(`/inventario/inventario/${id}/`);
  }

  // Actualizar un registro de inventario
  updateInventario(id, data) {
    return api.put(`/inventario/inventario/${id}/`, data);
  }

  // Filtrar inventario (endpoint personalizado)
  filtrarInventario(tipo, valor, stock = 'todos') {
    const params = { stock };
    if (tipo && valor) {
      params.tipo = tipo;
      params.valor = valor;
    }
    return api.get('/inventario/inventario/filtrar/', { params });
  }

  // ==================== BÚSQUEDAS ====================

  // Buscar productos por nombre o código
  buscarProductos(searchTerm) {
    return api.get('/inventario/productos/', {
      params: { search: searchTerm }
    });
  }

  // Buscar inventario por sede
  getInventarioBySede(sedeId) {
    return api.get('/inventario/inventario/', {
      params: { sede: sedeId }
    });
  }

  // Buscar productos con stock bajo
  getProductosStockBajo() {
    return api.get('/inventario/inventario/filtrar/', {
      params: { stock: 'sin_stock' }
    });
  }

  // Buscar productos con stock disponible
  getProductosConStock() {
    return api.get('/inventario/inventario/filtrar/', {
      params: { stock: 'con_stock' }
    });
  }
}

export default new InventarioService();
