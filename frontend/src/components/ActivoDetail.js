import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { activoService } from '../services/gestionEquiposService';
import './ActivoDetail.css';

const ActivoDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activo, setActivo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    cargarActivo();
  }, [id]);

  const cargarActivo = async () => {
    try {
      setLoading(true);
      const response = await activoService.getById(id);
      setActivo(response.data);
      setError(null);
    } catch (error) {
      console.error('Error al cargar activo:', error);
      setError('Error al cargar la información del activo');
    } finally {
      setLoading(false);
    }
  };

  const handleEliminar = async () => {
    if (window.confirm(`¿Estás seguro de eliminar el activo ${activo.codigo}?`)) {
      try {
        await activoService.delete(id);
        alert('Activo eliminado exitosamente');
        navigate('/gestion-equipos/activos');
      } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error al eliminar el activo');
      }
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getEstadoConfig = (estado) => {
    const configs = {
      'activo': { color: '#10b981', icon: '✓', label: 'Activo' },
      'mantenimiento': { color: '#f59e0b', icon: '🔧', label: 'En Mantenimiento' },
      'baja': { color: '#6b7280', icon: '🚫', label: 'Dado de Baja' },
      'inactivo': { color: '#ef4444', icon: '⏸️', label: 'Inactivo' }
    };
    return configs[estado] || configs['inactivo'];
  };

  if (loading) {
    return (
      <div className="activo-detail-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando información del activo...</p>
        </div>
      </div>
    );
  }

  if (error || !activo) {
    return (
      <div className="activo-detail-container">
        <div className="error-state">
          <span className="error-icon">⚠️</span>
          <h2>Error al cargar</h2>
          <p>{error || 'No se pudo encontrar el activo'}</p>
          <Link to="/gestion-equipos/activos" className="btn-back">
            ← Volver al listado
          </Link>
        </div>
      </div>
    );
  }

  const estadoConfig = getEstadoConfig(activo.estado);

  return (
    <div className="activo-detail-container">
      {/* Header con navegación */}
      <div className="detail-header">
        <Link to="/gestion-equipos/activos" className="btn-back-simple">
          ← Volver
        </Link>
        <div className="detail-actions">
          <Link
            to={`/gestion-equipos/activos/edit/${activo.activo_id}`}
            className="btn-edit"
          >
            ✏️ Editar
          </Link>
          <button onClick={handleEliminar} className="btn-delete">
            🗑️ Eliminar
          </button>
        </div>
      </div>

      {/* Hero Section con imagen */}
      <div className="detail-hero">
        <div className="hero-image">
          {activo.imagen ? (
            <img
              src={activo.imagen.startsWith('http') ? activo.imagen : `https://carefree-fulfillment-production.up.railway.app${activo.imagen}`}
              alt={activo.nombre}
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = 'https://via.placeholder.com/800x500/1e293b/60a5fa?text=Sin+Imagen';
              }}
            />
          ) : (
            <div className="hero-placeholder">
              <span className="placeholder-icon-large">
                {activo.categoria?.nombre?.includes('Cardiovascular') ? '🏃' :
                 activo.categoria?.nombre?.includes('Fuerza') ? '💪' :
                 activo.categoria?.nombre?.includes('Pesas') ? '🏋️' :
                 activo.categoria?.nombre?.includes('Funcional') ? '🤸' :
                 activo.categoria?.nombre?.includes('Mobiliario') ? '🪑' : '📦'}
              </span>
              <span className="placeholder-text-large">Sin Imagen</span>
            </div>
          )}
        </div>

        <div className="hero-info">
          <div className="hero-badge">
            <span className="badge-codigo">{activo.codigo}</span>
            <span
              className="badge-estado-detail"
              style={{ backgroundColor: estadoConfig.color }}
            >
              {estadoConfig.icon} {estadoConfig.label}
            </span>
          </div>
          <h1 className="hero-title">{activo.nombre}</h1>
          {activo.descripcion && (
            <p className="hero-description">{activo.descripcion}</p>
          )}
        </div>
      </div>

      {/* Información principal en grid */}
      <div className="detail-grid">
        {/* Información General */}
        <div className="detail-section">
          <h2 className="section-title">📋 Información General</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Código</span>
              <span className="info-value">{activo.codigo}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Nombre</span>
              <span className="info-value">{activo.nombre}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Categoría</span>
              <span className="info-value">
                {activo.categoria?.nombre || 'Sin categoría'}
              </span>
            </div>
            <div className="info-item">
              <span className="info-label">Estado</span>
              <span className="info-value">
                <span
                  className="status-badge"
                  style={{ backgroundColor: estadoConfig.color }}
                >
                  {estadoConfig.icon} {estadoConfig.label}
                </span>
              </span>
            </div>
          </div>
        </div>

        {/* Información de Compra */}
        <div className="detail-section">
          <h2 className="section-title">💰 Información de Compra</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Fecha de Compra</span>
              <span className="info-value">{formatDate(activo.fecha_compra)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Valor</span>
              <span className="info-value highlight">{formatCurrency(activo.valor)}</span>
            </div>
          </div>
        </div>

        {/* Detalles Técnicos */}
        <div className="detail-section">
          <h2 className="section-title">🔧 Detalles Técnicos</h2>
          <div className="info-grid">
            {activo.marca && (
              <div className="info-item">
                <span className="info-label">Marca</span>
                <span className="info-value">{activo.marca}</span>
              </div>
            )}
            {activo.modelo && (
              <div className="info-item">
                <span className="info-label">Modelo</span>
                <span className="info-value">{activo.modelo}</span>
              </div>
            )}
            {activo.numero_serie && (
              <div className="info-item">
                <span className="info-label">Número de Serie</span>
                <span className="info-value mono">{activo.numero_serie}</span>
              </div>
            )}
          </div>
        </div>

        {/* Ubicación */}
        <div className="detail-section">
          <h2 className="section-title">📍 Ubicación</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Sede</span>
              <span className="info-value">{activo.sede?.nombre || 'Sin sede'}</span>
            </div>
            {activo.espacio?.nombre && (
              <div className="info-item">
                <span className="info-label">Espacio</span>
                <span className="info-value">{activo.espacio.nombre}</span>
              </div>
            )}
            {activo.ubicacion && (
              <div className="info-item full-width">
                <span className="info-label">Ubicación Específica</span>
                <span className="info-value">{activo.ubicacion}</span>
              </div>
            )}
          </div>
        </div>

        {/* Historial de Mantenimientos */}
        {activo.historial_mantenimientos && activo.historial_mantenimientos.length > 0 && (
          <div className="detail-section full-width">
            <h2 className="section-title">🔧 Historial de Mantenimientos</h2>
            <div className="mantenimiento-list">
              {activo.historial_mantenimientos.map((mant, index) => (
                <div key={index} className="mantenimiento-item">
                  <div className="mantenimiento-header">
                    <span className={`mantenimiento-tipo ${mant.tipo_mantenimiento}`}>
                      {mant.tipo_mantenimiento === 'preventivo' ? '🛡️' : '🔧'} {mant.tipo_display}
                    </span>
                    <span className={`mantenimiento-estado ${mant.estado}`}>
                      {mant.estado_display}
                    </span>
                  </div>
                  <div className="mantenimiento-dates">
                    <span>📅 Programado: {formatDate(mant.fecha_programada)}</span>
                    {mant.fecha_ejecucion && (
                      <span>✓ Ejecutado: {formatDate(mant.fecha_ejecucion)}</span>
                    )}
                  </div>
                  {mant.descripcion && (
                    <p className="mantenimiento-description">{mant.descripcion}</p>
                  )}
                  {mant.costo > 0 && (
                    <div className="mantenimiento-cost">
                      Costo: {formatCurrency(mant.costo)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Estadísticas de Mantenimientos */}
        {activo.estadisticas && (
          <div className="detail-section full-width">
            <h2 className="section-title">📊 Estadísticas de Mantenimientos</h2>
            <div className="stats-grid-detail">
              <div className="stat-box">
                <span className="stat-number">{activo.estadisticas.total_mantenimientos}</span>
                <span className="stat-label">Total</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">{activo.estadisticas.completados}</span>
                <span className="stat-label">Completados</span>
              </div>
              <div className="stat-box">
                <span className="stat-number">{formatCurrency(activo.estadisticas.costo_total)}</span>
                <span className="stat-label">Costo Total</span>
              </div>
              {activo.estadisticas.ultimo_mantenimiento && (
                <div className="stat-box">
                  <span className="stat-number">{formatDate(activo.estadisticas.ultimo_mantenimiento)}</span>
                  <span className="stat-label">Último Mantenimiento</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Auditoría */}
        <div className="detail-section full-width">
          <h2 className="section-title">👤 Información de Auditoría</h2>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Creado por</span>
              <span className="info-value">{activo.creado_por_email || 'Sistema'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Fecha de Creación</span>
              <span className="info-value">{formatDate(activo.fecha_creacion)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Última Actualización</span>
              <span className="info-value">{formatDate(activo.fecha_actualizacion)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Botones de acción al final */}
      <div className="detail-footer-actions">
        <Link
          to={`/gestion-equipos/activos/edit/${activo.activo_id}`}
          className="btn-primary-large"
        >
          ✏️ Editar Activo
        </Link>
        <Link
          to="/gestion-equipos/mantenimientos"
          className="btn-secondary-large"
        >
          🔧 Programar Mantenimiento
        </Link>
        <Link
          to="/gestion-equipos/activos"
          className="btn-secondary-large"
        >
          ← Volver al Listado
        </Link>
      </div>
    </div>
  );
};

export default ActivoDetail;
