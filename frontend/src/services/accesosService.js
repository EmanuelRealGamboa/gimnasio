import api from './api';

const BASE_URL = '/accesos/registros';

const accesosService = {
  // Validar si un cliente puede acceder
  validarAcceso: async (searchTerm, sedeId) => {
    try {
      const response = await api.post(`${BASE_URL}/validar_acceso/`, {
        search_term: searchTerm,
        sede_id: sedeId
      });
      return response.data;
    } catch (error) {
      console.error('Error al validar acceso:', error);
      throw error;
    }
  },

  // Buscar clientes en tiempo real (autocompletado)
  buscarClientesRealTime: async (searchTerm, sedeId) => {
    try {
      const response = await api.post(`${BASE_URL}/validar_acceso/`, {
        search_term: searchTerm,
        sede_id: sedeId
      });
      return response.data;
    } catch (error) {
      console.error('Error en búsqueda en tiempo real:', error);
      throw error;
    }
  },

  // Registrar un acceso (entrada)
  registrarAcceso: async (clienteId, sedeId, notas = '') => {
    try {
      const response = await api.post(`${BASE_URL}/registrar_acceso/`, {
        cliente_id: clienteId,
        sede_id: sedeId,
        notas: notas
      });
      return response.data;
    } catch (error) {
      console.error('Error al registrar acceso:', error);
      throw error;
    }
  },

  // Obtener registros de acceso con filtros
  getRegistros: async (filtros = {}) => {
    try {
      const response = await api.get(BASE_URL, { params: filtros });
      return response.data;
    } catch (error) {
      console.error('Error al obtener registros:', error);
      throw error;
    }
  },

  // Obtener un registro específico
  getRegistroById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener registro:', error);
      throw error;
    }
  },

  // Obtener estadísticas de accesos
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

export default accesosService;
