import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import accesosService from '../services/accesosService';
import instalacionesService from '../services/instalacionesService';
import './AccesosMonitor.css';

function AccesosMonitor() {
  const navigate = useNavigate();
  const [accesos, setAccesos] = useState([]);
  const [stats, setStats] = useState({});
  const [sedes, setSedes] = useState([]);
  const [sedeFilter, setSedeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchSedes();
    fetchAccesos();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    fetchAccesos();
    fetchEstadisticas();
  }, [sedeFilter]);

  useEffect(() => {
    let interval;
    if (autoRefresh) {
      // Auto-refrescar cada 10 segundos
      interval = setInterval(() => {
        fetchAccesos();
        fetchEstadisticas();
      }, 10000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, sedeFilter]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchAccesos = async () => {
    try {
      const params = {};
      if (sedeFilter) params.sede = sedeFilter;
      params.limit = 30; // Últimos 30 accesos

      const response = await accesosService.listarRegistros(params);
      setAccesos(response.data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error al cargar accesos:', err);
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const params = {};
      if (sedeFilter) params.sede = sedeFilter;

      const response = await accesosService.getEstadisticas(params);
      setStats(response.data || {});
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const formatHora = (fechaHora) => {
    const fecha = new Date(fechaHora);
    return fecha.toLocaleTimeString('es-MX', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatFechaCompleta = (fechaHora) => {
    const fecha = new Date(fechaHora);
    return fecha.toLocaleString('es-MX', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getEstadoClass = (autorizado) => {
    return autorizado ? 'acceso-autorizado' : 'acceso-denegado';
  };

  const getEstadoIcon = (autorizado) => {
    return autorizado ? '✅' : '❌';
  };

  if (loading) {
    return (
      <div className="accesos-monitor-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando accesos...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="accesos-monitor-container">
      {/* Header */}
      <div className="monitor-header">
        <div>
          <h1>🚪 Monitor de Accesos en Tiempo Real</h1>
          <p className="monitor-subtitle">Visualiza quién está entrando al gimnasio</p>
        </div>
        <div className="header-actions">
          <button
            className={`btn-refresh ${autoRefresh ? 'active' : ''}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
            title={autoRefresh ? 'Auto-refresh activado' : 'Auto-refresh desactivado'}
          >
            {autoRefresh ? '🔄 Auto-refresh ON' : '⏸ Auto-refresh OFF'}
          </button>
          <button
            className="btn-manual-refresh"
            onClick={() => {
              fetchAccesos();
              fetchEstadisticas();
            }}
          >
            🔄 Refrescar
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
            🚪
          </div>
          <div className="stat-content">
            <div className="stat-label">Accesos Hoy</div>
            <div className="stat-value">{stats.accesos_hoy || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            ✅
          </div>
          <div className="stat-content">
            <div className="stat-label">Autorizados</div>
            <div className="stat-value">{stats.autorizados || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
            ❌
          </div>
          <div className="stat-content">
            <div className="stat-label">Denegados</div>
            <div className="stat-value">{stats.denegados || 0}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
            👥
          </div>
          <div className="stat-content">
            <div className="stat-label">Clientes Únicos (Mes)</div>
            <div className="stat-value">{stats.clientes_unicos_mes || 0}</div>
          </div>
        </div>
      </div>

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-group">
          <label>Filtrar por sede:</label>
          <select
            value={sedeFilter}
            onChange={(e) => setSedeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas las sedes</option>
            {sedes.map(sede => (
              <option key={sede.id} value={sede.id}>{sede.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Lista de Accesos */}
      <div className="accesos-section">
        <h2 className="section-title">
          📋 Últimos Accesos ({accesos.length})
        </h2>

        {accesos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🚪</div>
            <p>No hay accesos registrados hoy</p>
            <p className="empty-subtitle">Los accesos aparecerán aquí en tiempo real</p>
          </div>
        ) : (
          <div className="accesos-list">
            {accesos.map((acceso) => (
              <div
                key={acceso.id}
                className={`acceso-item ${getEstadoClass(acceso.autorizado)}`}
              >
                <div className="acceso-status-icon">
                  {getEstadoIcon(acceso.autorizado)}
                </div>

                <div className="acceso-main-info">
                  <div className="acceso-cliente">
                    <div className="cliente-avatar">
                      {acceso.cliente_nombre?.charAt(0) || '?'}
                    </div>
                    <div className="cliente-datos">
                      <h3>{acceso.cliente_nombre || 'Cliente Desconocido'}</h3>
                      {acceso.membresia_nombre && (
                        <p className="membresia-badge">
                          🎫 {acceso.membresia_nombre}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="acceso-detalles">
                    <div className="detalle-item">
                      <span className="detalle-label">🏢 Sede:</span>
                      <span className="detalle-value">{acceso.sede_nombre || 'N/A'}</span>
                    </div>
                    <div className="detalle-item">
                      <span className="detalle-label">🕐 Hora:</span>
                      <span className="detalle-value">{formatHora(acceso.fecha_hora_entrada)}</span>
                    </div>
                    {acceso.membresia_estado && (
                      <div className="detalle-item">
                        <span className="detalle-label">📊 Estado Membresía:</span>
                        <span className={`badge badge-${acceso.membresia_estado}`}>
                          {acceso.membresia_estado}
                        </span>
                      </div>
                    )}
                  </div>

                  {!acceso.autorizado && acceso.motivo_denegado && (
                    <div className="acceso-motivo-denegado">
                      <span className="motivo-icon">⚠️</span>
                      <span className="motivo-text">{acceso.motivo_denegado}</span>
                    </div>
                  )}

                  {acceso.notas && (
                    <div className="acceso-notas">
                      <span className="notas-icon">📝</span>
                      <span className="notas-text">{acceso.notas}</span>
                    </div>
                  )}
                </div>

                <div className="acceso-timestamp">
                  {formatFechaCompleta(acceso.fecha_hora_entrada)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AccesosMonitor;
