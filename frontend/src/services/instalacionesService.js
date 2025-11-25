import api from './api'; // api.js ya usa REACT_APP_API_URL

class InstalacionesService {
  // ========== SEDES ==========

  // Obtener todas las sedes
  getSedes() {
    return api.get('/instalaciones/sedes/');
  }

  // Obtener una sede por ID
  getSede(id) {
    return api.get(`/instalaciones/sedes/${id}/`);
  }

  // ========== ESPACIOS ==========

  // Obtener todos los espacios
  getEspacios(params = {}) {
    return api.get('/instalaciones/espacios/', { params });
  }

  // Obtener espacios por sede
  getEspaciosBySede(sedeId) {
    return api.get(`/instalaciones/espacios/`, {
      params: { sede: sedeId }
    });
  }

  // Obtener un espacio por ID
  getEspacio(id) {
    return api.get(`/instalaciones/espacios/${id}/`);
  }
}

export default new InstalacionesService();
