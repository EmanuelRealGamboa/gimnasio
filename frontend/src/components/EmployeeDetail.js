import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import employeeService from '../services/employeeService';
import ConfirmModal from './ConfirmModal';
import './EmployeeDetail.css';

function EmployeeDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [employee, setEmployee] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [saving, setSaving] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);

  useEffect(() => {
    fetchEmployeeDetail();
  }, [id]);

  const fetchEmployeeDetail = async () => {
    try {
      setLoading(true);
      const response = await employeeService.getEmployee(id);
      setEmployee(response.data);
      setEditedData(response.data);
    } catch (err) {
      setError('Error al cargar los detalles del empleado');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditToggle = () => {
    if (isEditing) {
      // Cancelar edición - restaurar datos originales
      setEditedData(employee);
    }
    setIsEditing(!isEditing);
    setError('');
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditedData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveClick = () => {
    setShowSaveModal(true);
  };

  const handleConfirmSave = async () => {
    try {
      setSaving(true);
      setError('');
      setShowSaveModal(false);

      // Crear FormData para la actualización
      const formData = new FormData();
      Object.keys(editedData).forEach(key => {
        if (editedData[key] !== null && editedData[key] !== undefined && editedData[key] !== '') {
          formData.append(key, editedData[key]);
        }
      });

      await employeeService.updateEmployee(id, formData);

      // Recargar datos actualizados
      await fetchEmployeeDetail();
      setIsEditing(false);

      // Mostrar mensaje de éxito
      showSuccessMessage('Empleado actualizado exitosamente');
    } catch (err) {
      console.error('Error al actualizar:', err);
      const errorMsg = err.response?.data;
      if (typeof errorMsg === 'object') {
        const errors = Object.entries(errorMsg)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
          .join('\n');
        setError(errors);
      } else {
        setError('Error al actualizar el empleado');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleCancelSave = () => {
    setShowSaveModal(false);
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

  const renderField = (label, fieldName, value, type = 'text', options = null) => {
    if (!isEditing) {
      return (
        <div className="detail-item">
          <label>{label}:</label>
          <span>{value || 'No especificado'}</span>
        </div>
      );
    }

    return (
      <div className="detail-item">
        <label htmlFor={fieldName}>{label}:</label>
        {type === 'select' && options ? (
          <select
            id={fieldName}
            name={fieldName}
            value={editedData[fieldName] || ''}
            onChange={handleInputChange}
            className="edit-input"
          >
            {options.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        ) : (
          <input
            type={type}
            id={fieldName}
            name={fieldName}
            value={editedData[fieldName] || ''}
            onChange={handleInputChange}
            className="edit-input"
          />
        )}
      </div>
    );
  };

  return (
    <div className="detail-container">
      <div className="detail-card">
        <div className="detail-header">
          <h2>Detalles del Empleado</h2>
          <div className="header-actions">
            {isEditing ? (
              <>
                <button
                  className="btn btn-success"
                  onClick={handleSaveClick}
                  disabled={saving}
                >
                  {saving ? '💾 Guardando...' : '💾 Guardar'}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={handleEditToggle}
                  disabled={saving}
                >
                  ✖ Cancelar
                </button>
              </>
            ) : (
              <>
                <button
                  className="btn btn-primary"
                  onClick={handleEditToggle}
                >
                  ✏️ Editar
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => navigate('/employees')}
                >
                  ← Volver
                </button>
              </>
            )}
          </div>
        </div>

        {error && (
          <div className="error-message">
            <pre>{error}</pre>
          </div>
        )}

        <div className="detail-section">
          <h3>Datos Personales</h3>
          <div className="detail-grid">
            {renderField('Nombre', 'nombre', employee.nombre)}
            {renderField('Apellido Paterno', 'apellido_paterno', employee.apellido_paterno)}
            {renderField('Apellido Materno', 'apellido_materno', employee.apellido_materno)}
            {renderField('Fecha de Nacimiento', 'fecha_nacimiento', employee.fecha_nacimiento, 'date')}
            {renderField('Sexo', 'sexo', employee.sexo, 'select', [
              { value: '', label: 'Seleccionar' },
              { value: 'Masculino', label: 'Masculino' },
              { value: 'Femenino', label: 'Femenino' }
            ])}
            {renderField('Teléfono', 'telefono', employee.telefono, 'tel')}
            <div className="detail-item full-width">
              {isEditing ? (
                <>
                  <label htmlFor="direccion">Dirección:</label>
                  <input
                    type="text"
                    id="direccion"
                    name="direccion"
                    value={editedData.direccion || ''}
                    onChange={handleInputChange}
                    className="edit-input"
                  />
                </>
              ) : (
                <>
                  <label>Dirección:</label>
                  <span>{employee.direccion || 'No especificado'}</span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Datos de Usuario</h3>
          <div className="detail-grid">
            {renderField('Email', 'email', employee.email, 'email')}
          </div>
        </div>

        <div className="detail-section">
          <h3>Datos Laborales</h3>
          <div className="detail-grid">
            {renderField('Puesto', 'puesto', employee.puesto)}
            {renderField('Departamento', 'departamento', employee.departamento)}
            {renderField('Fecha de Contratación', 'fecha_contratacion', employee.fecha_contratacion, 'date')}
            {renderField('Tipo de Contrato', 'tipo_contrato', employee.tipo_contrato, 'select', [
              { value: 'Indefinido', label: 'Indefinido' },
              { value: 'Temporal', label: 'Temporal' },
              { value: 'Por Proyecto', label: 'Por Proyecto' }
            ])}
            {renderField('Salario', 'salario', employee.salario ? parseFloat(employee.salario).toFixed(2) : '', 'number')}
            {renderField('Estado', 'estado', employee.estado, 'select', [
              { value: 'Activo', label: 'Activo' },
              { value: 'Inactivo', label: 'Inactivo' },
              { value: 'Suspendido', label: 'Suspendido' }
            ])}
            {renderField('RFC', 'rfc', employee.rfc)}
            <div className="detail-item">
              <label>Rol:</label>
              <span>{employee.rol_nombre || 'No asignado'}</span>
            </div>
          </div>
        </div>

        <div className="detail-section">
          <h3>Documentos Adjuntos</h3>
          <div className="documents-grid">
            <div className="document-item">
              <div className="document-header">
                <span className="document-icon">📄</span>
                <label>Identificación Oficial</label>
              </div>
              {employee.identificacion_url ? (
                <a
                  href={employee.identificacion_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-document"
                >
                  Ver Documento
                </a>
              ) : (
                <span className="no-document">No disponible</span>
              )}
            </div>

            <div className="document-item">
              <div className="document-header">
                <span className="document-icon">🏠</span>
                <label>Comprobante de Domicilio</label>
              </div>
              {employee.comprobante_url ? (
                <a
                  href={employee.comprobante_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-document"
                >
                  Ver Documento
                </a>
              ) : (
                <span className="no-document">No disponible</span>
              )}
            </div>

            <div className="document-item">
              <div className="document-header">
                <span className="document-icon">🎓</span>
                <label>Certificados</label>
              </div>
              {employee.certificados_url ? (
                <a
                  href={employee.certificados_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-document"
                >
                  Ver Documento
                </a>
              ) : (
                <span className="no-document">No disponible</span>
              )}
            </div>
          </div>
        </div>
      </div>

      <ConfirmModal
        isOpen={showSaveModal}
        onClose={handleCancelSave}
        onConfirm={handleConfirmSave}
        title="¿Guardar cambios?"
        message="¿Estás seguro de que deseas guardar los cambios realizados al empleado?"
        confirmText="Guardar"
        cancelText="Cancelar"
        type="info"
      />
    </div>
  );
}

export default EmployeeDetail;
