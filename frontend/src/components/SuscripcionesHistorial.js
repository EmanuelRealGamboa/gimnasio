import React, { useState, useEffect } from 'react';
import suscripcionesService from '../services/suscripcionesService';
import instalacionesService from '../services/instalacionesService';
import './SuscripcionesHistorial.css';

const SuscripcionesHistorial = () => {
  const [suscripciones, setSuscripciones] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [sedeFilter, setSedeFilter] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Paginación
  const [paginaActual, setPaginaActual] = useState(1);
  const suscripcionesPorPagina = 10;

  // Estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total_suscripciones: 0,
    activas: 0,
    vencidas: 0,
    canceladas: 0,
    ingresos_totales: 0,
    ingresos_mes_actual: 0,
    por_sede: []
  });

  // Modal de detalle
  const [suscripcionSeleccionada, setSuscripcionSeleccionada] = useState(null);
  const [mostrarModal, setMostrarModal] = useState(false);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  useEffect(() => {
    if (sedes.length > 0) {
      cargarSuscripciones();
      cargarEstadisticas();
    }
  }, [sedeFilter, estadoFilter]);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);

      const sedesResponse = await instalacionesService.getSedes();
      const sedesData = Array.isArray(sedesResponse) ? sedesResponse : sedesResponse.data;
      setSedes(sedesData || []);

      await cargarSuscripciones();
      await cargarEstadisticas();
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      setError('Error al cargar datos. Por favor, recarga la página.');
      setSedes([]);
    } finally {
      setLoading(false);
    }
  };

  const cargarSuscripciones = async () => {
    try {
      setLoading(true);

      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;
      if (estadoFilter) filtros.estado = estadoFilter;

      const data = await suscripcionesService.getSuscripciones(filtros);
      setSuscripciones(Array.isArray(data) ? data : []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar suscripciones:', error);
      setError('Error al cargar el historial de suscripciones');
      setSuscripciones([]);
    } finally {
      setLoading(false);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;

      const data = await suscripcionesService.getEstadisticas(filtros);
      setEstadisticas(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    }
  };

  const verDetalle = (suscripcion) => {
    setSuscripcionSeleccionada(suscripcion);
    setMostrarModal(true);
  };

  const cerrarModal = () => {
    setMostrarModal(false);
    setSuscripcionSeleccionada(null);
  };

  const cancelarSuscripcion = async (suscripcionId) => {
    if (!window.confirm('¿Está seguro de cancelar esta suscripción?')) {
      return;
    }

    try {
      await suscripcionesService.cancelarSuscripcion(suscripcionId);
      alert('Suscripción cancelada exitosamente');
      await cargarSuscripciones();
      await cargarEstadisticas();
      cerrarModal();
    } catch (error) {
      console.error('Error al cancelar suscripción:', error);
      alert('Error al cancelar la suscripción: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setSedeFilter('');
    setEstadoFilter('');
    setSearchTerm('');
    setPaginaActual(1);
  };

  // Filtrar suscripciones por término de búsqueda
  const suscripcionesFiltradas = suscripciones.filter(suscripcion => {
    if (!searchTerm) return true;

    const searchLower = searchTerm.toLowerCase();
    const clienteNombre = suscripcion.cliente_nombre?.toLowerCase() || '';
    const membresiaNombre = suscripcion.membresia_nombre?.toLowerCase() || '';

    return (
      clienteNombre.includes(searchLower) ||
      membresiaNombre.includes(searchLower) ||
      suscripcion.id?.toString().includes(searchLower)
    );
  });

  // Paginación
  const indexUltimaSuscripcion = paginaActual * suscripcionesPorPagina;
  const indexPrimeraSuscripcion = indexUltimaSuscripcion - suscripcionesPorPagina;
  const suscripcionesActuales = suscripcionesFiltradas.slice(indexPrimeraSuscripcion, indexUltimaSuscripcion);
  const totalPaginas = Math.ceil(suscripcionesFiltradas.length / suscripcionesPorPagina);

  const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatPrecio = (precio) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(precio);
  };

  const getEstadoBadgeClass = (estado) => {
    const clases = {
      'activa': 'badge-activa',
      'vencida': 'badge-vencida',
      'cancelada': 'badge-cancelada'
    };
    return clases[estado] || '';
  };

  const getEstadoTexto = (estado) => {
    const textos = {
      'activa': '✓ Activa',
      'vencida': '⏰ Vencida',
      'cancelada': '✕ Cancelada'
    };
    return textos[estado] || estado;
  };

  return (
    <div className="suscripciones-historial-container">
      {/* Header */}
      <div className="historial-header">
        <div className="header-left">
          <h1>
            <span className="header-icon">💳</span>
            Historial de Suscripciones
          </h1>
          <p className="subtitle">Consulta y gestiona las suscripciones de membresías</p>
        </div>
        <button className="btn-primary" onClick={cargarSuscripciones}>
          🔄 Actualizar
        </button>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">📊</div>
          <div className="stat-content">
            <h3>{estadisticas.total_suscripciones}</h3>
            <p>Total de Suscripciones</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-green">✓</div>
          <div className="stat-content">
            <h3>{estadisticas.activas}</h3>
            <p>Suscripciones Activas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-yellow">⏰</div>
          <div className="stat-content">
            <h3>{estadisticas.vencidas}</h3>
            <p>Suscripciones Vencidas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-purple">💰</div>
          <div className="stat-content">
            <h3>{formatPrecio(estadisticas.ingresos_totales)}</h3>
            <p>Ingresos Totales</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-orange">📅</div>
          <div className="stat-content">
            <h3>{formatPrecio(estadisticas.ingresos_mes_actual)}</h3>
            <p>Ingresos del Mes</p>
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
          {/* Búsqueda general */}
          <div className="filter-group">
            <label>Buscar</label>
            <input
              type="text"
              placeholder="Cliente, membresía, ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="filter-input"
            />
          </div>

          {/* Filtro por sede */}
          <div className="filter-group">
            <label>Sede</label>
            <select
              value={sedeFilter}
              onChange={(e) => setSedeFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todas las sedes</option>
              {sedes.map(sede => (
                <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
          </div>

          {/* Filtro por estado */}
          <div className="filter-group">
            <label>Estado</label>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos</option>
              <option value="activa">Activa</option>
              <option value="vencida">Vencida</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>
        </div>
      </div>

      {/* Mensajes */}
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon" onClick={() => setError(null)}>✕</span>
          {error}
        </div>
      )}

      {/* Tabla de suscripciones */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando suscripciones...</p>
        </div>
      ) : suscripcionesActuales.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">📋</div>
          <p>No se encontraron suscripciones con los filtros seleccionados</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="suscripciones-table">
              <thead>
                <tr>
                  <th>Cliente</th>
                  <th>Membresía</th>
                  <th>Sede</th>
                  <th>Fecha Inicio</th>
                  <th>Fecha Fin</th>
                  <th>Precio</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {suscripcionesActuales.map(suscripcion => (
                  <tr key={suscripcion.id} className={`suscripcion-row suscripcion-${suscripcion.estado}`}>
                    <td>{suscripcion.cliente_nombre || 'N/A'}</td>
                    <td>
                      <div className="membresia-info">
                        <div className="membresia-nombre">{suscripcion.membresia_nombre}</div>
                        <div className="membresia-tipo">{suscripcion.membresia_tipo}</div>
                      </div>
                    </td>
                    <td>
                      {suscripcion.sede_nombre ? (
                        <span className="badge-sede">{suscripcion.sede_nombre}</span>
                      ) : suscripcion.permite_todas_sedes ? (
                        <span className="badge-multisede">⭐ Todas</span>
                      ) : 'N/A'}
                    </td>
                    <td>{formatFecha(suscripcion.fecha_inicio)}</td>
                    <td>{formatFecha(suscripcion.fecha_fin)}</td>
                    <td className="precio-pagado">{formatPrecio(suscripcion.precio_pagado)}</td>
                    <td>
                      <span className={`badge-estado ${getEstadoBadgeClass(suscripcion.estado)}`}>
                        {getEstadoTexto(suscripcion.estado)}
                      </span>
                    </td>
                    <td className="acciones-cell">
                      <button
                        className="btn-accion btn-ver"
                        onClick={() => verDetalle(suscripcion)}
                        title="Ver detalle"
                      >
                        👁️
                      </button>
                      {suscripcion.estado === 'activa' && (
                        <button
                          className="btn-accion btn-cancelar"
                          onClick={() => cancelarSuscripcion(suscripcion.id)}
                          title="Cancelar suscripción"
                        >
                          🚫
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          {totalPaginas > 1 && (
            <div className="pagination">
              <button
                className="btn-pagination"
                onClick={() => setPaginaActual(paginaActual - 1)}
                disabled={paginaActual === 1}
              >
                ← Anterior
              </button>

              <div className="pagination-info">
                Página {paginaActual} de {totalPaginas} ({suscripcionesFiltradas.length} suscripciones)
              </div>

              <button
                className="btn-pagination"
                onClick={() => setPaginaActual(paginaActual + 1)}
                disabled={paginaActual === totalPaginas}
              >
                Siguiente →
              </button>
            </div>
          )}
        </>
      )}

      {/* Modal de Detalle */}
      {mostrarModal && suscripcionSeleccionada && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <span className="modal-icon">📋</span>
                Detalle de Suscripción #{suscripcionSeleccionada.id}
              </h2>
              <button className="btn-cerrar-modal" onClick={cerrarModal}>✕</button>
            </div>

            <div className="modal-body">
              {/* Información del Cliente */}
              <div className="info-section">
                <h3>Información del Cliente</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Nombre:</span>
                    <span className="info-value">{suscripcionSeleccionada.cliente_nombre || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Información de la Membresía */}
              <div className="info-section">
                <h3>Información de la Membresía</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Plan:</span>
                    <span className="info-value">{suscripcionSeleccionada.membresia_nombre}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Tipo:</span>
                    <span className="info-value">{suscripcionSeleccionada.membresia_tipo}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Sede:</span>
                    <span className="info-value">
                      {suscripcionSeleccionada.sede_nombre ||
                       (suscripcionSeleccionada.permite_todas_sedes ? '⭐ Todas las sedes' : 'N/A')}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Estado:</span>
                    <span className={`badge-estado ${getEstadoBadgeClass(suscripcionSeleccionada.estado)}`}>
                      {getEstadoTexto(suscripcionSeleccionada.estado)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Información de Fechas y Pago */}
              <div className="info-section">
                <h3>Fechas y Pago</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Fecha de Suscripción:</span>
                    <span className="info-value">{formatFecha(suscripcionSeleccionada.fecha_suscripcion)}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Fecha de Inicio:</span>
                    <span className="info-value">{formatFecha(suscripcionSeleccionada.fecha_inicio)}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Fecha de Fin:</span>
                    <span className="info-value">{formatFecha(suscripcionSeleccionada.fecha_fin)}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Método de Pago:</span>
                    <span className="info-value">{suscripcionSeleccionada.metodo_pago_display || suscripcionSeleccionada.metodo_pago}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Precio Pagado:</span>
                    <span className="info-value precio-destacado">{formatPrecio(suscripcionSeleccionada.precio_pagado)}</span>
                  </div>
                </div>
              </div>

              {/* Notas */}
              {suscripcionSeleccionada.notas && (
                <div className="info-section">
                  <h3>Notas</h3>
                  <p className="notas-text">{suscripcionSeleccionada.notas}</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              {suscripcionSeleccionada.estado === 'activa' && (
                <button
                  className="btn-cancelar-suscripcion"
                  onClick={() => cancelarSuscripcion(suscripcionSeleccionada.id)}
                >
                  🚫 Cancelar Suscripción
                </button>
              )}
              <button className="btn-cerrar" onClick={cerrarModal}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuscripcionesHistorial;
