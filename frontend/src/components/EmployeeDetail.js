import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import employeeService from '../services/employeeService';
import './EmployeeDetail.css';

function EmployeeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchEmployeeDetail();
  }, [id]);

  const fetchEmployeeDetail = async () => {
    try {
      setLoading(true);
      const response = await employeeService.getEmployee(id);
      setEmployee(response.data);
    } catch (err) {
      setError('Error al cargar los detalles del empleado');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando detalles del empleado...</div>;
  }

  if (error || !employee) {
    return (
      <div className="detail-container">
        <div className="error-message">{error || 'Empleado no encontrado'}</div>
        <button className="btn btn-secondary" onClick={() => navigate('/employees')}>
          Volver al Listado
        </button>
      </div>
    );
  }

  return (
    <div className="detail-container">
      <div className="detail-card">
        <div className="detail-header">
          <h2>Detalles del Empleado</h2>
          <div className="header-actions">
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/employees/edit/${id}`)}
            >
              ✏️ Editar
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => navigate('/employees')}
            >
              ← Volver
            </button>
          </div>
        </div>

        <div className="detail-section">
          <h3>Datos Personales</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Nombre Completo:</label>
              <span>
                {employee.nombre} {employee.apellido_paterno}{' '}
                {employee.apellido_materno}
              </span>
            </div>
            <div className="detail-item">
              <label>Fecha de Nacimiento:</label>
              <span>{employee.fecha_nacimiento || 'No especificado'}</span>
            </div>
            <div className="detail-item">
              <label>Sexo:</label>
              <span>{employee.sexo || 'No especificado'}</span>
            </div>
            <div className="detail-item">
              <label>Teléfono:</label>
              <span>{employee.telefono}</span>
            </div>
            <div className="detail-item full-width">
              <label>Dirección:</label>
              <span>{employee.direccion || 'No especificado'}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Datos de Usuario</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Email:</label>
              <span>{employee.email}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Datos Laborales</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <label>Puesto:</label>
              <span>{employee.puesto}</span>
            </div>
            <div className="detail-item">
              <label>Departamento:</label>
              <span>{employee.departamento}</span>
            </div>
            <div className="detail-item">
              <label>Fecha de Contratación:</label>
              <span>{employee.fecha_contratacion}</span>
            </div>
            <div className="detail-item">
              <label>Tipo de Contrato:</label>
              <span>{employee.tipo_contrato}</span>
            </div>
            <div className="detail-item">
              <label>Salario:</label>
              <span>${parseFloat(employee.salario).toLocaleString('es-MX')}</span>
            </div>
            <div className="detail-item">
              <label>Estado:</label>
              <span className={`status status-${employee.estado.toLowerCase()}`}>
                {employee.estado}
              </span>
            </div>
            <div className="detail-item">
              <label>RFC:</label>
              <span>{employee.rfc}</span>
            </div>
            <div className="detail-item">
              <label>Rol:</label>
              <span>{employee.rol_nombre || 'No asignado'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmployeeDetail;
