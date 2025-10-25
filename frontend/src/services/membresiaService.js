import api from './api';

class MembresiaService {
  // Obtener todas las membresías
  getMembresias(params = {}) {
    return api.get('/membresias/', { params });
  }

  // Obtener solo membresías activas
  getMembresiasActivas() {
    return api.get('/membresias/activas/');
  }

  // Obtener una membresía por ID
  getMembresia(id) {
    return api.get(`/membresias/${id}/`);
  }

  // Crear una nueva membresía
  createMembresia(data) {
    return api.post('/membresias/', data);
  }

  // Actualizar una membresía existente
  updateMembresia(id, data) {
    return api.put(`/membresias/${id}/`, data);
  }

  // Eliminar una membresía
  deleteMembresia(id) {
    return api.delete(`/membresias/${id}/`);
  }

  // Activar/desactivar membresía
  toggleActivo(id) {
    return api.post(`/membresias/${id}/toggle_activo/`);
  }

  // Obtener estadísticas de membresías
  getEstadisticas() {
    return api.get('/membresias/estadisticas/');
  }

  // Buscar membresías con filtros
  searchMembresias(searchTerm, tipo = null, activo = null) {
    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (tipo) params.tipo = tipo;
    if (activo !== null) params.activo = activo;
    return api.get('/membresias/', { params });
  }
}

export default new MembresiaService();
