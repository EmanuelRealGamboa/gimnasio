import axios from 'axios';

const API_URL = 'http://localhost:8000/api/horarios/';

// Configurar interceptor para agregar token
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const horariosService = {
  // ===== TIPOS DE ACTIVIDAD =====
  getTiposActividad: async () => {
    const response = await axios.get(`${API_URL}api/tipos-actividad/`);
    return response.data;
  },

  createTipoActividad: async (data) => {
    const response = await axios.post(`${API_URL}api/tipos-actividad/`, data);
    return response.data;
  },

  updateTipoActividad: async (id, data) => {
    const response = await axios.put(`${API_URL}api/tipos-actividad/${id}/`, data);
    return response.data;
  },

  deleteTipoActividad: async (id) => {
    const response = await axios.delete(`${API_URL}api/tipos-actividad/${id}/`);
    return response.data;
  },

  // ===== HORARIOS =====
  getHorarios: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.sede) params.append('espacio__sede', filters.sede);
    if (filters.estado) params.append('estado', filters.estado);
    if (filters.dia_semana) params.append('dia_semana', filters.dia_semana);
    if (filters.tipo_actividad) params.append('tipo_actividad', filters.tipo_actividad);
    if (filters.entrenador) params.append('entrenador', filters.entrenador);
    if (filters.search) params.append('search', filters.search);

    const response = await axios.get(`${API_URL}api/horarios/?${params.toString()}`);
    return response.data;
  },

  getHorario: async (id) => {
    const response = await axios.get(`${API_URL}api/horarios/${id}/`);
    return response.data;
  },

  createHorario: async (data) => {
    const response = await axios.post(`${API_URL}api/horarios/`, data);
    return response.data;
  },

  updateHorario: async (id, data) => {
    const response = await axios.put(`${API_URL}api/horarios/${id}/`, data);
    return response.data;
  },

  deleteHorario: async (id) => {
    const response = await axios.delete(`${API_URL}api/horarios/${id}/`);
    return response.data;
  },

  getCalendarioSemanal: async (sedeId) => {
    const params = sedeId ? `?sede_id=${sedeId}` : '';
    const response = await axios.get(`${API_URL}api/horarios/calendario_semanal/${params}`);
    return response.data;
  },

  // ===== SESIONES DE CLASE =====
  getSesiones: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.horario) params.append('horario', filters.horario);
    if (filters.estado) params.append('estado', filters.estado);
    if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
    if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);

    const response = await axios.get(`${API_URL}api/sesiones/?${params.toString()}`);
    return response.data;
  },

  getSesion: async (id) => {
    const response = await axios.get(`${API_URL}api/sesiones/${id}/`);
    return response.data;
  },

  createSesion: async (data) => {
    const response = await axios.post(`${API_URL}api/sesiones/`, data);
    return response.data;
  },

  updateSesion: async (id, data) => {
    const response = await axios.put(`${API_URL}api/sesiones/${id}/`, data);
    return response.data;
  },

  deleteSesion: async (id) => {
    const response = await axios.delete(`${API_URL}api/sesiones/${id}/`);
    return response.data;
  },

  getCalendarioMensual: async (año, mes) => {
    const response = await axios.get(`${API_URL}api/sesiones/calendario_mensual/?año=${año}&mes=${mes}`);
    return response.data;
  },

  // ===== RESERVAS DE CLASE =====
  getReservas: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.cliente) params.append('cliente', filters.cliente);
    if (filters.sesion) params.append('sesion_clase', filters.sesion);
    if (filters.estado) params.append('estado', filters.estado);

    const response = await axios.get(`${API_URL}api/reservas-clases/?${params.toString()}`);
    return response.data;
  },

  createReserva: async (data) => {
    const response = await axios.post(`${API_URL}api/reservas-clases/`, data);
    return response.data;
  },

  cancelarReserva: async (id) => {
    const response = await axios.post(`${API_URL}api/reservas-clases/${id}/cancelar/`);
    return response.data;
  },

  getMisReservas: async () => {
    const response = await axios.get(`${API_URL}api/reservas-clases/mis_reservas/`);
    return response.data;
  },

  // ===== ESTADÍSTICAS =====
  getEstadisticas: async (sedeId = null) => {
    const params = sedeId ? `?sede=${sedeId}` : '';
    const response = await axios.get(`${API_URL}api/horarios/estadisticas/${params}`);
    return response.data;
  },
};

export default horariosService;
