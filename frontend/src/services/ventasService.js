import api from './api';

const BASE_URL = '/ventas/ventas-productos';

const ventasService = {
  // Obtener todas las ventas con filtros opcionales
  getVentas: async (filtros = {}) => {
    try {
      const response = await api.get(BASE_URL, { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener ventas:', error);
      throw error;
    }
  },

  // Obtener una venta específica por ID
  getVentaById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener venta:', error);
      throw error;
    }
  },

  // Crear una nueva venta
  crearVenta: async (ventaData) => {
    try {
      const response = await api.post(`${BASE_URL}/crear_venta/`, ventaData);
      return response.data;
    } catch (error) {
      console.error('Error al crear venta:', error);
      throw error;
    }
  },

  // Cancelar una venta
  cancelarVenta: async (id) => {
    try {
      const response = await api.post(`${BASE_URL}/${id}/cancelar/`, {});
      return response.data;
    } catch (error) {
      console.error('Error al cancelar venta:', error);
      throw error;
    }
  },

  // Obtener productos disponibles para venta por sede
  getProductosDisponibles: async (sedeId, filtros = {}) => {
    try {
      const params = { sede: sedeId, ...filtros };
      const response = await api.get(`${BASE_URL}/productos-disponibles/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener productos disponibles:', error);
      throw error;
    }
  },

  // Obtener estadísticas de ventas
  getEstadisticas: async (filtros = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/estadisticas/`, { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      throw error;
    }
  },
};

export default ventasService;
