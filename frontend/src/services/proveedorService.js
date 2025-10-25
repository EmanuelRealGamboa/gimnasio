import api from './api';

class ProveedorService {
  // Obtener todos los proveedores
  getProveedores(params = {}) {
    return api.get('/gestion-equipos/proveedores/', { params });
  }

  // Obtener un proveedor por ID
  getProveedor(id) {
    return api.get(`/gestion-equipos/proveedores/${id}/`);
  }

  // Crear un nuevo proveedor
  createProveedor(data) {
    return api.post('/gestion-equipos/proveedores/', data);
  }

  // Actualizar un proveedor existente
  updateProveedor(id, data) {
    return api.put(`/gestion-equipos/proveedores/${id}/`, data);
  }

  // Actualización parcial de un proveedor
  patchProveedor(id, data) {
    return api.patch(`/gestion-equipos/proveedores/${id}/`, data);
  }

  // Eliminar un proveedor
  deleteProveedor(id) {
    return api.delete(`/gestion-equipos/proveedores/${id}/`);
  }

  // Activar/Desactivar proveedor
  toggleActivo(id) {
    return api.post(`/gestion-equipos/proveedores/${id}/toggle_activo/`);
  }

  // Obtener solo proveedores activos
  getProveedoresActivos() {
    return api.get('/gestion-equipos/proveedores/activos/');
  }

  // Obtener mantenimientos de un proveedor
  getMantenimientosProveedor(id) {
    return api.get(`/gestion-equipos/proveedores/${id}/mantenimientos/`);
  }

  // Obtener estadísticas de proveedores
  getEstadisticas() {
    return api.get('/gestion-equipos/proveedores/estadisticas/');
  }
}

export default new ProveedorService();
