import api from './api';

class ClienteService {
  // Obtener todos los clientes
  getClientes(params = {}) {
    return api.get('/clientes/', { params });
  }

  // Obtener un cliente por ID
  getCliente(id) {
    return api.get(`/clientes/${id}/`);
  }

  // Crear un nuevo cliente
  createCliente(data) {
    return api.post('/clientes/', data);
  }

  // Actualizar un cliente existente
  updateCliente(id, data) {
    return api.put(`/clientes/${id}/`, data);
  }

  // Actualización parcial de un cliente
  patchCliente(id, data) {
    return api.patch(`/clientes/${id}/`, data);
  }

  // Eliminar un cliente
  deleteCliente(id) {
    return api.delete(`/clientes/${id}/`);
  }

  // Cambiar el estado de un cliente
  cambiarEstado(id, estado) {
    return api.post(`/clientes/${id}/cambiar_estado/`, { estado });
  }

  // Obtener estadísticas de clientes
  getEstadisticas() {
    return api.get('/clientes/estadisticas/');
  }

  // Buscar clientes con filtros
  searchClientes(searchTerm, estado = null, nivelExperiencia = null) {
    const params = {};
    if (searchTerm) params.search = searchTerm;
    if (estado) params.estado = estado;
    if (nivelExperiencia) params.nivel_experiencia = nivelExperiencia;
    return api.get('/clientes/', { params });
  }
}

export default new ClienteService();
