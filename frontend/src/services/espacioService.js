import api from './api';

class EspacioService {
  getEspacios(sedeId = null) {
    const params = sedeId ? { sede: sedeId } : {};
    return api.get('/instalaciones/espacios/', { params });
  }

  getEspacio(id) {
    return api.get(`/instalaciones/espacios/${id}/`);
  }

  createEspacio(data) {
    return api.post('/instalaciones/espacios/', data);
  }

  updateEspacio(id, data) {
    return api.put(`/instalaciones/espacios/${id}/`, data);
  }

  deleteEspacio(id) {
    return api.delete(`/instalaciones/espacios/${id}/`);
  }
}

export default new EspacioService();
