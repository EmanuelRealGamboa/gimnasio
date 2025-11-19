import axios from 'axios';

const API_URL = 'http://localhost:8000/api/gestion-equipos/';

// Función auxiliar para obtener el token
const getAuthHeader = () => {
  const token = localStorage.getItem('access_token');
  if (!token) {
    // Si no hay token, redirigir al login
    window.location.href = '/login';
    return {};
  }
  return { Authorization: `Bearer ${token}` };
};

// Interceptor para manejar errores 401
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expirado o inválido
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== CATEGORÍAS DE ACTIVOS ====================

export const categoriaActivoService = {
  // CRUD básico
  getAll: () => axios.get(`${API_URL}categorias-activo/`, { headers: getAuthHeader() }),
  getById: (id) => axios.get(`${API_URL}categorias-activo/${id}/`, { headers: getAuthHeader() }),
  create: (data) => axios.post(`${API_URL}categorias-activo/`, data, { headers: getAuthHeader() }),
  update: (id, data) => axios.put(`${API_URL}categorias-activo/${id}/`, data, { headers: getAuthHeader() }),
  delete: (id) => axios.delete(`${API_URL}categorias-activo/${id}/`, { headers: getAuthHeader() }),

  // Acciones personalizadas
  getActivas: () => axios.get(`${API_URL}categorias-activo/activas/`, { headers: getAuthHeader() }),
  toggleActivo: (id) => axios.post(`${API_URL}categorias-activo/${id}/toggle_activo/`, {}, { headers: getAuthHeader() }),
};

// ==================== PROVEEDORES ====================

export const proveedorService = {
  // CRUD básico
  getAll: () => axios.get(`${API_URL}proveedores/`, { headers: getAuthHeader() }),
  getById: (id) => axios.get(`${API_URL}proveedores/${id}/`, { headers: getAuthHeader() }),
  create: (data) => axios.post(`${API_URL}proveedores/`, data, { headers: getAuthHeader() }),
  update: (id, data) => axios.put(`${API_URL}proveedores/${id}/`, data, { headers: getAuthHeader() }),
  delete: (id) => axios.delete(`${API_URL}proveedores/${id}/`, { headers: getAuthHeader() }),

  // Acciones personalizadas
  getActivos: () => axios.get(`${API_URL}proveedores/activos/`, { headers: getAuthHeader() }),
  toggleActivo: (id) => axios.post(`${API_URL}proveedores/${id}/toggle_activo/`, {}, { headers: getAuthHeader() }),
  getMantenimientos: (id) => axios.get(`${API_URL}proveedores/${id}/mantenimientos/`, { headers: getAuthHeader() }),
  getEstadisticas: () => axios.get(`${API_URL}proveedores/estadisticas/`, { headers: getAuthHeader() }),

  // Búsqueda
  search: (query) => axios.get(`${API_URL}proveedores/?search=${query}`, { headers: getAuthHeader() }),
};

// ==================== ACTIVOS ====================

export const activoService = {
  // CRUD básico
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return axios.get(`${API_URL}activos/${queryString ? '?' + queryString : ''}`, { headers: getAuthHeader() });
  },
  getById: (id) => axios.get(`${API_URL}activos/${id}/`, { headers: getAuthHeader() }),
  create: (data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return axios.post(`${API_URL}activos/`, formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      }
    });
  },
  update: (id, data) => {
    const formData = new FormData();
    Object.keys(data).forEach(key => {
      if (data[key] !== null && data[key] !== undefined) {
        formData.append(key, data[key]);
      }
    });
    return axios.put(`${API_URL}activos/${id}/`, formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      }
    });
  },
  delete: (id) => axios.delete(`${API_URL}activos/${id}/`, { headers: getAuthHeader() }),

  // Acciones personalizadas
  porEstado: (estado) => axios.get(`${API_URL}activos/por_estado/?estado=${estado}`, { headers: getAuthHeader() }),
  porSede: (sedeId) => axios.get(`${API_URL}activos/por_sede/?sede_id=${sedeId}`, { headers: getAuthHeader() }),
  cambiarEstado: (id, estado) => axios.post(`${API_URL}activos/${id}/cambiar_estado/`, { estado }, { headers: getAuthHeader() }),
  getHistorialMantenimiento: (id) => axios.get(`${API_URL}activos/${id}/historial_mantenimiento/`, { headers: getAuthHeader() }),
  getProximosMantenimientos: () => axios.get(`${API_URL}activos/proximos_mantenimientos/`, { headers: getAuthHeader() }),
  getEstadisticas: () => axios.get(`${API_URL}activos/estadisticas/`, { headers: getAuthHeader() }),

  // Búsqueda y filtros
  search: (query) => axios.get(`${API_URL}activos/?search=${query}`, { headers: getAuthHeader() }),
  filtrar: (filtros) => {
    const params = new URLSearchParams(filtros).toString();
    return axios.get(`${API_URL}activos/?${params}`, { headers: getAuthHeader() });
  },
};

// ==================== MANTENIMIENTOS ====================

export const mantenimientoService = {
  // CRUD básico
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return axios.get(`${API_URL}mantenimientos/${queryString ? '?' + queryString : ''}`, { headers: getAuthHeader() });
  },
  getById: (id) => axios.get(`${API_URL}mantenimientos/${id}/`, { headers: getAuthHeader() }),
  create: (data) => axios.post(`${API_URL}mantenimientos/`, data, { headers: getAuthHeader() }),
  update: (id, data) => axios.put(`${API_URL}mantenimientos/${id}/`, data, { headers: getAuthHeader() }),
  delete: (id) => axios.delete(`${API_URL}mantenimientos/${id}/`, { headers: getAuthHeader() }),

  // Acciones personalizadas
  getPendientes: () => axios.get(`${API_URL}mantenimientos/pendientes/`, { headers: getAuthHeader() }),
  getEnProceso: () => axios.get(`${API_URL}mantenimientos/en_proceso/`, { headers: getAuthHeader() }),
  getAlertas: () => axios.get(`${API_URL}mantenimientos/alertas/`, { headers: getAuthHeader() }),
  getVencidos: () => axios.get(`${API_URL}mantenimientos/vencidos/`, { headers: getAuthHeader() }),
  iniciar: (id) => axios.post(`${API_URL}mantenimientos/${id}/iniciar/`, {}, { headers: getAuthHeader() }),
  completar: (id, data) => axios.post(`${API_URL}mantenimientos/${id}/completar/`, data, { headers: getAuthHeader() }),
  cancelar: (id, motivo) => axios.post(`${API_URL}mantenimientos/${id}/cancelar/`, { motivo }, { headers: getAuthHeader() }),
  getEstadisticas: () => axios.get(`${API_URL}mantenimientos/estadisticas/`, { headers: getAuthHeader() }),
  porActivo: (activoId) => axios.get(`${API_URL}mantenimientos/por_activo/?activo_id=${activoId}`, { headers: getAuthHeader() }),

  // Búsqueda y filtros
  search: (query) => axios.get(`${API_URL}mantenimientos/?search=${query}`, { headers: getAuthHeader() }),
  filtrar: (filtros) => {
    const params = new URLSearchParams(filtros).toString();
    return axios.get(`${API_URL}mantenimientos/?${params}`, { headers: getAuthHeader() });
  },
};

// ==================== ÓRDENES DE MANTENIMIENTO ====================

export const ordenMantenimientoService = {
  // CRUD básico
  getAll: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    return axios.get(`${API_URL}ordenes/${queryString ? '?' + queryString : ''}`, { headers: getAuthHeader() });
  },
  getById: (id) => axios.get(`${API_URL}ordenes/${id}/`, { headers: getAuthHeader() }),
  create: (data) => axios.post(`${API_URL}ordenes/`, data, { headers: getAuthHeader() }),
  update: (id, data) => axios.put(`${API_URL}ordenes/${id}/`, data, { headers: getAuthHeader() }),
  delete: (id) => axios.delete(`${API_URL}ordenes/${id}/`, { headers: getAuthHeader() }),

  // Acciones personalizadas
  porPrioridad: (prioridad) => axios.get(`${API_URL}ordenes/por_prioridad/?prioridad=${prioridad}`, { headers: getAuthHeader() }),
  getUrgentes: () => axios.get(`${API_URL}ordenes/urgentes/`, { headers: getAuthHeader() }),
  cambiarEstado: (id, estadoOrden) => axios.post(`${API_URL}ordenes/${id}/cambiar_estado/`, { estado_orden: estadoOrden }, { headers: getAuthHeader() }),
  getEstadisticas: () => axios.get(`${API_URL}ordenes/estadisticas/`, { headers: getAuthHeader() }),

  // Búsqueda y filtros
  search: (query) => axios.get(`${API_URL}ordenes/?search=${query}`, { headers: getAuthHeader() }),
  filtrar: (filtros) => {
    const params = new URLSearchParams(filtros).toString();
    return axios.get(`${API_URL}ordenes/?${params}`, { headers: getAuthHeader() });
  },
};

// Exportar todo como objeto por defecto también
export default {
  categoriaActivo: categoriaActivoService,
  proveedor: proveedorService,
  activo: activoService,
  mantenimiento: mantenimientoService,
  ordenMantenimiento: ordenMantenimientoService,
};
