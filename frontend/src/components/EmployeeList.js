import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import employeeService from '../services/employeeService';
import sedeService from '../services/sedeService';
import roleService from '../services/roleService';
import ConfirmModal from './ConfirmModal';
import './EmployeeList.css';

// Función para obtener el badge del rol
const getRoleBadge = (rolNombre) => {
  if (!rolNombre) return { color: '#666666', icon: '👤' };

  // Normalizar el nombre del rol para hacer la comparación
  const rolNormalizado = rolNombre.toLowerCase().trim();

  const roleMap = {
    'administrador': { color: '#2a2a2a', icon: '👑' },
    'entrenador': { color: '#22c55e', icon: '💪' },
    'recepcionista': { color: '#f59e0b', icon: '🎫' },
    'cajero': { color: '#2a2a2a', icon: '💰' },
    'supervisor de espacio': { color: '#666666', icon: '🏗️' },
    'personal de limpieza': { color: '#999999', icon: '🧹' }
  };

  return roleMap[rolNormalizado] || { color: '#666666', icon: '👤' };
};

function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sedeFilter, setSedeFilter] = useState('all');
  const [rolFilter, setRolFilter] = useState('all');
  const [sedes, setSedes] = useState([]);
  const [roles, setRoles] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchEmployees();
    fetchSedes();
    fetchRoles();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    filterEmployees();
  }, [employees, searchTerm, statusFilter, sedeFilter, rolFilter]);

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const response = await employeeService.getEmployees();
      setEmployees(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar los empleados');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
      setSedes([]);
    }
  };

  const fetchRoles = async () => {
    try {
      const response = await roleService.getRoles();
      setRoles(response.data);
    } catch (err) {
      console.error('Error al cargar roles:', err);
      setRoles([]);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const response = await employeeService.getEstadisticas();
      setEstadisticas(response.data);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const filterEmployees = () => {
    let filtered = [...employees];

    // Filter by search term - buscar por nombre completo
    if (searchTerm) {
      filtered = filtered.filter(emp => {
        // Construir nombre completo del empleado
        const nombreCompleto = `${emp.nombre || ''} ${emp.apellido_paterno || ''} ${emp.apellido_materno || ''}`.toLowerCase();
        return nombreCompleto.includes(searchTerm.toLowerCase());
      });
    }

    // Filter by status - usando el campo 'estado' del backend
    if (statusFilter !== 'all') {
      filtered = filtered.filter(emp => {
        const isActive = emp.estado && emp.estado.toLowerCase() === 'activo';
        return statusFilter === 'active' ? isActive : !isActive;
      });
    }

    // Filter by sede
    if (sedeFilter !== 'all') {
      filtered = filtered.filter(emp => {
        return emp.sede_id && emp.sede_id.toString() === sedeFilter;
      });
    }

    // Filter by rol
    if (rolFilter !== 'all') {
      filtered = filtered.filter(emp => {
        return emp.rol_id && emp.rol_id.toString() === rolFilter;
      });
    }

    setFilteredEmployees(filtered);
  };

  const handleDeleteClick = (employee) => {
    setEmployeeToDelete(employee);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await employeeService.deleteEmployee(employeeToDelete.id);
      setEmployees(employees.filter(emp => emp.id !== employeeToDelete.id));
      setShowDeleteModal(false);
      setEmployeeToDelete(null);
      showSuccessMessage('Empleado eliminado exitosamente');
    } catch (err) {
      setError('Error al eliminar el empleado');
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setEmployeeToDelete(null);
  };

  const showSuccessMessage = (message) => {
    const successModal = document.createElement('div');
    successModal.className = 'success-modal-overlay';
    successModal.innerHTML = `
      <div class="success-modal">
        <div class="success-icon">✓</div>
        <h2>¡Éxito!</h2>
        <p>${message}</p>
      </div>
    `;
    document.body.appendChild(successModal);
    setTimeout(() => successModal.remove(), 2000);
  };

  const handleViewDetail = (id) => {
    navigate(`/employees/${id}`);
  };

  const handleEdit = (id) => {
    navigate(`/employees/${id}`);
  };

  if (loading) {
    return <div className="loading">Cargando empleados...</div>;
  }

  return (
    <div className="employee-list-container">
      <div className="page-header">
        <h1>Gestión de Empleados</h1>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/employees/new')}
        >
          <span className="btn-icon">+</span>
          Nuevo Empleado
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Estadísticas */}
      {estadisticas && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '0.5rem',
          marginBottom: '0.5rem'
        }}>
          {/* Total Empleados */}
          <div style={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            border: '1px solid #e8e8e8',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <div style={{
              width: '50px',
              height: '50px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              boxShadow: '0 2px 6px rgba(42, 42, 42, 0.4)',
              flexShrink: 0
            }}>
              👥
            </div>
            <div style={{ flex: 1 }}>
              <div style={{
                color: '#1a1a1a',
                fontSize: '1.75rem',
                fontWeight: '700',
                lineHeight: '1',
                marginBottom: '0.25rem'
              }}>
                {estadisticas.total_empleados || 0}
              </div>
              <div style={{
                color: '#666666',
                fontSize: '0.75rem',
                fontWeight: '500',
                textTransform: 'capitalize'
              }}>
                Total Empleados
              </div>
            </div>
          </div>

          {/* Activos */}
          <div style={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            border: '1px solid #e8e8e8',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <div style={{
              width: '50px',
              height: '50px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              boxShadow: '0 2px 6px rgba(34, 197, 94, 0.4)',
              flexShrink: 0
            }}>
              ✓
            </div>
            <div style={{ flex: 1 }}>
              <div style={{
                color: '#22c55e',
                fontSize: '1.75rem',
                fontWeight: '700',
                lineHeight: '1',
                marginBottom: '0.25rem'
              }}>
                {estadisticas.por_estado?.activos || 0}
              </div>
              <div style={{
                color: '#666666',
                fontSize: '0.75rem',
                fontWeight: '500',
                textTransform: 'capitalize'
              }}>
                Activos
              </div>
            </div>
          </div>

          {/* Inactivos */}
          <div style={{
            background: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            border: '1px solid #e8e8e8',
            boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <div style={{
              width: '50px',
              height: '50px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              boxShadow: '0 2px 6px rgba(239, 68, 68, 0.4)',
              flexShrink: 0
            }}>
              ⏸️
            </div>
            <div style={{ flex: 1 }}>
              <div style={{
                color: '#ef4444',
                fontSize: '1.75rem',
                fontWeight: '700',
                lineHeight: '1',
                marginBottom: '0.25rem'
              }}>
                {estadisticas.por_estado?.inactivos || 0}
              </div>
              <div style={{
                color: '#666666',
                fontSize: '0.75rem',
                fontWeight: '500',
                textTransform: 'capitalize'
              }}>
                Inactivos
              </div>
            </div>
          </div>

          {/* Empleados por Sede */}
          {estadisticas.por_sede && estadisticas.por_sede.length > 0 && (
            <div style={{
              background: 'linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%)',
              padding: '1.5rem',
              borderRadius: '16px',
              border: '1px solid #e8e8e8',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              gridColumn: estadisticas.por_sede.length > 2 ? 'span 1' : 'span 1'
            }}>
              <div style={{
                marginBottom: '1.25rem',
                color: '#1a1a1a',
                fontSize: '1rem',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}>
                <span style={{ fontSize: '1.5rem' }}>🏢</span>
                Empleados por Sede
              </div>
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.75rem',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                {estadisticas.por_sede.map((sede, index) => (
                  <div key={index} style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem 1rem',
                    background: '#fafafa',
                    borderRadius: '10px',
                    border: '1px solid #e8e8e8'
                  }}>
                    <span style={{
                      color: '#1a1a1a',
                      fontSize: '0.95rem',
                      fontWeight: '500'
                    }}>
                      {sede.sede__nombre || 'Sin sede'}
                    </span>
                    <span style={{
                      background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)',
                      color: '#ffffff',
                      fontWeight: '700',
                      fontSize: '1rem',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '8px',
                      minWidth: '45px',
                      textAlign: 'center'
                    }}>
                      {sede.total}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="filters-container">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-buttons">
          <button
            className={`filter-btn ${statusFilter === 'all' ? 'active' : ''}`}
            onClick={() => setStatusFilter('all')}
          >
            Todos
          </button>
          <button
            className={`filter-btn ${statusFilter === 'active' ? 'active' : ''}`}
            onClick={() => setStatusFilter('active')}
          >
            Activos
          </button>
          <button
            className={`filter-btn ${statusFilter === 'inactive' ? 'active' : ''}`}
            onClick={() => setStatusFilter('inactive')}
          >
            Inactivos
          </button>
        </div>

        <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div className="filter-sede">
            <label htmlFor="sedeFilter" style={{ marginRight: '0.5rem', color: '#1a1a1a', fontWeight: '600' }}>
              Filtrar por Sede:
            </label>
            <select
              id="sedeFilter"
              value={sedeFilter}
              onChange={(e) => setSedeFilter(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: '1px solid #334155',
                background: '#1e293b',
                color: '#e2e8f0',
                fontSize: '0.9rem',
                cursor: 'pointer',
                minWidth: '200px'
              }}
            >
              <option value="all">Todas las sedes</option>
              {sedes.map(sede => (
                <option key={sede.id} value={sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-rol">
            <label htmlFor="rolFilter" style={{ marginRight: '0.5rem', color: '#1a1a1a', fontWeight: '600' }}>
              Filtrar por Rol:
            </label>
            <select
              id="rolFilter"
              value={rolFilter}
              onChange={(e) => setRolFilter(e.target.value)}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: '1px solid #334155',
                background: '#1e293b',
                color: '#e2e8f0',
                fontSize: '0.9rem',
                cursor: 'pointer',
                minWidth: '200px'
              }}
            >
              <option value="all">Todos los roles</option>
              {roles.filter(rol => rol.nombre !== 'Cliente').map(rol => (
                <option key={rol.id} value={rol.id}>
                  {rol.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="table-container">
        <table className="employee-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.length === 0 ? (
              <tr>
                <td colSpan="5" className="no-data">
                  {searchTerm || statusFilter !== 'all' || sedeFilter !== 'all' || rolFilter !== 'all'
                    ? 'No se encontraron empleados con los filtros aplicados'
                    : 'No hay empleados registrados'}
                </td>
              </tr>
            ) : (
              filteredEmployees.map((employee) => {
                const roleBadge = getRoleBadge(employee.rol_nombre);
                const nombreCompleto = `${employee.nombre || ''} ${employee.apellido_paterno || ''} ${employee.apellido_materno || ''}`.trim();
                return (
                  <tr key={employee.id}>
                    <td className="td-nombre">{nombreCompleto || 'Sin nombre'}</td>
                    <td className="td-email">{employee.email}</td>
                    <td>
                      {employee.rol_nombre ? (
                        <span
                          className="role-badge"
                          style={{
                            backgroundColor: `${roleBadge.color}20`,
                            color: roleBadge.color,
                            borderColor: roleBadge.color
                          }}
                        >
                          {employee.rol_nombre}
                        </span>
                      ) : (
                        <span className="text-muted">Sin rol</span>
                      )}
                    </td>
                    <td>
                      <span className={`status-badge ${employee.estado && employee.estado.toLowerCase() === 'activo' ? 'status-active' : 'status-inactive'}`}>
                        {employee.estado || 'INACTIVO'}
                      </span>
                    </td>
                    <td className="actions">
                    <button
                      className="btn-action btn-view"
                      onClick={() => handleViewDetail(employee.id)}
                      title="Ver detalles"
                    >
                      👁️
                    </button>
                    <button
                      className="btn-action btn-edit"
                      onClick={() => handleEdit(employee.id)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-action btn-delete"
                      onClick={() => handleDeleteClick(employee)}
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="¿Eliminar empleado?"
        message={`¿Estás seguro de que deseas eliminar a ${employeeToDelete ? `${employeeToDelete.nombre} ${employeeToDelete.apellido_paterno}` : 'este empleado'}? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default EmployeeList;
