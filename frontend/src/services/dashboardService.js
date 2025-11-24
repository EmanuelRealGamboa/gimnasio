import api from './api';

const dashboardService = {
  // Obtener estadísticas del dashboard con filtros opcionales
  getStats: async (filtros = {}) => {
    try {
      const response = await api.get('/dashboard/stats/', { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas del dashboard:', error);
      throw error;
    }
  },

  // Obtener estadísticas con filtro de sede
  getStatsBySede: async (sedeId) => {
    try {
      const response = await api.get('/dashboard/stats/', {
        params: { sede: sedeId }
      });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas por sede:', error);
      throw error;
    }
  },

  // Obtener estadísticas con rango de fechas
  getStatsByDateRange: async (fechaInicio, fechaFin, sedeId = null) => {
    try {
      const params = {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin
      };

      if (sedeId) {
        params.sede = sedeId;
      }

      const response = await api.get('/dashboard/stats/', { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas por rango de fechas:', error);
      throw error;
    }
  }
};

export default dashboardService;
