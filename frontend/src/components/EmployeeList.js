import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import employeeService from '../services/employeeService';
import './EmployeeList.css';

function EmployeeList() {
  const [employees, setEmployees] = useState([]);
  const [filteredEmployees, setFilteredEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const navigate = useNavigate();

  useEffect(() => {
    fetchEmployees();
  }, []);

  useEffect(() => {
    filterEmployees();
  }, [employees, searchTerm, statusFilter]);

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

  const filterEmployees = () => {
    let filtered = [...employees];

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(emp =>
        emp.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(emp =>
        statusFilter === 'active' ? emp.is_active : !emp.is_active
      );
    }

    setFilteredEmployees(filtered);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este empleado?')) {
      try {
        await employeeService.deleteEmployee(id);
        setEmployees(employees.filter(emp => emp.id !== id));
      } catch (err) {
        alert('Error al eliminar el empleado');
        console.error(err);
      }
    }
  };

  const handleViewDetail = (id) => {
    navigate(`/employees/${id}`);
  };

  const handleEdit = (id) => {
    navigate(`/employees/edit/${id}`);
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

      <div className="filters-container">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por email..."
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
      </div>

      <div className="table-container">
        <table className="employee-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Estado</th>
              <th>Persona ID</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.length === 0 ? (
              <tr>
                <td colSpan="5" className="no-data">
                  {searchTerm || statusFilter !== 'all'
                    ? 'No se encontraron empleados con los filtros aplicados'
                    : 'No hay empleados registrados'}
                </td>
              </tr>
            ) : (
              filteredEmployees.map((employee) => (
                <tr key={employee.id}>
                  <td className="td-id">{employee.id}</td>
                  <td className="td-email">{employee.email}</td>
                  <td>
                    <span className={`status-badge ${employee.is_active ? 'status-active' : 'status-inactive'}`}>
                      {employee.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td>{employee.persona || '-'}</td>
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
                      onClick={() => handleDelete(employee.id)}
                      title="Eliminar"
                    >
                      🗑️
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default EmployeeList;
