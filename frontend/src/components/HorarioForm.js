import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Calendar,
  X,
  Loader,
  ClipboardList,
  AlarmClock,
  Settings,
  Save,
  CheckCircle2,
  ArrowLeft,
} from 'lucide-react';
import horariosService from '../services/horariosService';
import instalacionesService from '../services/instalacionesService';
import ConfirmModal from './ConfirmModal';
import './HorarioForm.css';

const HorarioForm = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Modales de confirmación
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successModalMessage, setSuccessModalMessage] = useState('');
  const [formDataToSubmit, setFormDataToSubmit] = useState(null);

  // Datos del formulario
  const [formData, setFormData] = useState({
    tipo_actividad: '',
    entrenador: '',
    espacio: '',
    dia_semana: '',
    hora_inicio: '',
    hora_fin: '',
    fecha_inicio: '',
    fecha_fin: '',
    cupo_maximo: 20,
    estado: 'activo',
    observaciones: '',
  });

  // Datos para selects
  const [tiposActividad, setTiposActividad] = useState([]);
  const [entrenadores, setEntrenadores] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [sedes, setSedes] = useState([]);

  // Filtros
  const [sedeSeleccionada, setSedeSeleccionada] = useState('');

  const DIAS_SEMANA = [
    { value: 'lunes', label: 'Lunes' },
    { value: 'martes', label: 'Martes' },
    { value: 'miercoles', label: 'Miércoles' },
    { value: 'jueves', label: 'Jueves' },
    { value: 'viernes', label: 'Viernes' },
    { value: 'sabado', label: 'Sábado' },
    { value: 'domingo', label: 'Domingo' },
  ];

  useEffect(() => {
    cargarDatosIniciales();
  }, [id]);

  useEffect(() => {
    if (sedeSeleccionada) {
      cargarEspaciosPorSede(sedeSeleccionada);
      cargarEntrenadoresPorSede(sedeSeleccionada);
      cargarTiposPorSede(sedeSeleccionada);
    }
  }, [sedeSeleccionada]);

  const cargarTiposPorSede = async (sedeId) => {
    try {
      const data = await horariosService.getTiposActividad({ sede: sedeId, activo: true });
      setTiposActividad(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error('Error al cargar tipos de actividad:', error);
      setTiposActividad([]);
    }
  };

  const cargarDatosIniciales = async () => {
    try {
      setLoadingData(true);
      const sedesData = await instalacionesService.getSedes();

      setSedes(Array.isArray(sedesData) ? sedesData : sedesData.data || []);

      // Si estamos editando, cargar el horario
      if (isEdit) {
        const horario = await horariosService.getHorario(id);
        setFormData({
          tipo_actividad: horario.tipo_actividad,
          entrenador: horario.entrenador,
          espacio: horario.espacio,
          dia_semana: horario.dia_semana,
          hora_inicio: horario.hora_inicio,
          hora_fin: horario.hora_fin,
          fecha_inicio: horario.fecha_inicio,
          fecha_fin: horario.fecha_fin || '',
          cupo_maximo: horario.cupo_maximo,
          estado: horario.estado,
          observaciones: horario.observaciones || '',
        });

        // Cargar la sede del espacio
        if (horario.espacio_sede_id) {
          setSedeSeleccionada(horario.espacio_sede_id);
        }
      }
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      setError('Error al cargar los datos del formulario');
    } finally {
      setLoadingData(false);
    }
  };

  const cargarEspaciosPorSede = async (sedeId) => {
    try {
      const data = await horariosService.getEspacios(sedeId);
      setEspacios(Array.isArray(data) ? data : data.data || []);
    } catch (error) {
      console.error('Error al cargar espacios:', error);
      setEspacios([]);
    }
  };

  const cargarEntrenadoresPorSede = async (sedeId) => {
    try {
      const data = await horariosService.getEntrenadores(sedeId);
      setEntrenadores(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error('Error al cargar entrenadores:', error);
      setEntrenadores([]);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      // Validaciones
      if (!sedeSeleccionada) {
        throw new Error('Debe seleccionar una sede');
      }

      if (formData.hora_inicio >= formData.hora_fin) {
        throw new Error('La hora de inicio debe ser anterior a la hora de fin');
      }

      if (formData.fecha_fin && formData.fecha_inicio > formData.fecha_fin) {
        throw new Error('La fecha de inicio debe ser anterior a la fecha de fin');
      }

      const dataToSend = {
        ...formData,
        cupo_maximo: parseInt(formData.cupo_maximo),
        fecha_fin: formData.fecha_fin || null,
      };

      // Guardar los datos y mostrar modal de confirmación
      setFormDataToSubmit(dataToSend);
      if (isEdit) {
        setShowUpdateModal(true);
      } else {
        setShowCreateModal(true);
      }
    } catch (error) {
      console.error('Error en validación:', error);
      setError(error.response?.data?.error || error.message || 'Error al validar el horario');
    }
  };

  const confirmarGuardar = async () => {
    setLoading(true);

    try {
      if (isEdit) {
        await horariosService.updateHorario(id, formDataToSubmit);
        setShowUpdateModal(false);
        setSuccessModalMessage('Horario actualizado exitosamente');
        setShowSuccessModal(true);
      } else {
        await horariosService.createHorario(formDataToSubmit);
        setShowCreateModal(false);
        setSuccessModalMessage('Horario creado exitosamente');
        setShowSuccessModal(true);
      }

      // Navegar después de 1.5 segundos
      setTimeout(() => {
        navigate('/horarios');
      }, 1500);
    } catch (error) {
      console.error('Error al guardar horario:', error);
      setShowCreateModal(false);
      setShowUpdateModal(false);
      setError(error.response?.data?.error || error.message || 'Error al guardar el horario');
    } finally {
      setLoading(false);
    }
  };

  if (loadingData) {
    return (
      <div className="horario-form-container">
        <div className="loading-spinner">
          <span className="spinner"><Loader size={24} /></span>
          <p>Cargando formulario...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="horario-form-container">
      {/* Header */}
      <div className="form-header">
        <div>
          <h2>
            <span className="header-icon"><Calendar size={20} /></span>
            {isEdit ? 'Editar Horario' : 'Nuevo Horario'}
          </h2>
          <p className="subtitle">Complete la información para {isEdit ? 'actualizar' : 'crear'} el horario</p>
        </div>
        <button type="button" className="btn-secondary" onClick={() => navigate('/horarios')}>
          <ArrowLeft size={18} /> Volver
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <span className="alert-icon" onClick={() => setError(null)}>
            <X size={16} />
          </span>
        </div>
      )}

      {/* Success Alert */}
      {successMessage && (
        <div className="alert alert-success">
          <span>{successMessage}</span>
          <span className="alert-icon" onClick={() => setSuccessMessage('')}>
            <X size={16} />
          </span>
        </div>
      )}

      {/* Formulario */}
      <form onSubmit={handleSubmit} className="horario-form">
        {/* Card: Información General */}
        <div className="form-card">
          <div className="card-header">
            <h3><ClipboardList size={18} /> Información General</h3>
          </div>
          <div className="card-body">
            <div className="form-row">
              <div className="form-group">
                <label>
                  Sede *
                  <span className="label-hint">Seleccione primero la sede</span>
                </label>
                <select
                  value={sedeSeleccionada}
                  onChange={(e) => setSedeSeleccionada(e.target.value)}
                  className="form-input"
                  required
                  disabled={isEdit}
                >
                  <option value="">Seleccione una sede</option>
                  {sedes.map((sede) => (
                    <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                      {sede.nombre}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Tipo de Actividad *</label>
                <select
                  name="tipo_actividad"
                  value={formData.tipo_actividad}
                  onChange={handleChange}
                  className="form-input"
                  required
                >
                  <option value="">Seleccione un tipo</option>
                  {tiposActividad.map((tipo) => (
                    <option key={tipo.id} value={tipo.id}>
                      {tipo.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>
                  Espacio *
                  {!sedeSeleccionada && <span className="label-warning">Seleccione una sede primero</span>}
                </label>
                <select
                  name="espacio"
                  value={formData.espacio}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled={!sedeSeleccionada}
                >
                  <option value="">Seleccione un espacio</option>
                  {espacios.map((espacio) => (
                    <option key={espacio.espacio_id || espacio.id} value={espacio.espacio_id || espacio.id}>
                      {espacio.nombre} (Capacidad: {espacio.capacidad})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>
                  Entrenador *
                  {!sedeSeleccionada && <span className="label-warning">Seleccione una sede primero</span>}
                </label>
                <select
                  name="entrenador"
                  value={formData.entrenador}
                  onChange={handleChange}
                  className="form-input"
                  required
                  disabled={!sedeSeleccionada}
                >
                  <option value="">Seleccione un entrenador</option>
                  {entrenadores.map((entrenador) => (
                    <option key={entrenador.id} value={entrenador.id}>
                      {entrenador.nombre_completo || entrenador.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Card: Horario y Fechas */}
        <div className="form-card">
          <div className="card-header">
            <h3><AlarmClock size={18} /> Horario y Fechas</h3>
          </div>
          <div className="card-body">
            <div className="form-row">
              <div className="form-group">
                <label>Día de la Semana *</label>
                <select name="dia_semana" value={formData.dia_semana} onChange={handleChange} className="form-input" required>
                  <option value="">Seleccione un día</option>
                  {DIAS_SEMANA.map(({ value, label }) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Hora Inicio *</label>
                <input
                  type="time"
                  name="hora_inicio"
                  value={formData.hora_inicio}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label>Hora Fin *</label>
                <input
                  type="time"
                  name="hora_fin"
                  value={formData.hora_fin}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Fecha Inicio de Vigencia *</label>
                <input
                  type="date"
                  name="fecha_inicio"
                  value={formData.fecha_inicio}
                  onChange={handleChange}
                  className="form-input"
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  Fecha Fin de Vigencia
                  <span className="label-hint">Opcional - dejar vacío si es indefinido</span>
                </label>
                <input
                  type="date"
                  name="fecha_fin"
                  value={formData.fecha_fin}
                  onChange={handleChange}
                  className="form-input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Card: Configuración Adicional */}
        <div className="form-card">
          <div className="card-header">
            <h3><Settings size={18} /> Configuración Adicional</h3>
          </div>
          <div className="card-body">
            <div className="form-row">
              <div className="form-group">
                <label>Cupo Máximo *</label>
                <input
                  type="number"
                  name="cupo_maximo"
                  value={formData.cupo_maximo}
                  onChange={handleChange}
                  className="form-input"
                  min="1"
                  max="100"
                  required
                />
              </div>

              <div className="form-group">
                <label>Estado *</label>
                <select name="estado" value={formData.estado} onChange={handleChange} className="form-input" required>
                  <option value="activo">Activo</option>
                  <option value="suspendido">Suspendido</option>
                  <option value="cancelado">Cancelado</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Observaciones</label>
              <textarea
                name="observaciones"
                value={formData.observaciones}
                onChange={handleChange}
                className="form-textarea"
                rows="4"
                placeholder="Observaciones adicionales..."
              />
            </div>
          </div>
        </div>

        {/* Botones de Acción */}
        <div className="form-actions">
          <button type="button" className="btn-secondary" onClick={() => navigate('/horarios')} disabled={loading}>
            Cancelar
          </button>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <><Loader size={18} /> Guardando...</>
            ) : isEdit ? (
              <><Save size={18} /> Actualizar Horario</>
            ) : (
              <><CheckCircle2 size={18} /> Crear Horario</>
            )}
          </button>
        </div>
      </form>

      {/* Modal de Confirmación de Creación */}
      <ConfirmModal
        isOpen={showCreateModal}
        onClose={() => {
          setShowCreateModal(false);
          setFormDataToSubmit(null);
        }}
        onConfirm={confirmarGuardar}
        title="Crear Horario"
        message="¿Está seguro de crear este horario con la información proporcionada?"
        confirmText="Crear Horario"
        cancelText="Revisar"
        type="info"
      />

      {/* Modal de Confirmación de Actualización */}
      <ConfirmModal
        isOpen={showUpdateModal}
        onClose={() => {
          setShowUpdateModal(false);
          setFormDataToSubmit(null);
        }}
        onConfirm={confirmarGuardar}
        title="Actualizar Horario"
        message="¿Está seguro de actualizar este horario? Los cambios se aplicarán de inmediato."
        confirmText="Actualizar"
        cancelText="Revisar"
        type="warning"
      />

      {/* Modal de Éxito */}
      <ConfirmModal
        isOpen={showSuccessModal}
        onClose={() => {
          setShowSuccessModal(false);
          navigate('/horarios');
        }}
        onConfirm={() => {
          setShowSuccessModal(false);
          navigate('/horarios');
        }}
        title="Éxito"
        message={successModalMessage}
        confirmText="Aceptar"
        cancelText=""
        type="success"
      />
    </div>
  );
};

export default HorarioForm;
