import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import horariosService from '../services/horariosService';
import instalacionesService from '../services/instalacionesService';
import './HorariosList.css';

const HorariosList = () => {
  const navigate = useNavigate();
  const [horarios, setHorarios] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [tiposActividad, setTiposActividad] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [sedeFilter, setSedeFilter] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [diaFilter, setDiaFilter] = useState('');
  const [tipoActividadFilter, setTipoActividadFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total_horarios: 0,
    activos: 0,
    por_dia: {},
  });

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
  }, [sedeFilter, estadoFilter, diaFilter, tipoActividadFilter]);

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
      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;
      if (estadoFilter) filtros.estado = estadoFilter;
      if (diaFilter) filtros.dia_semana = diaFilter;
      if (tipoActividadFilter) filtros.tipo_actividad = tipoActividadFilter;
      if (searchTerm) filtros.search = searchTerm;

      const data = await horariosService.getHorarios(filtros);
      setHorarios(Array.isArray(data) ? data : data.results || []);

      // Calcular estadísticas
      calcularEstadisticas(Array.isArray(data) ? data : data.results || []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar horarios:', error);
      setError('Error al cargar horarios');
      setHorarios([]);
    } finally {
      setLoading(false);
    }
  };

  const calcularEstadisticas = (data) => {
    const total = data.length;
    const activos = data.filter((h) => h.estado === 'activo').length;

    const porDia = {};
    DIAS_SEMANA.forEach(({ value }) => {
      porDia[value] = data.filter((h) => h.dia_semana === value).length;
    });

    setEstadisticas({ total_horarios: total, activos, por_dia: porDia });
  };

  const eliminarHorario = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar este horario? Esto eliminará también todas las sesiones asociadas.')) {
      return;
    }

    try {
      await horariosService.deleteHorario(id);
      alert('Horario eliminado exitosamente');
      await cargarHorarios();
    } catch (error) {
      console.error('Error al eliminar horario:', error);
      alert('Error al eliminar el horario: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setSedeFilter('');
    setEstadoFilter('');
    setDiaFilter('');
    setTipoActividadFilter('');
    setSearchTerm('');
  };

  const horariosFiltrados = horarios.filter((horario) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      horario.tipo_actividad_nombre?.toLowerCase().includes(searchLower) ||
      horario.entrenador_nombre?.toLowerCase().includes(searchLower) ||
      horario.espacio_nombre?.toLowerCase().includes(searchLower)
    );
  });

  const formatHora = (hora) => {
    if (!hora) return '';
    return hora.substring(0, 5); // HH:MM
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
    <div className="horarios-list-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2>
            <span className="header-icon">📅</span>
            Gestión de Horarios
          </h2>
          <p className="subtitle">Administra los horarios de clases y actividades del gimnasio</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/horarios/new')}>
          + Nuevo Horario
        </button>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">📊</div>
          <div className="stat-content">
            <h3>{estadisticas.total_horarios}</h3>
            <p>Total de Horarios</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-green">✓</div>
          <div className="stat-content">
            <h3>{estadisticas.activos}</h3>
            <p>Horarios Activos</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-purple">📅</div>
          <div className="stat-content">
            <h3>{Object.values(estadisticas.por_dia).reduce((a, b) => Math.max(a, b), 0)}</h3>
            <p>Día con Más Clases</p>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="filters-card">
        <div className="filters-header">
          <h3>
            <span className="filter-icon">🔍</span>
            Filtros de Búsqueda
          </h3>
          <button className="btn-limpiar" onClick={limpiarFiltros}>
            ✕ Limpiar Filtros
          </button>
        </div>

        <div className="filters-grid">
          <div className="filter-group">
            <label>Buscar</label>
            <input
              type="text"
              placeholder="Actividad, entrenador, espacio..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Sede</label>
            <select value={sedeFilter} onChange={(e) => setSedeFilter(e.target.value)} className="filter-select">
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
            <select value={diaFilter} onChange={(e) => setDiaFilter(e.target.value)} className="filter-select">
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
            <select value={tipoActividadFilter} onChange={(e) => setTipoActividadFilter(e.target.value)} className="filter-select">
              <option value="">Todas las actividades</option>
              {tiposActividad.map((tipo) => (
                <option key={tipo.id} value={tipo.id}>
                  {tipo.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Estado</label>
            <select value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)} className="filter-select">
              <option value="">Todos</option>
              <option value="activo">Activo</option>
              <option value="suspendido">Suspendido</option>
              <option value="cancelado">Cancelado</option>
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

      {/* Tabla de Horarios */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando horarios...</p>
        </div>
      ) : horariosFiltrados.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">📅</div>
          <p>No se encontraron horarios con los filtros seleccionados</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="horarios-table">
            <thead>
              <tr>
                <th>Día</th>
                <th>Actividad</th>
                <th>Horario</th>
                <th>Entrenador</th>
                <th>Espacio</th>
                <th>Sede</th>
                <th>Cupo</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {horariosFiltrados.map((horario) => (
                <tr key={horario.id} className={`horario-row horario-${horario.estado}`}>
                  <td>
                    <span className="badge-dia" style={{ backgroundColor: getDiaColor(horario.dia_semana) }}>
                      {horario.dia_semana?.charAt(0).toUpperCase() + horario.dia_semana?.slice(1)}
                    </span>
                  </td>
                  <td className="actividad-cell">
                    <div className="actividad-nombre">{horario.tipo_actividad_nombre}</div>
                  </td>
                  <td className="horario-cell">
                    <span className="hora-inicio">{formatHora(horario.hora_inicio)}</span>
                    <span className="separador">→</span>
                    <span className="hora-fin">{formatHora(horario.hora_fin)}</span>
                  </td>
                  <td>{horario.entrenador_nombre}</td>
                  <td>{horario.espacio_nombre}</td>
                  <td>
                    <span className="badge-sede">{horario.sede_nombre}</span>
                  </td>
                  <td className="text-center">{horario.cupo_maximo}</td>
                  <td>
                    <span className={`badge-estado badge-${horario.estado}`}>
                      {horario.estado === 'activo' ? '✓ Activo' : horario.estado === 'suspendido' ? '⏸ Suspendido' : '✕ Cancelado'}
                    </span>
                  </td>
                  <td className="acciones-cell">
                    <button className="btn-accion btn-ver" onClick={() => navigate(`/horarios/${horario.id}`)} title="Ver detalle">
                      👁️
                    </button>
                    <button className="btn-accion btn-editar" onClick={() => navigate(`/horarios/edit/${horario.id}`)} title="Editar">
                      ✏️
                    </button>
                    {horario.estado === 'activo' && (
                      <button className="btn-accion btn-eliminar" onClick={() => eliminarHorario(horario.id)} title="Eliminar">
                        🗑️
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default HorariosList;
