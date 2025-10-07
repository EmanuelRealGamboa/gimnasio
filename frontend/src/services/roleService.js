import api from './api';

class RoleService {
  // Obtener lista de roles
  getRoles() {
    return api.get('/roles/');
  }
}

export default new RoleService();
