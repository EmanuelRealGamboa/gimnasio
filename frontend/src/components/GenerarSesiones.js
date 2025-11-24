import React, { useState, useEffect } from 'react';
import horariosService from '../services/horariosService';
import instalacionesService from '../services/instalacionesService';
import './GenerarSesiones.css';

const GenerarSesiones = () => {
  const [horarios, setHorarios] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [tiposActividad, setTiposActividad] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Filtros
  const [sedeFilter, setSedeFilter] = useState('');
  const [diaFilter, setDiaFilter] = useState('');
  const [tipoActividadFilter, setTipoActividadFilter] = useState('');

  // Modal
  const [showModal, setShowModal] = useState(false);
  const [horarioSeleccionado, setHorarioSeleccionado] = useState(null);
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');

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
  }, []);

  useEffect(() => {
    if (sedes.length > 0) {
      cargarHorarios();
    }
  }, [sedeFilter, diaFilter, tipoActividadFilter]);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);
      const [sedesData, tiposData] = await Promise.all([
        instalacionesService.getSedes(),
        horariosService.getTiposActividad(),
      ]);

      setSedes(Array.isArray(sedesData) ? sedesData : sedesData.data || []);
      setTiposActividad(Array.isArray(tiposData) ? tiposData : tiposData.results || []);

      await cargarHorarios();
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      setError('Error al cargar datos. Por favor, recarga la página.');
    } finally {
      setLoading(false);
    }
  };

  const cargarHorarios = async () => {
    try {
      setLoading(true);
      const filtros = { estado: 'activo' }; // Solo horarios activos
      if (sedeFilter) filtros.sede = sedeFilter;
      if (diaFilter) filtros.dia_semana = diaFilter;
      if (tipoActividadFilter) filtros.tipo_actividad = tipoActividadFilter;

      const data = await horariosService.getHorarios(filtros);
      setHorarios(Array.isArray(data) ? data : data.results || []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar horarios:', error);
      setError('Error al cargar horarios');
      setHorarios([]);
    } finally {
      setLoading(false);
    }
  };

  const abrirModal = (horario) => {
    setHorarioSeleccionado(horario);
    const hoy = new Date().toISOString().split('T')[0];
    setFechaInicio(hoy);
    const fechaFinDefault = new Date();
    fechaFinDefault.setDate(fechaFinDefault.getDate() + 30);
    setFechaFin(fechaFinDefault.toISOString().split('T')[0]);
    setShowModal(true);
  };

  const cerrarModal = () => {
    setShowModal(false);
    setHorarioSeleccionado(null);
    setFechaInicio('');
    setFechaFin('');
  };

  const handleGenerarSesiones = async (e) => {
    e.preventDefault();

    if (!fechaInicio || !fechaFin) {
      alert('Por favor, selecciona ambas fechas');
      return;
    }

    if (new Date(fechaInicio) > new Date(fechaFin)) {
      alert('La fecha de inicio debe ser anterior a la fecha de fin');
      return;
    }

    try {
      const resultado = await horariosService.generarSesiones(
        horarioSeleccionado.id,
        fechaInicio,
        fechaFin
      );

      // Mostrar mensaje de éxito con animación
      setSuccessMessage(
        `✓ ${resultado.mensaje || 'Sesiones generadas exitosamente'} - ` +
        `${resultado.sesiones_creadas} sesiones creadas`
      );
      setTimeout(() => setSuccessMessage(''), 4000);

      cerrarModal();
      await cargarHorarios(); // Recargar horarios después de generar sesiones
    } catch (error) {
      console.error('Error al generar sesiones:', error);
      alert('Error al generar sesiones: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setSedeFilter('');
    setDiaFilter('');
    setTipoActividadFilter('');
  };

  const formatHora = (hora) => {
    if (!hora) return '';
    return hora.substring(0, 5);
  };

  const getDiaColor = (dia) => {
    const colores = {
      lunes: '#3b82f6',
      martes: '#10b981',
      miercoles: '#f59e0b',
      jueves: '#8b5cf6',
      viernes: '#ec4899',
      sabado: '#06b6d4',
      domingo: '#ef4444',
    };
    return colores[dia] || '#6b7280';
  };

  return (
    <div className="generar-sesiones-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2>
            <span className="header-icon">🔄</span>
            Generar Sesiones de Clases
          </h2>
          <p className="subtitle">
            Genera sesiones automáticamente para tus horarios en un rango de fechas
          </p>
        </div>
      </div>

      {/* Info Card */}
      <div className="info-card">
        <div className="info-icon-large">ℹ️</div>
        <div className="info-content">
          <h3>¿Cómo funciona?</h3>
          <p>
            1. Selecciona el horario para el cual deseas generar sesiones
            <br />
            2. Elige el rango de fechas (inicio y fin)
            <br />
            3. El sistema creará automáticamente sesiones para todos los días que coincidan con el
            día de la semana del horario
            <br />
            4. Las sesiones generadas estarán disponibles para que los clientes realicen reservas
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="filters-card">
        <div className="filters-header">
          <h3>
            <span className="filter-icon">🔍</span>
            Filtrar Horarios
          </h3>
          <button className="btn-limpiar" onClick={limpiarFiltros}>
            ✕ Limpiar Filtros
          </button>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label>Sede</label>
            <select
              value={sedeFilter}
              onChange={(e) => setSedeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todas las sedes</option>
              {sedes.map((sede) => (
                <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Día de la Semana</label>
            <select
              value={diaFilter}
              onChange={(e) => setDiaFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los días</option>
              {DIAS_SEMANA.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Tipo de Actividad</label>
            <select
              value={tipoActividadFilter}
              onChange={(e) => setTipoActividadFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todas las actividades</option>
              {tiposActividad.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nombre}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Mensajes de Error */}
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon" onClick={() => setError(null)}>
            ✕
          </span>
          {error}
        </div>
      )}

      {/* Mensaje de Éxito */}
      {successMessage && (
        <div className="alert alert-success">
          <span>{successMessage}</span>
          <span className="alert-icon" onClick={() => setSuccessMessage('')}>
            ✕
          </span>
        </div>
      )}

      {/* Lista de Horarios */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando horarios...</p>
        </div>
      ) : horarios.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">📅</div>
          <p>No se encontraron horarios activos con los filtros seleccionados</p>
        </div>
      ) : (
        <div className="horarios-grid">
          {horarios.map((horario) => (
            <div key={horario.id} className="horario-card">
              <div className="horario-card-header">
                <div className="horario-titulo">
                  <h3>{horario.tipo_actividad_nombre}</h3>
                  <span className="badge-sede">{horario.sede_nombre}</span>
                </div>
                <span
                  className="badge-dia"
                  style={{ backgroundColor: getDiaColor(horario.dia_semana) }}
                >
                  {horario.dia_semana?.charAt(0).toUpperCase() + horario.dia_semana?.slice(1)}
                </span>
              </div>

              <div className="horario-card-body">
                <div className="horario-info-row">
                  <span className="info-label">⏰ Horario</span>
                  <span className="info-value">
                    {formatHora(horario.hora_inicio)} - {formatHora(horario.hora_fin)}
                  </span>
                </div>

                <div className="horario-info-row">
                  <span className="info-label">👤 Entrenador</span>
                  <span className="info-value">{horario.entrenador_nombre}</span>
                </div>

                <div className="horario-info-row">
                  <span className="info-label">📍 Espacio</span>
                  <span className="info-value">{horario.espacio_nombre}</span>
                </div>

                <div className="horario-info-row">
                  <span className="info-label">👥 Cupo</span>
                  <span className="info-value">{horario.cupo_maximo} personas</span>
                </div>
              </div>

              <div className="horario-card-footer">
                <button
                  className="btn-generar-principal"
                  onClick={() => abrirModal(horario)}
                >
                  🔄 Generar Sesiones
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Generar Sesiones */}
      {showModal && horarioSeleccionado && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>🔄 Generar Sesiones</h3>
              <button className="modal-close" onClick={cerrarModal}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="horario-info-modal">
                <p>
                  <strong>Actividad:</strong> {horarioSeleccionado.tipo_actividad_nombre}
                </p>
                <p>
                  <strong>Día:</strong>{' '}
                  {horarioSeleccionado.dia_semana?.charAt(0).toUpperCase() +
                    horarioSeleccionado.dia_semana?.slice(1)}
                </p>
                <p>
                  <strong>Horario:</strong> {formatHora(horarioSeleccionado.hora_inicio)} -{' '}
                  {formatHora(horarioSeleccionado.hora_fin)}
                </p>
                <p>
                  <strong>Entrenador:</strong> {horarioSeleccionado.entrenador_nombre}
                </p>
                <p>
                  <strong>Espacio:</strong> {horarioSeleccionado.espacio_nombre}
                </p>
              </div>

              <form onSubmit={handleGenerarSesiones}>
                <div className="form-group">
                  <label>Fecha de Inicio *</label>
                  <input
                    type="date"
                    value={fechaInicio}
                    onChange={(e) => setFechaInicio(e.target.value)}
                    required
                    className="form-input"
                  />
                </div>

                <div className="form-group">
                  <label>Fecha de Fin *</label>
                  <input
                    type="date"
                    value={fechaFin}
                    onChange={(e) => setFechaFin(e.target.value)}
                    required
                    className="form-input"
                  />
                </div>

                <div className="info-message">
                  <span className="info-icon">ℹ️</span>
                  <p>
                    Se crearán sesiones automáticamente para todos los{' '}
                    <strong>
                      {horarioSeleccionado.dia_semana?.charAt(0).toUpperCase() +
                        horarioSeleccionado.dia_semana?.slice(1)}
                    </strong>{' '}
                    entre las fechas seleccionadas.
                  </p>
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn-cancelar" onClick={cerrarModal}>
                    Cancelar
                  </button>
                  <button type="submit" className="btn-primary">
                    🔄 Generar Sesiones
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GenerarSesiones;
