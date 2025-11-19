import api from './api';

const ventasProductosService = {
  // Obtener todas las ventas
  getVentas: (params = {}) => {
    return api.get('/ventas/ventas-productos/', { params });
  },

  // Obtener una venta específica
  getVenta: (id) => {
    return api.get(`/ventas/ventas-productos/${id}/`);
  },

  // Crear una venta con carrito
  crearVenta: (ventaData) => {
    return api.post('/ventas/ventas-productos/crear_venta/', ventaData);
  },

  // Cancelar una venta
  cancelarVenta: (id) => {
    return api.post(`/ventas/ventas-productos/${id}/cancelar/`);
  },

  // Obtener productos disponibles para el POS
  getProductosDisponibles: (params = {}) => {
    return api.get('/ventas/ventas-productos/productos-disponibles/', { params });
  },

  // Obtener estadísticas de ventas
  getEstadisticas: (params = {}) => {
    return api.get('/ventas/ventas-productos/estadisticas/', { params });
  },
};

export default ventasProductosService;
