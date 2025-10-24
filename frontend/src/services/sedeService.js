import api from './api';

class SedeService {
  getSedes() {
    return api.get('/instalaciones/sedes/');
  }

  getSede(id) {
    return api.get(`/instalaciones/sedes/${id}/`);
  }

  createSede(data) {
    return api.post('/instalaciones/sedes/', data);
  }

  updateSede(id, data) {
    return api.put(`/instalaciones/sedes/${id}/`, data);
  }

  deleteSede(id) {
    return api.delete(`/instalaciones/sedes/${id}/`);
  }

  getEspaciosBySede(sedeId) {
    return api.get(`/instalaciones/sedes/${sedeId}/espacios/`);
  }
}

export default new SedeService();
