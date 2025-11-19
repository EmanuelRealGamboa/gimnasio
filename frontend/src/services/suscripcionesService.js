import api from './api';

const BASE_URL = '/suscripciones';

const suscripcionesService = {
  // Obtener todas las suscripciones con filtros opcionales
  getSuscripciones: async (filtros = {}) => {
    try {
      const response = await api.get(BASE_URL, { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener suscripciones:', error);
      throw error;
    }
  },

  // Obtener una suscripción específica por ID
  getSuscripcionById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener suscripción:', error);
      throw error;
    }
  },

  // Cancelar una suscripción
  cancelarSuscripcion: async (id) => {
    try {
      const response = await api.post(`${BASE_URL}/${id}/cancelar/`, {});
      return response.data;
    } catch (error) {
      console.error('Error al cancelar suscripción:', error);
      throw error;
    }
  },

  // Renovar una suscripción
  renovarSuscripcion: async (id, metodoPago = 'efectivo') => {
    try {
      const response = await api.post(`${BASE_URL}/${id}/renovar/`, {
        metodo_pago: metodoPago
      });
      return response.data;
    } catch (error) {
      console.error('Error al renovar suscripción:', error);
      throw error;
    }
  },

  // Obtener estadísticas de suscripciones
  getEstadisticas: async (filtros = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/estadisticas/`, { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      throw error;
    }
  },

  // Obtener clientes con membresía activa
  getClientesConMembresia: async () => {
    try {
      const response = await api.get(`${BASE_URL}/clientes_con_membresia/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener clientes con membresía:', error);
      throw error;
    }
  },
};

export default suscripcionesService;
