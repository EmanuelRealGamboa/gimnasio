import api from './api';

class MembresiaService {
  // Obtener todas las membresías
  getMembresias(params = {}) {
    return api.get('/membresias/', { params });
  }

  // Obtener solo membresías activas
  getMembresiasActivas(sedeId = null) {
    const params = {};
    if (sedeId) {
      params.sede = sedeId;
    }
    return api.get('/membresias/activas/', { params });
  }

  // Obtener membresías por sede
  getMembresiasBySede(sedeId) {
    return api.get('/membresias/', {
      params: { sede: sedeId, activo: true }
    });
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

  // ========== SUSCRIPCIONES ==========

  // Obtener todas las suscripciones
  getSuscripciones(params = {}) {
    return api.get('/suscripciones/', { params });
  }

  // Obtener una suscripción por ID
  getSuscripcion(id) {
    return api.get(`/suscripciones/${id}/`);
  }

  // Crear una nueva suscripción
  createSuscripcion(data) {
    return api.post('/suscripciones/', data);
  }

  // Actualizar una suscripción
  updateSuscripcion(id, data) {
    return api.put(`/suscripciones/${id}/`, data);
  }

  // Eliminar una suscripción
  deleteSuscripcion(id) {
    return api.delete(`/suscripciones/${id}/`);
  }

  // Cancelar una suscripción
  cancelarSuscripcion(id) {
    return api.post(`/suscripciones/${id}/cancelar/`);
  }

  // Renovar una suscripción
  renovarSuscripcion(id, metodo_pago = 'efectivo') {
    return api.post(`/suscripciones/${id}/renovar/`, { metodo_pago });
  }

  // Obtener clientes con membresía activa
  getClientesConMembresia() {
    return api.get('/suscripciones/clientes_con_membresia/');
  }

  // Obtener estadísticas de suscripciones
  getEstadisticasSuscripciones() {
    return api.get('/suscripciones/estadisticas/');
  }

  // Buscar suscripciones por cliente
  getSuscripcionesByCliente(clienteId) {
    return api.get('/suscripciones/', { params: { cliente: clienteId } });
  }
}

export default new MembresiaService();
