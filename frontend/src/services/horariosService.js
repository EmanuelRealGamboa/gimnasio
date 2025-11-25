import axios from 'axios';

const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000/api') + '/horarios';

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
  getTiposActividad: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.sede) params.append('sede', filters.sede);
    if (filters.activo !== undefined) params.append('activo', filters.activo);

    const response = await axios.get(`${API_URL}/tipos-actividad/?${params.toString()}`);
    return response.data;
  },

  createTipoActividad: async (data) => {
    const response = await axios.post(`${API_URL}/tipos-actividad/`, data);
    return response.data;
  },

  updateTipoActividad: async (id, data) => {
    const response = await axios.put(`${API_URL}/tipos-actividad/${id}/`, data);
    return response.data;
  },

  deleteTipoActividad: async (id) => {
    const response = await axios.delete(`${API_URL}/tipos-actividad/${id}/`);
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

    const response = await axios.get(`${API_URL}/horarios/?${params.toString()}`);
    return response.data;
  },

  getHorario: async (id) => {
    const response = await axios.get(`${API_URL}/horarios/${id}/`);
    return response.data;
  },

  createHorario: async (data) => {
    const response = await axios.post(`${API_URL}/horarios/`, data);
    return response.data;
  },

  updateHorario: async (id, data) => {
    const response = await axios.put(`${API_URL}/horarios/${id}/`, data);
    return response.data;
  },

  deleteHorario: async (id) => {
    const response = await axios.delete(`${API_URL}/horarios/${id}/`);
    return response.data;
  },

  getCalendarioSemanal: async (sedeId) => {
    const params = sedeId ? `?sede_id=${sedeId}` : '';
    const response = await axios.get(`${API_URL}/horarios/calendario_semanal/${params}`);
    return response.data;
  },

  // ===== SESIONES DE CLASE =====
  getSesiones: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.horario) params.append('horario', filters.horario);
    if (filters.estado) params.append('estado', filters.estado);
    if (filters.fecha_desde) params.append('fecha_desde', filters.fecha_desde);
    if (filters.fecha_hasta) params.append('fecha_hasta', filters.fecha_hasta);

    const response = await axios.get(`${API_URL}/sesiones/?${params.toString()}`);
    return response.data;
  },

  getSesion: async (id) => {
    const response = await axios.get(`${API_URL}/sesiones/${id}/`);
    return response.data;
  },

  createSesion: async (data) => {
    const response = await axios.post(`${API_URL}/sesiones/`, data);
    return response.data;
  },

  updateSesion: async (id, data) => {
    const response = await axios.put(`${API_URL}/sesiones/${id}/`, data);
    return response.data;
  },

  deleteSesion: async (id) => {
    const response = await axios.delete(`${API_URL}/sesiones/${id}/`);
    return response.data;
  },

  getCalendarioMensual: async (año, mes) => {
    const response = await axios.get(`${API_URL}/sesiones/calendario_mensual/?año=${año}&mes=${mes}`);
    return response.data;
  },

  // ===== RESERVAS DE CLASE =====
  getReservas: async (filters = {}) => {
    const params = new URLSearchParams();
    if (filters.cliente) params.append('cliente', filters.cliente);
    if (filters.sesion) params.append('sesion_clase', filters.sesion);
    if (filters.estado) params.append('estado', filters.estado);

    const response = await axios.get(`${API_URL}/reservas-clases/?${params.toString()}`);
    return response.data;
  },

  createReserva: async (data) => {
    const response = await axios.post(`${API_URL}/reservas-clases/`, data);
    return response.data;
  },

  cancelarReserva: async (id) => {
    const response = await axios.post(`${API_URL}/reservas-clases/${id}/cancelar/`);
    return response.data;
  },

  getMisReservas: async () => {
    const response = await axios.get(`${API_URL}/reservas-clases/mis_reservas/`);
    return response.data;
  },

  // ===== ESTADÍSTICAS =====
  getEstadisticas: async (sedeId = null) => {
    const params = sedeId ? `?sede=${sedeId}` : '';
    const response = await axios.get(`${API_URL}/horarios/estadisticas/${params}`);
    return response.data;
  },

  // ===== HELPERS PARA FORMULARIOS =====
  getEntrenadores: async (sedeId = null) => {
    const params = sedeId ? `?sede=${sedeId}` : '';
    const response = await axios.get(`${API_URL}/horarios/entrenadores/${params}`);
    return response.data;
  },

  getEspacios: async (sedeId = null) => {
    const params = sedeId ? `?sede=${sedeId}` : '';
    const response = await axios.get(`${API_URL}/horarios/espacios/${params}`);
    return response.data;
  },

  // ===== GENERAR SESIONES =====
  generarSesiones: async (horarioId, fechaInicio, fechaFin) => {
    const response = await axios.post(`${API_URL}/horarios/${horarioId}/generar_sesiones/`, {
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin
    });
    return response.data;
  },
};

export default horariosService;
