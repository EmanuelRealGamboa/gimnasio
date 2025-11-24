import api from './api';

const BASE_URL = '/limpieza';

const limpiezaService = {
  // =====================================
  // TAREAS DE LIMPIEZA (Catálogo)
  // =====================================
  getTareas: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/tareas/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener tareas:', error);
      throw error;
    }
  },

  getTareaById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/tareas/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener tarea:', error);
      throw error;
    }
  },

  crearTarea: async (data) => {
    try {
      const response = await api.post(`${BASE_URL}/tareas/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al crear tarea:', error);
      throw error;
    }
  },

  actualizarTarea: async (id, data) => {
    try {
      const response = await api.put(`${BASE_URL}/tareas/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar tarea:', error);
      throw error;
    }
  },

  eliminarTarea: async (id) => {
    try {
      const response = await api.delete(`${BASE_URL}/tareas/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al eliminar tarea:', error);
      throw error;
    }
  },

  // =====================================
  // PERSONAL DE LIMPIEZA
  // =====================================
  getPersonal: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/personal/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener personal:', error);
      throw error;
    }
  },

  getPersonalById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/personal/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener personal:', error);
      throw error;
    }
  },

  // =====================================
  // HORARIOS
  // =====================================
  getHorarios: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/horarios/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener horarios:', error);
      throw error;
    }
  },

  getHorarioById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/horarios/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener horario:', error);
      throw error;
    }
  },

  crearHorario: async (data) => {
    try {
      const response = await api.post(`${BASE_URL}/horarios/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al crear horario:', error);
      throw error;
    }
  },

  actualizarHorario: async (id, data) => {
    try {
      const response = await api.put(`${BASE_URL}/horarios/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar horario:', error);
      throw error;
    }
  },

  eliminarHorario: async (id) => {
    try {
      const response = await api.delete(`${BASE_URL}/horarios/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al eliminar horario:', error);
      throw error;
    }
  },

  // =====================================
  // ASIGNACIONES DE TAREAS
  // =====================================
  getAsignaciones: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/asignaciones/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener asignaciones:', error);
      throw error;
    }
  },

  getAsignacionById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/asignaciones/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener asignación:', error);
      throw error;
    }
  },

  crearAsignacion: async (data) => {
    try {
      const response = await api.post(`${BASE_URL}/asignaciones/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al crear asignación:', error);
      throw error;
    }
  },

  actualizarAsignacion: async (id, data) => {
    try {
      const response = await api.put(`${BASE_URL}/asignaciones/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar asignación:', error);
      throw error;
    }
  },

  eliminarAsignacion: async (id) => {
    try {
      const response = await api.delete(`${BASE_URL}/asignaciones/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al eliminar asignación:', error);
      throw error;
    }
  },

  marcarCompletada: async (id, data) => {
    try {
      const response = await api.post(`${BASE_URL}/asignaciones/${id}/marcar_completada/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al marcar tarea como completada:', error);
      throw error;
    }
  },

  marcarEnProgreso: async (id) => {
    try {
      const response = await api.post(`${BASE_URL}/asignaciones/${id}/marcar_en_progreso/`);
      return response.data;
    } catch (error) {
      console.error('Error al marcar tarea en progreso:', error);
      throw error;
    }
  },

  cancelarAsignacion: async (id, data) => {
    try {
      const response = await api.post(`${BASE_URL}/asignaciones/${id}/cancelar/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al cancelar tarea:', error);
      throw error;
    }
  },

  // =====================================
  // CHECKLISTS
  // =====================================
  getChecklists: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/checklists/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener checklists:', error);
      throw error;
    }
  },

  getChecklistById: async (id) => {
    try {
      const response = await api.get(`${BASE_URL}/checklists/${id}/`);
      return response.data;
    } catch (error) {
      console.error('Error al obtener checklist:', error);
      throw error;
    }
  },

  crearChecklist: async (data) => {
    try {
      const response = await api.post(`${BASE_URL}/checklists/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al crear checklist:', error);
      throw error;
    }
  },

  actualizarChecklist: async (id, data) => {
    try {
      const response = await api.put(`${BASE_URL}/checklists/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al actualizar checklist:', error);
      throw error;
    }
  },

  verificarChecklist: async (id, data) => {
    try {
      const response = await api.post(`${BASE_URL}/checklists/${id}/verificar/`, data);
      return response.data;
    } catch (error) {
      console.error('Error al verificar checklist:', error);
      throw error;
    }
  },

  // =====================================
  // ESTADÍSTICAS
  // =====================================
  getEstadisticas: async (params = {}) => {
    try {
      const response = await api.get(`${BASE_URL}/estadisticas/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error al obtener estadísticas:', error);
      throw error;
    }
  },
};

export default limpiezaService;
