import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import inventarioService from '../services/inventarioService';
import './Inventario.css';

function CategoriaProductoForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre: ''
  });

  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');

  useEffect(() => {
    if (isEditMode) {
      fetchCategoria();
    }
  }, [id]);

  const fetchCategoria = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getCategoria(id);
      setFormData({
        nombre: response.data.nombre || ''
      });
    } catch (err) {
      console.error('Error al cargar categoría:', err);
      showNotif('Error al cargar la categoría', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      showNotif('Por favor, completa todos los campos requeridos', 'error');
      return;
    }

    try {
      setLoading(true);

      if (isEditMode) {
        await inventarioService.updateCategoria(id, formData);
        showNotif('✓ Categoría actualizada exitosamente', 'success');
      } else {
        await inventarioService.createCategoria(formData);
        showNotif('✓ Categoría creada exitosamente', 'success');
      }

      setTimeout(() => {
        navigate('/inventario/categorias');
      }, 1500);
    } catch (err) {
      console.error('Error al guardar categoría:', err);
      showNotif(`Error al ${isEditMode ? 'actualizar' : 'crear'} la categoría`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  return (
    <div className="inventario-container">
      {/* Notification */}
      {showNotification && (
        <div className={`notification ${notificationType} show`}>
          {notificationMessage}
        </div>
      )}

      {/* Header */}
      <div className="inventario-header">
        <div>
          <h1>{isEditMode ? '✏️ Editar Categoría' : '➕ Nueva Categoría'}</h1>
          <p className="inventario-subtitle">
            {isEditMode ? 'Modifica los datos de la categoría' : 'Completa los datos para crear una nueva categoría'}
          </p>
        </div>
        <button
          className="btn-secondary"
          onClick={() => navigate('/inventario/categorias')}
        >
          ← Volver
        </button>
      </div>

      {/* Form */}
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3 className="form-section-title">Información de la Categoría</h3>

            <div className="form-grid">
              <div className="form-group full-width">
                <label htmlFor="nombre">
                  Nombre de la Categoría <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  className={errors.nombre ? 'error' : ''}
                  placeholder="Ej: Suplementos, Equipamiento, Accesorios..."
                  disabled={loading}
                />
                {errors.nombre && (
                  <span className="error-message">{errors.nombre}</span>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/inventario/categorias')}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-small"></span>
                  {isEditMode ? 'Actualizando...' : 'Guardando...'}
                </>
              ) : (
                <>
                  {isEditMode ? '💾 Actualizar' : '➕ Crear'} Categoría
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CategoriaProductoForm;
