import api from './api';

class EmployeeService {
  // Obtener lista de empleados
  getEmployees() {
    return api.get('/admin/empleados/');
  }

  // Obtener detalle de un empleado
  getEmployee(id) {
    return api.get(`/admin/empleados/${id}/detalle`);
  }

  // Crear empleado
  createEmployee(data) {
    return api.post('/admin/empleados/', data);
  }

  // Actualizar empleado completo (PUT)
  updateEmployee(id, data) {
    return api.put(`/admin/empleados/${id}/`, data);
  }

  // Actualizar empleado parcial (PATCH)
  patchEmployee(id, data) {
    return api.patch(`/admin/empleados/${id}/`, data);
  }

  // Eliminar empleado
  deleteEmployee(id) {
    return api.delete(`/admin/empleados/${id}/`);
  }
}

export default new EmployeeService();
