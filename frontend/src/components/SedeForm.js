import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import sedeService from '../services/sedeService';
import './SedeForm.css';

function SedeForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;

  const [formData, setFormData] = useState({
    nombre: '',
    direccion: '',
    telefono: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isEditMode) {
      fetchSedeDetail();
    }
  }, [id, isEditMode]);

  const fetchSedeDetail = async () => {
    try {
      setLoading(true);
      const response = await sedeService.getSede(id);
      setFormData(response.data);
    } catch (err) {
      setError('Error al cargar los datos de la sede');
      console.error(err);
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
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isEditMode) {
        await sedeService.updateSede(id, formData);
        showSuccessMessage('Sede actualizada exitosamente');
      } else {
        await sedeService.createSede(formData);
        showSuccessMessage('Sede creada exitosamente');
      }

      setTimeout(() => {
        navigate('/sedes');
      }, 2000);
    } catch (err) {
      console.error('Error:', err);
      setError('Error al guardar la sede');
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

  if (loading && isEditMode && !formData.nombre) {
    return <div className="loading">Cargando datos de la sede...</div>;
  }

  return (
    <div className="sede-form-container">
      <div className="form-card">
        <h2>{isEditMode ? 'Editar Sede' : 'Nueva Sede'}</h2>

        {error && (
          <div className="error-message">
            <pre>{error}</pre>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="nombre">Nombre *</label>
            <input
              type="text"
              id="nombre"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              required
              placeholder="Ej: Sede Central"
            />
          </div>

          <div className="form-group">
            <label htmlFor="direccion">Dirección *</label>
            <input
              type="text"
              id="direccion"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              required
              placeholder="Ej: Av. Principal 123, Col. Centro"
            />
          </div>

          <div className="form-group">
            <label htmlFor="telefono">Teléfono</label>
            <input
              type="tel"
              id="telefono"
              name="telefono"
              value={formData.telefono}
              onChange={handleChange}
              placeholder="Ej: 1234567890"
              maxLength="15"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/sedes')}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Guardando...' : isEditMode ? 'Actualizar' : 'Crear Sede'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default SedeForm;
