import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import horariosService from '../services/horariosService';
import instalacionesService from '../services/instalacionesService';
import './TipoActividadList.css';

const TipoActividadList = () => {
  const navigate = useNavigate();
  const [tiposActividad, setTiposActividad] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [sedeFilter, setSedeFilter] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total: 0,
    activos: 0,
    inactivos: 0,
  });

  useEffect(() => {
    cargarDatos();
  }, [sedeFilter, estadoFilter]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;
      if (estadoFilter) filtros.activo = estadoFilter === 'true';

      const [tiposData, sedesData] = await Promise.all([
        horariosService.getTiposActividad(filtros),
        instalacionesService.getSedes(),
      ]);

      const tipos = Array.isArray(tiposData) ? tiposData : tiposData.results || [];
      setTiposActividad(tipos);
      setSedes(Array.isArray(sedesData) ? sedesData : sedesData.data || []);

      // Calcular estadísticas
      setEstadisticas({
        total: tipos.length,
        activos: tipos.filter((t) => t.activo).length,
        inactivos: tipos.filter((t) => !t.activo).length,
      });

      setError(null);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setError('Error al cargar los tipos de actividad');
    } finally {
      setLoading(false);
    }
  };

  const eliminarTipo = async (id) => {
    if (!window.confirm('¿Está seguro de eliminar este tipo de actividad?')) {
      return;
    }

    try {
      await horariosService.deleteTipoActividad(id);
      alert('Tipo de actividad eliminado exitosamente');
      await cargarDatos();
    } catch (error) {
      console.error('Error al eliminar:', error);
      alert('Error al eliminar: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setSedeFilter('');
    setEstadoFilter('');
    setSearchTerm('');
  };

  const tiposFiltrados = tiposActividad.filter((tipo) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      tipo.nombre?.toLowerCase().includes(searchLower) ||
      tipo.descripcion?.toLowerCase().includes(searchLower)
    );
  });

  const formatDuracion = (duracion) => {
    if (!duracion) return '';
    // Formato HH:MM:SS viene del backend
    const parts = duracion.split(':');
    const horas = parseInt(parts[0]);
    const minutos = parseInt(parts[1]);

    if (horas > 0) {
      return `${horas}h ${minutos}m`;
    }
    return `${minutos} min`;
  };

  return (
    <div className="tipo-actividad-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2>
            <span className="header-icon">🏋️</span>
            Tipos de Actividad
          </h2>
          <p className="subtitle">Gestiona los tipos de actividades disponibles en cada sede</p>
        </div>
        <button className="btn-primary" onClick={() => navigate('/horarios/tipos-actividad/new')}>
          + Nueva Actividad
        </button>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">📊</div>
          <div className="stat-content">
            <h3>{estadisticas.total}</h3>
            <p>Total Actividades</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-green">✓</div>
          <div className="stat-content">
            <h3>{estadisticas.activos}</h3>
            <p>Activas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-red">✕</div>
          <div className="stat-content">
            <h3>{estadisticas.inactivos}</h3>
            <p>Inactivas</p>
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
              placeholder="Nombre, descripción..."
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
            <label>Estado</label>
            <select value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)} className="filter-select">
              <option value="">Todos</option>
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <span className="alert-icon" onClick={() => setError(null)}>
            ✕
          </span>
        </div>
      )}

      {/* Tabla */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando tipos de actividad...</p>
        </div>
      ) : tiposFiltrados.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">🏋️</div>
          <p>No se encontraron tipos de actividad</p>
        </div>
      ) : (
        <div className="table-container">
          <table className="tipos-table">
            <thead>
              <tr>
                <th>Actividad</th>
                <th>Descripción</th>
                <th>Duración</th>
                <th>Sede</th>
                <th>Color</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {tiposFiltrados.map((tipo) => (
                <tr key={tipo.id} className={`tipo-row ${!tipo.activo ? 'tipo-inactivo' : ''}`}>
                  <td className="actividad-cell">
                    <div className="actividad-nombre">{tipo.nombre}</div>
                  </td>
                  <td className="descripcion-cell">
                    {tipo.descripcion ? tipo.descripcion.substring(0, 80) + (tipo.descripcion.length > 80 ? '...' : '') : '-'}
                  </td>
                  <td>
                    <span className="badge-duracion">{tipo.duracion_texto || formatDuracion(tipo.duracion_default)}</span>
                  </td>
                  <td>
                    {tipo.sede_nombre ? (
                      <span className="badge-sede">{tipo.sede_nombre}</span>
                    ) : (
                      <span className="badge-global">Global</span>
                    )}
                  </td>
                  <td>
                    <div className="color-preview" style={{ backgroundColor: tipo.color_hex }}>
                      <span className="color-hex">{tipo.color_hex}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge-estado ${tipo.activo ? 'badge-activo' : 'badge-inactivo'}`}>
                      {tipo.activo ? '✓ Activo' : '✕ Inactivo'}
                    </span>
                  </td>
                  <td className="acciones-cell">
                    <button
                      className="btn-accion btn-editar"
                      onClick={() => navigate(`/horarios/tipos-actividad/edit/${tipo.id}`)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button className="btn-accion btn-eliminar" onClick={() => eliminarTipo(tipo.id)} title="Eliminar">
                      🗑️
                    </button>
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

export default TipoActividadList;
