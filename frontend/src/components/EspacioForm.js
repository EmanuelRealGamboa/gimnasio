import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import espacioService from '../services/espacioService';
import sedeService from '../services/sedeService';
import './EspacioForm.css';

function EspacioForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    capacidad: '',
    sede: '',
    imagen: ''
  });

  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchSedes();
    if (isEditMode) {
      fetchEspacio();
    }
  }, [id]);

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      setError('Error al cargar las sedes');
      console.error(err);
    }
  };

  const fetchEspacio = async () => {
    try {
      setLoading(true);
      const response = await espacioService.getEspacio(id);
      setFormData({
        nombre: response.data.nombre,
        descripcion: response.data.descripcion || '',
        capacidad: response.data.capacidad,
        sede: response.data.sede,
        imagen: response.data.imagen || ''
      });
    } catch (err) {
      setError('Error al cargar el espacio');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.sede) {
      newErrors.sede = 'Debe seleccionar una sede';
    }

    if (!formData.capacidad || formData.capacidad <= 0) {
      newErrors.capacidad = 'La capacidad debe ser mayor a 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo cuando el usuario empieza a escribir
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

      const dataToSend = {
        ...formData,
        capacidad: parseInt(formData.capacidad)
      };

      if (isEditMode) {
        await espacioService.updateEspacio(id, dataToSend);
        showSuccessMessage('Espacio actualizado exitosamente');
      } else {
        await espacioService.createEspacio(dataToSend);
        showSuccessMessage('Espacio creado exitosamente');
      }

      setTimeout(() => {
        navigate('/espacios');
      }, 1500);
    } catch (err) {
      setError(
        err.response?.data?.message ||
        'Error al guardar el espacio. Por favor, verifica los datos.'
      );
      console.error(err);
    } finally {
      setLoading(false);
    }
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

  if (loading && isEditMode) {
    return <div className="loading">Cargando espacio...</div>;
  }

  return (
    <div className="espacio-form-container">
      <div className="form-header">
        <h2>{isEditMode ? 'Editar Espacio' : 'Nuevo Espacio'}</h2>
        <button
          className="btn-back"
          onClick={() => navigate('/espacios')}
        >
          ← Volver
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="espacio-form">
        <div className="form-section">
          <h3>Información del Espacio</h3>

          <div className="form-group">
            <label htmlFor="nombre">
              Nombre del Espacio <span className="required">*</span>
            </label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className={errors.nombre ? 'error' : ''}
              placeholder="Ej: Sala de Spinning, Piscina Olímpica"
            />
            {errors.nombre && <span className="error-text">{errors.nombre}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="sede">
              Sede <span className="required">*</span>
            </label>
            <select
              id="sede"
              name="sede"
              value={formData.sede}
              onChange={handleChange}
              className={errors.sede ? 'error' : ''}
            >
              <option value="">Seleccione una sede</option>
              {sedes.map((sede) => (
                <option key={sede.id} value={sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
            {errors.sede && <span className="error-text">{errors.sede}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="capacidad">
              Capacidad <span className="required">*</span>
            </label>
            <input
              type="number"
              id="capacidad"
              name="capacidad"
              value={formData.capacidad}
              onChange={handleChange}
              className={errors.capacidad ? 'error' : ''}
              placeholder="Número de personas"
              min="1"
            />
            {errors.capacidad && <span className="error-text">{errors.capacidad}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="descripcion">
              Descripción
            </label>
            <textarea
              id="descripcion"
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              placeholder="Descripción del espacio (opcional)"
              rows="4"
            />
          </div>

          <div className="form-group">
            <label htmlFor="imagen">
              URL de Imagen
            </label>
            <input
              type="text"
              id="imagen"
              name="imagen"
              value={formData.imagen}
              onChange={handleChange}
              placeholder="https://ejemplo.com/imagen.jpg (opcional)"
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/espacios')}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar Espacio' : 'Crear Espacio'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default EspacioForm;
