import React, { useState, useEffect } from 'react';
import ventasService from '../services/ventasService';
import instalacionesService from '../services/instalacionesService';
import './VentasHistorial.css';

const VentasHistorial = () => {
  const [ventas, setVentas] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filtros
  const [sedeFilter, setSedeFilter] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [fechaDesde, setFechaDesde] = useState('');
  const [fechaHasta, setFechaHasta] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Paginación
  const [paginaActual, setPaginaActual] = useState(1);
  const ventasPorPagina = 10;

  // Estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total_ventas: 0,
    ingresos_totales: 0,
    ticket_promedio: 0
  });

  // Modal de detalle
  const [ventaSeleccionada, setVentaSeleccionada] = useState(null);
  const [mostrarModal, setMostrarModal] = useState(false);

  useEffect(() => {
    cargarDatosIniciales();
  }, []);

  useEffect(() => {
    if (sedes.length > 0) {
      cargarVentas();
      cargarEstadisticas();
    }
  }, [sedeFilter, estadoFilter, fechaDesde, fechaHasta]);

  const cargarDatosIniciales = async () => {
    try {
      setLoading(true);
      const sedesResponse = await instalacionesService.getSedes();
      // El servicio devuelve el objeto response, necesitamos .data
      const sedesData = Array.isArray(sedesResponse) ? sedesResponse : sedesResponse.data;
      setSedes(sedesData || []);

      // Cargar ventas después de tener las sedes
      await cargarVentas();
      await cargarEstadisticas();
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      setError('Error al cargar datos. Por favor, recarga la página.');
      setSedes([]); // Asegurar que sea un array
    } finally {
      setLoading(false);
    }
  };

  const cargarVentas = async () => {
    try {
      setLoading(true);

      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;
      if (estadoFilter) filtros.estado = estadoFilter;
      if (fechaDesde) filtros.fecha_desde = fechaDesde;
      if (fechaHasta) filtros.fecha_hasta = fechaHasta;

      const data = await ventasService.getVentas(filtros);
      setVentas(Array.isArray(data) ? data : []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar ventas:', error);
      setError('Error al cargar el historial de ventas');
      setVentas([]); // Asegurar que sea un array
    } finally {
      setLoading(false);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      const filtros = {};
      if (sedeFilter) filtros.sede = sedeFilter;
      if (fechaDesde) filtros.fecha_desde = fechaDesde;
      if (fechaHasta) filtros.fecha_hasta = fechaHasta;

      const data = await ventasService.getEstadisticas(filtros);
      setEstadisticas(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    }
  };

  const verDetalle = (venta) => {
    setVentaSeleccionada(venta);
    setMostrarModal(true);
  };

  const cerrarModal = () => {
    setMostrarModal(false);
    setVentaSeleccionada(null);
  };

  const cancelarVenta = async (ventaId) => {
    if (!window.confirm('¿Está seguro de cancelar esta venta? Se restaurará el stock de los productos.')) {
      return;
    }

    try {
      await ventasService.cancelarVenta(ventaId);
      alert('Venta cancelada exitosamente');
      await cargarVentas();
      await cargarEstadisticas();
      cerrarModal();
    } catch (error) {
      console.error('Error al cancelar venta:', error);
      alert('Error al cancelar la venta: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setSedeFilter('');
    setEstadoFilter('');
    setFechaDesde('');
    setFechaHasta('');
    setSearchTerm('');
    setPaginaActual(1);
  };

  // Filtrar ventas por término de búsqueda
  const ventasFiltradas = ventas.filter(venta => {
    if (!searchTerm) return true;

    const searchLower = searchTerm.toLowerCase();
    return (
      venta.venta_id?.toString().includes(searchLower) ||
      venta.cliente_nombre?.toLowerCase().includes(searchLower) ||
      venta.sede_nombre?.toLowerCase().includes(searchLower) ||
      venta.empleado_nombre?.toLowerCase().includes(searchLower)
    );
  });

  // Paginación
  const indexUltimaVenta = paginaActual * ventasPorPagina;
  const indexPrimeraVenta = indexUltimaVenta - ventasPorPagina;
  const ventasActuales = ventasFiltradas.slice(indexPrimeraVenta, indexUltimaVenta);
  const totalPaginas = Math.ceil(ventasFiltradas.length / ventasPorPagina);

  const formatFecha = (fecha) => {
    return new Date(fecha).toLocaleString('es-MX', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrecio = (precio) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(precio);
  };

  return (
    <div className="ventas-historial-container">
      {/* Header */}
      <div className="historial-header">
        <div className="header-left">
          <h1>
            <span className="header-icon">📊</span>
            Historial de Ventas
          </h1>
          <p className="subtitle">Consulta y gestiona el registro de ventas realizadas</p>
        </div>
        <button className="btn-primary" onClick={cargarVentas}>
          🔄 Actualizar
        </button>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">🛒</div>
          <div className="stat-content">
            <h3>{estadisticas.total_ventas}</h3>
            <p>Total de Ventas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-green">💰</div>
          <div className="stat-content">
            <h3>{formatPrecio(estadisticas.ingresos_totales)}</h3>
            <p>Ingresos Totales</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-purple">📈</div>
          <div className="stat-content">
            <h3>{formatPrecio(estadisticas.ticket_promedio)}</h3>
            <p>Ticket Promedio</p>
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
              placeholder="ID, cliente, sede, empleado..."
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
              <option value="completada">Completada</option>
              <option value="cancelada">Cancelada</option>
            </select>
          </div>

          {/* Fecha desde */}
          <div className="filter-group">
            <label>Desde</label>
            <input
              type="date"
              value={fechaDesde}
              onChange={(e) => setFechaDesde(e.target.value)}
              className="filter-input"
            />
          </div>

          {/* Fecha hasta */}
          <div className="filter-group">
            <label>Hasta</label>
            <input
              type="date"
              value={fechaHasta}
              onChange={(e) => setFechaHasta(e.target.value)}
              className="filter-input"
            />
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

      {/* Tabla de ventas */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando ventas...</p>
        </div>
      ) : ventasActuales.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">📋</div>
          <p>No se encontraron ventas con los filtros seleccionados</p>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="ventas-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Sede</th>
                  <th>Total</th>
                  <th>Método Pago</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {ventasActuales.map(venta => (
                  <tr key={venta.venta_id} className={`venta-row venta-${venta.estado}`}>
                    <td className="venta-id">#{venta.venta_id}</td>
                    <td>{formatFecha(venta.fecha_venta)}</td>
                    <td>{venta.cliente_nombre || 'Cliente Anónimo'}</td>
                    <td>
                      <span className="badge-sede">{venta.sede_nombre}</span>
                    </td>
                    <td className="venta-total">{formatPrecio(venta.total)}</td>
                    <td>
                      <span className={`badge-metodo badge-${venta.metodo_pago}`}>
                        {venta.metodo_pago_display}
                      </span>
                    </td>
                    <td>
                      <span className={`badge-estado badge-${venta.estado}`}>
                        {venta.estado === 'completada' ? '✓ Completada' : '✕ Cancelada'}
                      </span>
                    </td>
                    <td className="acciones-cell">
                      <button
                        className="btn-accion btn-ver"
                        onClick={() => verDetalle(venta)}
                        title="Ver detalle"
                      >
                        👁️
                      </button>
                      {venta.estado === 'completada' && (
                        <button
                          className="btn-accion btn-cancelar"
                          onClick={() => cancelarVenta(venta.venta_id)}
                          title="Cancelar venta"
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
                Página {paginaActual} de {totalPaginas} ({ventasFiltradas.length} ventas)
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
      {mostrarModal && ventaSeleccionada && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                <span className="modal-icon">🧾</span>
                Detalle de Venta #{ventaSeleccionada.venta_id}
              </h2>
              <button className="btn-cerrar-modal" onClick={cerrarModal}>✕</button>
            </div>

            <div className="modal-body">
              {/* Información general */}
              <div className="info-section">
                <h3>Información General</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="info-label">Fecha:</span>
                    <span className="info-value">{formatFecha(ventaSeleccionada.fecha_venta)}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Cliente:</span>
                    <span className="info-value">{ventaSeleccionada.cliente_nombre || 'Cliente Anónimo'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Sede:</span>
                    <span className="info-value">{ventaSeleccionada.sede_nombre}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Cajero:</span>
                    <span className="info-value">{ventaSeleccionada.empleado_nombre || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Método de Pago:</span>
                    <span className="info-value">{ventaSeleccionada.metodo_pago_display}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Estado:</span>
                    <span className={`badge-estado badge-${ventaSeleccionada.estado}`}>
                      {ventaSeleccionada.estado === 'completada' ? '✓ Completada' : '✕ Cancelada'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Productos */}
              <div className="info-section">
                <h3>Productos Vendidos</h3>
                <div className="productos-detalle">
                  <table className="productos-table">
                    <thead>
                      <tr>
                        <th>Producto</th>
                        <th>Código</th>
                        <th>Cantidad</th>
                        <th>Precio Unit.</th>
                        <th>Descuento</th>
                        <th>Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ventaSeleccionada.detalles?.map(detalle => (
                        <tr key={detalle.detalle_id}>
                          <td>{detalle.producto_nombre}</td>
                          <td className="producto-codigo">{detalle.producto_codigo}</td>
                          <td className="text-center">{detalle.cantidad}</td>
                          <td>{formatPrecio(detalle.precio_unitario)}</td>
                          <td className="text-descuento">
                            {detalle.descuento > 0 ? `-${formatPrecio(detalle.descuento)}` : '-'}
                          </td>
                          <td className="text-total">{formatPrecio(detalle.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Totales */}
              <div className="info-section">
                <div className="totales-detalle">
                  <div className="total-row">
                    <span className="total-label">Subtotal:</span>
                    <span className="total-value">{formatPrecio(ventaSeleccionada.subtotal)}</span>
                  </div>
                  {ventaSeleccionada.descuento_global > 0 && (
                    <div className="total-row descuento-row">
                      <span className="total-label">Descuento Global:</span>
                      <span className="total-value">-{formatPrecio(ventaSeleccionada.descuento_global)}</span>
                    </div>
                  )}
                  <div className="total-row total-final-row">
                    <span className="total-label">Total:</span>
                    <span className="total-value">{formatPrecio(ventaSeleccionada.total)}</span>
                  </div>
                </div>
              </div>

              {/* Notas */}
              {ventaSeleccionada.notas && (
                <div className="info-section">
                  <h3>Notas</h3>
                  <p className="notas-text">{ventaSeleccionada.notas}</p>
                </div>
              )}
            </div>

            <div className="modal-footer">
              {ventaSeleccionada.estado === 'completada' && (
                <button
                  className="btn-cancelar-venta"
                  onClick={() => cancelarVenta(ventaSeleccionada.venta_id)}
                >
                  🚫 Cancelar Venta
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

export default VentasHistorial;
