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
    // Detectar si es FormData (con archivos) o JSON
    const isFormData = data instanceof FormData;

    return api.post('/admin/empleados/', data, {
      headers: isFormData ? {
        'Content-Type': 'multipart/form-data'
      } : {}
    });
  }

  // Actualizar empleado completo (PUT)
  updateEmployee(id, data) {
    // Detectar si es FormData (con archivos) o JSON
    const isFormData = data instanceof FormData;

    return api.put(`/admin/empleados/${id}/`, data, {
      headers: isFormData ? {
        'Content-Type': 'multipart/form-data'
      } : {}
    });
  }

  // Actualizar empleado parcial (PATCH)
  patchEmployee(id, data) {
    return api.patch(`/admin/empleados/${id}/`, data);
  }

  // Eliminar empleado
  deleteEmployee(id) {
    return api.delete(`/admin/empleados/${id}/`);
  }

  // Obtener estadísticas de empleados
  getEstadisticas(sedeId = null) {
    const params = sedeId ? { sede: sedeId } : {};
    return api.get('/admin/empleados/estadisticas/', { params });
  }
}

export default new EmployeeService();
