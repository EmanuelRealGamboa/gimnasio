import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import horariosService from '../services/horariosService';
import instalacionesService from '../services/instalacionesService';
import './TipoActividadForm.css';

const TipoActividadForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [sedes, setSedes] = useState([]);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    duracion_default: '01:00:00',
    duracion_horas: 1, // Campo auxiliar para el selector
    color_hex: '#3b82f6',
    activo: true,
    sede: '',
  });

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      const sedesData = await instalacionesService.getSedes();
      setSedes(Array.isArray(sedesData) ? sedesData : sedesData.data || []);

      if (isEdit) {
        const tipos = await horariosService.getTiposActividad();
        const tiposArray = Array.isArray(tipos) ? tipos : tipos.results || [];
        const tipo = tiposArray.find((t) => t.id === parseInt(id));

        if (tipo) {
          // Extraer horas de duracion_default (formato HH:MM:SS)
          const horas = tipo.duracion_default ? parseInt(tipo.duracion_default.split(':')[0]) : 1;

          setFormData({
            nombre: tipo.nombre,
            descripcion: tipo.descripcion || '',
            duracion_default: tipo.duracion_default || '01:00:00',
            duracion_horas: horas,
            color_hex: tipo.color_hex || '#3b82f6',
            activo: tipo.activo,
            sede: tipo.sede || '',
          });
        }
      }
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setError('Error al cargar los datos');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Convertir duracion_horas a formato HH:MM:SS
      const horas = formData.duracion_horas.toString().padStart(2, '0');
      const duracion_default = `${horas}:00:00`;

      const dataToSend = {
        nombre: formData.nombre,
        descripcion: formData.descripcion,
        duracion_default: duracion_default,
        color_hex: formData.color_hex,
        activo: formData.activo,
        sede: formData.sede || null,
      };

      if (isEdit) {
        await horariosService.updateTipoActividad(id, dataToSend);
        alert('Tipo de actividad actualizado exitosamente');
      } else {
        await horariosService.createTipoActividad(dataToSend);
        alert('Tipo de actividad creado exitosamente');
      }

      navigate('/horarios/tipos-actividad');
    } catch (error) {
      console.error('Error al guardar:', error);
      setError(error.response?.data?.error || error.message || 'Error al guardar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tipo-form-container">
      <div className="form-header">
        <div>
          <h2>
            <span className="header-icon">🏋️</span>
            {isEdit ? 'Editar Tipo de Actividad' : 'Nuevo Tipo de Actividad'}
          </h2>
          <p className="subtitle">Complete la información del tipo de actividad</p>
        </div>
        <button type="button" className="btn-secondary" onClick={() => navigate('/horarios/tipos-actividad')}>
          ← Volver
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <span className="alert-icon" onClick={() => setError(null)}>
            ✕
          </span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="tipo-form">
        <div className="form-card">
          <div className="card-header">
            <h3>📋 Información General</h3>
          </div>
          <div className="card-body">
            <div className="form-row">
              <div className="form-group">
                <label>Nombre de la Actividad *</label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  className="form-input"
                  placeholder="Ej: Yoga, CrossFit, Spinning..."
                  required
                />
              </div>

              <div className="form-group">
                <label>Sede</label>
                <select name="sede" value={formData.sede} onChange={handleChange} className="form-input">
                  <option value="">Global (todas las sedes)</option>
                  {sedes.map((sede) => (
                    <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                      {sede.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Descripción</label>
              <textarea
                name="descripcion"
                value={formData.descripcion}
                onChange={handleChange}
                className="form-textarea"
                rows="3"
                placeholder="Descripción de la actividad..."
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>
                  Duración por Defecto *
                  <span className="label-hint">Selecciona las horas de duración</span>
                </label>
                <select
                  name="duracion_horas"
                  value={formData.duracion_horas}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      duracion_horas: parseInt(e.target.value),
                    })
                  }
                  className="form-input"
                  required
                >
                  <option value="1">1 hora</option>
                  <option value="2">2 horas</option>
                  <option value="3">3 horas</option>
                  <option value="4">4 horas</option>
                  <option value="5">5 horas</option>
                  <option value="6">6 horas</option>
                  <option value="7">7 horas</option>
                  <option value="8">8 horas</option>
                </select>
              </div>

              <div className="form-group">
                <label>Color (para calendario)</label>
                <div className="color-input-group">
                  <input
                    type="color"
                    name="color_hex"
                    value={formData.color_hex}
                    onChange={handleChange}
                    className="color-picker"
                  />
                  <input
                    type="text"
                    name="color_hex"
                    value={formData.color_hex}
                    onChange={handleChange}
                    className="form-input"
                    placeholder="#3b82f6"
                    pattern="^#[0-9A-Fa-f]{6}$"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Estado</label>
                <div className="checkbox-group">
                  <input
                    type="checkbox"
                    name="activo"
                    checked={formData.activo}
                    onChange={handleChange}
                    className="form-checkbox"
                    id="activo-checkbox"
                  />
                  <label htmlFor="activo-checkbox" className="checkbox-label">
                    Actividad activa
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate('/horarios/tipos-actividad')} disabled={loading}>
            Cancelar
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? '⏳ Guardando...' : isEdit ? '💾 Actualizar' : '✅ Crear Actividad'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default TipoActividadForm;
