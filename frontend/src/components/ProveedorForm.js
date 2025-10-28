import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import proveedorService from '../services/proveedorService';
import './ClienteForm.css';

function ProveedorForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre_empresa: '',
    nombre_contacto: '',
    telefono: '',
    email: '',
    direccion: '',
    servicios_ofrecidos: '',
    activo: true
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isEditMode) {
      fetchProveedor();
    }
  }, [id]);

  const fetchProveedor = async () => {
    try {
      setLoading(true);
      const response = await proveedorService.getProveedor(id);
      const proveedor = response.data;

      setFormData({
        nombre_empresa: proveedor.nombre_empresa || '',
        nombre_contacto: proveedor.nombre_contacto || '',
        telefono: proveedor.telefono || '',
        email: proveedor.email || '',
        direccion: proveedor.direccion || '',
        servicios_ofrecidos: proveedor.servicios_ofrecidos || '',
        activo: proveedor.activo !== undefined ? proveedor.activo : true
      });
    } catch (err) {
      setError('Error al cargar el proveedor');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.nombre_empresa.trim()) {
      newErrors.nombre_empresa = 'El nombre de la empresa es requerido';
    }
    if (!formData.telefono.trim()) {
      newErrors.telefono = 'El teléfono es requerido';
    } else if (!/^[0-9]{10}$/.test(formData.telefono)) {
      newErrors.telefono = 'El teléfono debe tener 10 dígitos';
    }
    if (formData.email && !/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError('');

      if (isEditMode) {
        await proveedorService.updateProveedor(id, formData);
        showSuccessMessage('Proveedor actualizado exitosamente');
      } else {
        await proveedorService.createProveedor(formData);
        showSuccessMessage('Proveedor creado exitosamente');
      }

      setTimeout(() => {
        navigate('/gestion-equipos/proveedores');
      }, 1500);
    } catch (err) {
      const errorMessage = err.response?.data?.message || 'Error al guardar el proveedor. Por favor, verifica los datos.';
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const showSuccessMessage = (message) => {
    const successModal = document.createElement('div');
    successModal.className = 'success-modal-overlay';
    successModal.innerHTML = '<div class="success-modal"><div class="success-icon">✓</div><h2>¡Éxito!</h2><p>' + message + '</p></div>';
    document.body.appendChild(successModal);
    setTimeout(() => successModal.remove(), 2000);
  };

  if (loading && isEditMode) {
    return <div className="loading">Cargando proveedor...</div>;
  }

  return (
    <div className="cliente-form-container">
      <div className="form-header">
        <h2>{isEditMode ? 'Editar Proveedor' : 'Nuevo Proveedor'}</h2>
        <button className="btn-back" onClick={() => navigate('/gestion-equipos/proveedores')}>
          ← Volver
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="cliente-form">
        <div className="form-section">
          <h3>Información de la Empresa</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nombre_empresa">
                Nombre de la Empresa <span className="required">*</span>
              </label>
              <input
                type="text"
                id="nombre_empresa"
                name="nombre_empresa"
                value={formData.nombre_empresa}
                onChange={handleChange}
                className={errors.nombre_empresa ? 'error' : ''}
                placeholder="Ej: Electrónica y Sonido Pro"
              />
              {errors.nombre_empresa && <span className="error-text">{errors.nombre_empresa}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="nombre_contacto">
                Nombre de Contacto
              </label>
              <input
                type="text"
                id="nombre_contacto"
                name="nombre_contacto"
                value={formData.nombre_contacto}
                onChange={handleChange}
                placeholder="Ej: Miguel Hernández"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="telefono">
                Teléfono <span className="required">*</span>
              </label>
              <input
                type="tel"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                className={errors.telefono ? 'error' : ''}
                placeholder="5554445566"
                maxLength="10"
              />
              {errors.telefono && <span className="error-text">{errors.telefono}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="email">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="contacto@empresa.com"
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="direccion">Dirección</label>
            <textarea
              id="direccion"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              placeholder="Dirección completa de la empresa"
              rows="3"
            />
          </div>
        </div>

        <div className="form-section">
          <h3>Servicios y Estado</h3>

          <div className="form-group">
            <label htmlFor="servicios_ofrecidos">Servicios Ofrecidos</label>
            <textarea
              id="servicios_ofrecidos"
              name="servicios_ofrecidos"
              value={formData.servicios_ofrecidos}
              onChange={handleChange}
              placeholder="Descripción de los servicios que ofrece el proveedor"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="activo" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                id="activo"
                name="activo"
                checked={formData.activo}
                onChange={handleChange}
                style={{ width: 'auto' }}
              />
              Proveedor Activo
            </label>
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/gestion-equipos/proveedores')}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar Proveedor' : 'Crear Proveedor'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ProveedorForm;
