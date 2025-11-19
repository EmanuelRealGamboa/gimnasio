import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import membresiaService from '../services/membresiaService';
import instalacionesService from '../services/instalacionesService';
import './ClienteForm.css'; // Reutilizamos estilos

function MembresiaForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre_plan: '',
    tipo: 'mensual',
    precio: '',
    descripcion: '',
    duracion_dias: '',
    beneficios: '',
    activo: true,
    sede: '',
    espacios_incluidos: [],
    permite_todas_sedes: false
  });

  const [sedes, setSedes] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});

  const tiposMembresia = [
    { value: 'mensual', label: 'Mensual', dias: 30 },
    { value: 'trimestral', label: 'Trimestral', dias: 90 },
    { value: 'semestral', label: 'Semestral', dias: 180 },
    { value: 'anual', label: 'Anual', dias: 365 },
    { value: 'pase_dia', label: 'Pase del Día', dias: 1 },
    { value: 'pase_semana', label: 'Pase Semanal', dias: 7 }
  ];

  useEffect(() => {
    fetchSedes();
    if (isEditMode) {
      fetchMembresia();
    }
  }, [id]);

  useEffect(() => {
    if (formData.sede && !formData.permite_todas_sedes) {
      fetchEspaciosBySede(formData.sede);
    } else {
      setEspacios([]);
    }
  }, [formData.sede, formData.permite_todas_sedes]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchEspaciosBySede = async (sedeId) => {
    try {
      const response = await instalacionesService.getEspaciosBySede(sedeId);
      setEspacios(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar espacios:', err);
    }
  };

  const fetchMembresia = async () => {
    try {
      setLoading(true);
      const response = await membresiaService.getMembresia(id);
      const membresia = response.data;
      setFormData({
        nombre_plan: membresia.nombre_plan || '',
        tipo: membresia.tipo || 'mensual',
        precio: membresia.precio || '',
        descripcion: membresia.descripcion || '',
        duracion_dias: membresia.duracion_dias || '',
        beneficios: membresia.beneficios || '',
        activo: membresia.activo !== undefined ? membresia.activo : true,
        sede: membresia.sede || '',
        espacios_incluidos: membresia.espacios_incluidos || [],
        permite_todas_sedes: membresia.permite_todas_sedes || false
      });
    } catch (err) {
      setError('Error al cargar la membresía');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.nombre_plan.trim()) {
      newErrors.nombre_plan = 'El nombre del plan es requerido';
    }

    if (!formData.precio || formData.precio <= 0) {
      newErrors.precio = 'El precio debe ser mayor a 0';
    }

    if (formData.duracion_dias && formData.duracion_dias <= 0) {
      newErrors.duracion_dias = 'La duración debe ser mayor a 0';
    }

    if (!formData.permite_todas_sedes && !formData.sede) {
      newErrors.sede = 'Debe seleccionar una sede o marcar como membresía multi-sede';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    let newValue = value;
    if (type === 'checkbox') {
      newValue = checked;

      // Si se marca permite_todas_sedes, limpiar sede y espacios
      if (name === 'permite_todas_sedes' && checked) {
        setFormData(prev => ({
          ...prev,
          permite_todas_sedes: true,
          sede: '',
          espacios_incluidos: []
        }));
        return;
      }
    } else if (name === 'tipo') {
      // Auto-completar duración según el tipo
      const tipoSeleccionado = tiposMembresia.find(t => t.value === value);
      if (tipoSeleccionado && !formData.duracion_dias) {
        setFormData(prev => ({
          ...prev,
          tipo: value,
          duracion_dias: tipoSeleccionado.dias
        }));
        return;
      }
    } else if (name === 'sede') {
      // Limpiar espacios al cambiar de sede
      setFormData(prev => ({
        ...prev,
        sede: value,
        espacios_incluidos: []
      }));
      return;
    }

    setFormData(prev => ({
      ...prev,
      [name]: newValue
    }));

    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleEspacioToggle = (espacioId) => {
    setFormData(prev => {
      const isSelected = prev.espacios_incluidos.includes(espacioId);
      return {
        ...prev,
        espacios_incluidos: isSelected
          ? prev.espacios_incluidos.filter(id => id !== espacioId)
          : [...prev.espacios_incluidos, espacioId]
      };
    });
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
        precio: parseFloat(formData.precio),
        duracion_dias: formData.duracion_dias ? parseInt(formData.duracion_dias) : null
      };

      if (isEditMode) {
        await membresiaService.updateMembresia(id, dataToSend);
        showSuccessMessage('Membresía actualizada exitosamente');
      } else {
        await membresiaService.createMembresia(dataToSend);
        showSuccessMessage('Membresía creada exitosamente');
      }

      setTimeout(() => {
        navigate('/membresias');
      }, 1500);
    } catch (err) {
      const errorMessage = err.response?.data?.nombre_plan?.[0] ||
                          err.response?.data?.message ||
                          'Error al guardar la membresía. Por favor, verifica los datos.';
      setError(errorMessage);
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
    return <div className="loading">Cargando membresía...</div>;
  }

  return (
    <div className="cliente-form-container">
      <div className="form-header">
        <h2>{isEditMode ? 'Editar Membresía' : 'Nueva Membresía'}</h2>
        <button
          className="btn-back"
          onClick={() => navigate('/membresias')}
        >
          ← Volver
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="cliente-form">
        <div className="form-section">
          <h3>Información de la Membresía</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nombre_plan">
                Nombre del Plan <span className="required">*</span>
              </label>
              <input
                type="text"
                id="nombre_plan"
                name="nombre_plan"
                value={formData.nombre_plan}
                onChange={handleChange}
                className={errors.nombre_plan ? 'error' : ''}
                placeholder="Ej: Plan Básico, Plan Premium"
              />
              {errors.nombre_plan && <span className="error-text">{errors.nombre_plan}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="tipo">
                Tipo de Membresía <span className="required">*</span>
              </label>
              <select
                id="tipo"
                name="tipo"
                value={formData.tipo}
                onChange={handleChange}
              >
                {tiposMembresia.map(tipo => (
                  <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="precio">
                Precio <span className="required">*</span>
              </label>
              <input
                type="number"
                id="precio"
                name="precio"
                value={formData.precio}
                onChange={handleChange}
                className={errors.precio ? 'error' : ''}
                placeholder="0.00"
                step="0.01"
                min="0"
              />
              {errors.precio && <span className="error-text">{errors.precio}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="duracion_dias">
                Duración (días)
              </label>
              <input
                type="number"
                id="duracion_dias"
                name="duracion_dias"
                value={formData.duracion_dias}
                onChange={handleChange}
                className={errors.duracion_dias ? 'error' : ''}
                placeholder="Número de días"
                min="1"
              />
              {errors.duracion_dias && <span className="error-text">{errors.duracion_dias}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="activo" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  id="activo"
                  name="activo"
                  checked={formData.activo}
                  onChange={handleChange}
                  style={{ width: 'auto', cursor: 'pointer' }}
                />
                Membresía Activa
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="permite_todas_sedes" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  id="permite_todas_sedes"
                  name="permite_todas_sedes"
                  checked={formData.permite_todas_sedes}
                  onChange={handleChange}
                  style={{ width: 'auto', cursor: 'pointer' }}
                />
                Membresía Multi-Sede (Acceso a todas las sedes)
              </label>
            </div>
          </div>

          {!formData.permite_todas_sedes && (
            <>
              <div className="form-group">
                <label htmlFor="sede">
                  Sede {!formData.permite_todas_sedes && <span className="required">*</span>}
                </label>
                <select
                  id="sede"
                  name="sede"
                  value={formData.sede}
                  onChange={handleChange}
                  className={errors.sede ? 'error' : ''}
                >
                  <option value="">Selecciona una sede...</option>
                  {sedes.map((sede) => (
                    <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                  ))}
                </select>
                {errors.sede && <span className="error-text">{errors.sede}</span>}
              </div>

              {formData.sede && espacios.length > 0 && (
                <div className="form-group">
                  <label>Espacios Incluidos (Opcional)</label>
                  <div className="espacios-selector">
                    {espacios.map((espacio) => (
                      <div key={espacio.id} className="espacio-checkbox">
                        <label>
                          <input
                            type="checkbox"
                            checked={formData.espacios_incluidos.includes(espacio.id)}
                            onChange={() => handleEspacioToggle(espacio.id)}
                          />
                          <span>{espacio.nombre}</span>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          <div className="form-group">
            <label htmlFor="descripcion">
              Descripción
            </label>
            <textarea
              id="descripcion"
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              placeholder="Descripción breve del plan (opcional)"
              rows="3"
            />
          </div>

          <div className="form-group">
            <label htmlFor="beneficios">
              Beneficios
            </label>
            <textarea
              id="beneficios"
              name="beneficios"
              value={formData.beneficios}
              onChange={handleChange}
              placeholder="Lista de beneficios incluidos (opcional)&#10;Ejemplo:&#10;- Acceso ilimitado al gimnasio&#10;- Clases grupales&#10;- Asesoría nutricional"
              rows="6"
            />
          </div>
        </div>

        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/membresias')}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar Membresía' : 'Crear Membresía'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default MembresiaForm;
