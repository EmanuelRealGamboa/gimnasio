import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { mantenimientoService } from '../services/gestionEquiposService';
import './GestionEquipos.css';

const MantenimientoList = () => {
  const [searchParams] = useSearchParams();
  const filterParam = searchParams.get('filter');

  const [mantenimientos, setMantenimientos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState({
    search: '',
    tipo_mantenimiento: '',
    estado: filterParam === 'vencidos' ? 'pendiente' : '',
    filter: filterParam || '',
  });

  useEffect(() => {
    cargarMantenimientos();
  }, [filtros]);

  const cargarMantenimientos = async () => {
    try {
      setLoading(true);
      let response;

      // Cargar según filtro especial
      if (filtros.filter === 'vencidos') {
        response = await mantenimientoService.getVencidos();
      } else if (filtros.filter === 'alertas') {
        response = await mantenimientoService.getAlertas();
      } else {
        // Aplicar filtros normales
        const params = {};
        if (filtros.search) params.search = filtros.search;
        if (filtros.tipo_mantenimiento) params.tipo_mantenimiento = filtros.tipo_mantenimiento;
        if (filtros.estado) params.estado = filtros.estado;

        response = await mantenimientoService.getAll(params);
      }

      setMantenimientos(response.data);
    } catch (error) {
      console.error('Error al cargar mantenimientos:', error);
      alert('Error al cargar los mantenimientos');
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

  const handleIniciar = async (id) => {
    if (window.confirm('¿Iniciar este mantenimiento?')) {
      try {
        await mantenimientoService.iniciar(id);
        showSuccessMessage('Mantenimiento iniciado exitosamente');
        cargarMantenimientos();
      } catch (error) {
        console.error('Error al iniciar:', error);
        alert(error.response?.data?.error || 'Error al iniciar el mantenimiento');
      }
    }
  };

  const handleCompletar = async (id) => {
    const fechaEjecucion = prompt('Fecha de ejecución (YYYY-MM-DD):', new Date().toISOString().split('T')[0]);
    if (!fechaEjecucion) return;

    const observaciones = prompt('Observaciones:', '');
    const costo = prompt('Costo final (opcional):', '');

    try {
      const data = {
        fecha_ejecucion: fechaEjecucion,
        observaciones: observaciones || '',
      };
      if (costo) data.costo = parseFloat(costo);

      await mantenimientoService.completar(id, data);
      showSuccessMessage('Mantenimiento completado exitosamente');
      cargarMantenimientos();
    } catch (error) {
      console.error('Error al completar:', error);
      alert('Error al completar el mantenimiento');
    }
  };

  const handleCancelar = async (id) => {
    const motivo = prompt('Motivo de cancelación:');
    if (!motivo) return;

    try {
      await mantenimientoService.cancelar(id, motivo);
      showSuccessMessage('Mantenimiento cancelado');
      cargarMantenimientos();
    } catch (error) {
      console.error('Error al cancelar:', error);
      alert('Error al cancelar el mantenimiento');
    }
  };

  const handleEliminar = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este mantenimiento?')) {
      try {
        await mantenimientoService.delete(id);
        showSuccessMessage('Mantenimiento eliminado exitosamente');
        cargarMantenimientos();
      } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error al eliminar el mantenimiento');
      }
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const getEstadoColor = (estado) => {
    const colors = {
      'pendiente': '#f59e0b',
      'en_proceso': '#3b82f6',
      'completado': '#10b981',
      'cancelado': '#6b7280'
    };
    return colors[estado] || '#6b7280';
  };

  const getTipoIcon = (tipo) => {
    return tipo === 'preventivo' ? '🛡️' : '🔧';
  };

  const getEstadoIcon = (estado) => {
    const icons = {
      'pendiente': '⏳',
      'en_proceso': '🔄',
      'completado': '✅',
      'cancelado': '❌'
    };
    return icons[estado] || '📋';
  };

  const getDiasLabel = (dias) => {
    if (dias === null) return null;

    if (dias < 0) {
      return {
        text: `Vencido hace ${Math.abs(dias)} días`,
        color: '#ef4444',
        icon: '🚨'
      };
    } else if (dias === 0) {
      return {
        text: 'Hoy',
        color: '#f59e0b',
        icon: '⚠️'
      };
    } else if (dias <= 7) {
      return {
        text: `En ${dias} día${dias > 1 ? 's' : ''}`,
        color: '#f59e0b',
        icon: '⚠️'
      };
    } else {
      return {
        text: `En ${dias} días`,
        color: '#3b82f6',
        icon: '📅'
      };
    }
  };

  return (
    <div className="activo-list-container">
      <div className="header">
        <div>
          <h1>Gestión de Mantenimientos</h1>
          <p className="subtitle">
            {filtros.filter === 'vencidos' && '🚨 Mantenimientos vencidos - Requieren atención inmediata'}
            {filtros.filter === 'alertas' && '⚠️ Mantenimientos próximos (15 días)'}
            {!filtros.filter && 'Programación y seguimiento de mantenimientos de equipos'}
          </p>
        </div>
        <Link to="/gestion-equipos/mantenimientos/new" className="btn btn-primary">
          + Nuevo Mantenimiento
        </Link>
      </div>

      {/* Filtros Mejorados */}
      <div className="filters-section">
        <div className="filter-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por activo o descripción..."
            value={filtros.search}
            onChange={(e) => setFiltros({ ...filtros, search: e.target.value })}
            className="search-input"
          />
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">🏷️</span>
              Tipo
            </label>
            <select
              value={filtros.tipo_mantenimiento}
              onChange={(e) => setFiltros({ ...filtros, tipo_mantenimiento: e.target.value })}
              className="filter-select"
            >
              <option value="">Todos los tipos</option>
              <option value="preventivo">🛡️ Preventivo</option>
              <option value="correctivo">🔧 Correctivo</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">🔄</span>
              Estado
            </label>
            <select
              value={filtros.estado}
              onChange={(e) => setFiltros({ ...filtros, estado: e.target.value, filter: '' })}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="pendiente">⏳ Pendiente</option>
              <option value="en_proceso">🔄 En Proceso</option>
              <option value="completado">✅ Completado</option>
              <option value="cancelado">❌ Cancelado</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">⚡</span>
              Filtros Especiales
            </label>
            <select
              value={filtros.filter}
              onChange={(e) => setFiltros({ ...filtros, filter: e.target.value, estado: '' })}
              className="filter-select"
            >
              <option value="">Ninguno</option>
              <option value="alertas">⚠️ Próximos (15 días)</option>
              <option value="vencidos">🚨 Vencidos</option>
            </select>
          </div>

          <button
            onClick={() => setFiltros({ search: '', tipo_mantenimiento: '', estado: '', filter: '' })}
            className="btn-clear-filters"
          >
            <span className="clear-icon">✕</span>
            Limpiar filtros
          </button>
        </div>
      </div>

      {/* Cards de Mantenimientos */}
      {loading ? (
        <div className="loading">Cargando mantenimientos...</div>
      ) : mantenimientos.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🔧</div>
          <h3>No se encontraron mantenimientos</h3>
          <p>Comienza creando el primer mantenimiento para tus equipos</p>
          <Link to="/gestion-equipos/mantenimientos/new" className="btn btn-primary">
            + Crear primer mantenimiento
          </Link>
        </div>
      ) : (
        <>
          <div className="mantenimientos-grid">
            {mantenimientos.map(mant => {
              const diasLabel = getDiasLabel(mant.dias_para_mantenimiento);

              return (
                <div key={mant.mantenimiento_id} className="mantenimiento-card">
                  {/* Header de la card */}
                  <div className="mantenimiento-card-header">
                    <div className="mantenimiento-tipo">
                      <span className="tipo-icon">{getTipoIcon(mant.tipo_mantenimiento)}</span>
                      <span className="tipo-text">{mant.tipo_display}</span>
                    </div>
                    <div
                      className="mantenimiento-estado"
                      style={{ backgroundColor: getEstadoColor(mant.estado) }}
                    >
                      <span>{getEstadoIcon(mant.estado)}</span>
                      <span>{mant.estado_display}</span>
                    </div>
                  </div>

                  {/* Información del activo */}
                  <div className="mantenimiento-activo">
                    <div className="activo-icon">📦</div>
                    <div className="activo-info">
                      <div className="activo-codigo">{mant.activo_codigo}</div>
                      <div className="activo-nombre">{mant.activo_nombre}</div>
                    </div>
                  </div>

                  {/* Detalles */}
                  <div className="mantenimiento-detalles">
                    <div className="detalle-item">
                      <span className="detalle-icon">📅</span>
                      <div className="detalle-content">
                        <span className="detalle-label">Fecha Programada</span>
                        <span className="detalle-value">
                          {new Date(mant.fecha_programada).toLocaleDateString('es-MX', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric'
                          })}
                        </span>
                      </div>
                    </div>

                    {mant.fecha_ejecucion && (
                      <div className="detalle-item">
                        <span className="detalle-icon">✓</span>
                        <div className="detalle-content">
                          <span className="detalle-label">Fecha Ejecución</span>
                          <span className="detalle-value">
                            {new Date(mant.fecha_ejecucion).toLocaleDateString('es-MX', {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric'
                            })}
                          </span>
                        </div>
                      </div>
                    )}

                    {mant.responsable && (
                      <div className="detalle-item">
                        <span className="detalle-icon">
                          {mant.responsable.tipo === 'externo' ? '🏢' : '👤'}
                        </span>
                        <div className="detalle-content">
                          <span className="detalle-label">Responsable</span>
                          <span className="detalle-value">{mant.responsable.nombre}</span>
                        </div>
                      </div>
                    )}

                    <div className="detalle-item">
                      <span className="detalle-icon">💵</span>
                      <div className="detalle-content">
                        <span className="detalle-label">Costo</span>
                        <span className="detalle-value detalle-costo">{formatCurrency(mant.costo)}</span>
                      </div>
                    </div>

                    {diasLabel && (
                      <div className="detalle-item detalle-dias">
                        <div
                          className="dias-badge"
                          style={{
                            backgroundColor: diasLabel.color,
                            color: '#fff'
                          }}
                        >
                          <span>{diasLabel.icon}</span>
                          <span>{diasLabel.text}</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Acciones */}
                  <div className="mantenimiento-actions">
                    <Link
                      to={`/gestion-equipos/mantenimientos/${mant.mantenimiento_id}`}
                      className="btn-action btn-action-view"
                      title="Ver detalles"
                    >
                      <span className="action-icon">👁️</span>
                      <span className="action-text">Ver Detalles</span>
                    </Link>

                    {mant.estado === 'pendiente' && (
                      <>
                        <button
                          onClick={() => handleIniciar(mant.mantenimiento_id)}
                          className="btn-action btn-action-start"
                          title="Iniciar mantenimiento"
                        >
                          <span className="action-icon">▶️</span>
                          <span className="action-text">Iniciar</span>
                        </button>
                        <Link
                          to={`/gestion-equipos/mantenimientos/edit/${mant.mantenimiento_id}`}
                          className="btn-action btn-action-edit"
                          title="Editar"
                        >
                          <span className="action-icon">✏️</span>
                          <span className="action-text">Editar</span>
                        </Link>
                      </>
                    )}

                    {mant.estado === 'en_proceso' && (
                      <button
                        onClick={() => handleCompletar(mant.mantenimiento_id)}
                        className="btn-action btn-action-complete"
                        title="Completar"
                      >
                        <span className="action-icon">✅</span>
                        <span className="action-text">Completar</span>
                      </button>
                    )}

                    {(mant.estado === 'pendiente' || mant.estado === 'en_proceso') && (
                      <button
                        onClick={() => handleCancelar(mant.mantenimiento_id)}
                        className="btn-action btn-action-cancel"
                        title="Cancelar"
                      >
                        <span className="action-icon">❌</span>
                        <span className="action-text">Cancelar</span>
                      </button>
                    )}

                    <button
                      onClick={() => handleEliminar(mant.mantenimiento_id)}
                      className="btn-action btn-action-delete"
                      title="Eliminar"
                    >
                      <span className="action-icon">🗑️</span>
                      <span className="action-text">Eliminar</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="footer-info">
            <p>
              <span className="footer-icon">📊</span>
              Total de mantenimientos: <strong>{mantenimientos.length}</strong>
            </p>
          </div>
        </>
      )}

      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Link to="/gestion-equipos" className="btn-back-to-dashboard">
          ← Volver al Dashboard
        </Link>
      </div>
    </div>
  );
};

export default MantenimientoList;
