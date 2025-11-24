import React, { useState, useEffect } from 'react';
import horariosService from '../services/horariosService';
import clienteService from '../services/clienteService';
import instalacionesService from '../services/instalacionesService';
import './ReservasClases.css';

const ReservasClases = () => {
  const [reservas, setReservas] = useState([]);
  const [sesiones, setSesiones] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Filtros
  const [estadoFilter, setEstadoFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  // Nueva reserva - flujo paso a paso
  const [sedeSeleccionada, setSedeSeleccionada] = useState('');
  const [clienteSeleccionado, setClienteSeleccionado] = useState('');
  const [espacioSeleccionado, setEspacioSeleccionado] = useState('');
  const [sesionSeleccionada, setSesionSeleccionada] = useState('');
  const [clienteSearchTerm, setClienteSearchTerm] = useState('');

  // Estadísticas
  const [estadisticas, setEstadisticas] = useState({
    total: 0,
    confirmadas: 0,
    canceladas: 0,
    completadas: 0,
  });

  // Estadísticas de sesiones
  const [estadisticasSesiones, setEstadisticasSesiones] = useState({
    totalSesiones: 0,
    sesionesDisponibles: 0,
  });

  useEffect(() => {
    cargarDatos();
  }, [estadoFilter]);

  // Cargar clientes cuando se selecciona una sede
  useEffect(() => {
    if (sedeSeleccionada) {
      cargarClientesPorSede(sedeSeleccionada);
      cargarEspaciosPorSede(sedeSeleccionada);
    } else {
      setClientes([]);
      setEspacios([]);
    }
    setClienteSeleccionado('');
    setEspacioSeleccionado('');
    setSesionSeleccionada('');
  }, [sedeSeleccionada]);

  // Cargar sesiones cuando se selecciona un espacio
  useEffect(() => {
    if (espacioSeleccionado) {
      cargarSesionesPorEspacio(espacioSeleccionado);
    } else {
      setSesiones([]);
    }
    setSesionSeleccionada('');
  }, [espacioSeleccionado]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const filtros = {};
      if (estadoFilter) filtros.estado = estadoFilter;

      const [reservasData, sedesResponse, sesionesData] = await Promise.all([
        horariosService.getReservas(filtros),
        instalacionesService.getSedes(),
        horariosService.getSesiones({}), // Cargar todas las sesiones para estadísticas
      ]);

      setReservas(Array.isArray(reservasData) ? reservasData : reservasData.results || []);

      // El servicio de instalaciones devuelve response.data
      const sedesData = sedesResponse.data || sedesResponse;
      setSedes(Array.isArray(sedesData) ? sedesData : sedesData.data || []);

      calcularEstadisticas(Array.isArray(reservasData) ? reservasData : reservasData.results || []);
      calcularEstadisticasSesiones(Array.isArray(sesionesData) ? sesionesData : sesionesData.results || []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar datos:', error);

      // Verificar si es error de autenticación
      if (error.response?.status === 401) {
        setError('Sesión expirada. Por favor, vuelve a iniciar sesión.');
        // Redirigir al login después de 2 segundos
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        setError(error.response?.data?.error || error.message || 'Error al cargar las reservas');
      }

      setReservas([]);
    } finally {
      setLoading(false);
    }
  };

  const cargarClientesPorSede = async (sedeId) => {
    try {
      const response = await clienteService.getClientes({ estado: 'activo', sede: sedeId });
      const data = response.data || response;
      console.log('Clientes cargados:', data); // Debug
      setClientes(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error('Error al cargar clientes:', error);
      setClientes([]);
    }
  };

  const cargarEspaciosPorSede = async (sedeId) => {
    try {
      const response = await instalacionesService.getEspaciosBySede(sedeId);
      const data = response.data || response;
      setEspacios(Array.isArray(data) ? data : data.results || []);
    } catch (error) {
      console.error('Error al cargar espacios:', error);
      setEspacios([]);
    }
  };

  const cargarSesionesPorEspacio = async (espacioId) => {
    try {
      // Cargar todas las sesiones del espacio y filtrar por estado en el frontend
      const response = await horariosService.getSesiones({
        horario__espacio: espacioId,
        horario__espacio__sede: sedeSeleccionada // Filtrar por sede seleccionada
      });
      const data = response.data || response;
      const sesionesData = Array.isArray(data) ? data : data.results || [];

      console.log('Sesiones cargadas para sede:', sedeSeleccionada, sesionesData);

      // Obtener fecha actual (solo fecha, sin hora)
      const hoy = new Date();
      hoy.setHours(0, 0, 0, 0);

      // Filtrar sesiones futuras, con estado activa/programada y con lugares disponibles
      const sesionesFiltradas = sesionesData.filter(s => {
        const fechaSesion = new Date(s.fecha);
        fechaSesion.setHours(0, 0, 0, 0);

        return (
          fechaSesion >= hoy && // Solo sesiones futuras o de hoy
          (s.estado === 'activa' || s.estado === 'programada') &&
          !s.esta_llena &&
          s.lugares_disponibles > 0
        );
      });

      // Ordenar por fecha (más próximas primero)
      sesionesFiltradas.sort((a, b) => new Date(a.fecha) - new Date(b.fecha));

      console.log('Sesiones filtradas y ordenadas:', sesionesFiltradas);
      setSesiones(sesionesFiltradas);
    } catch (error) {
      console.error('Error al cargar sesiones:', error);
      setSesiones([]);
    }
  };

  const calcularEstadisticas = (data) => {
    const total = data.length;
    const confirmadas = data.filter((r) => r.estado === 'confirmada').length;
    const canceladas = data.filter((r) => r.estado === 'cancelada').length;
    const completadas = data.filter((r) => r.estado === 'completada').length;

    setEstadisticas({ total, confirmadas, canceladas, completadas });
  };

  const calcularEstadisticasSesiones = (data) => {
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    const sesionesDisponibles = data.filter(s => {
      const fechaSesion = new Date(s.fecha);
      fechaSesion.setHours(0, 0, 0, 0);

      return (
        fechaSesion >= hoy &&
        (s.estado === 'activa' || s.estado === 'programada') &&
        !s.esta_llena &&
        s.lugares_disponibles > 0
      );
    }).length;

    setEstadisticasSesiones({
      totalSesiones: data.length,
      sesionesDisponibles: sesionesDisponibles,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await horariosService.createReserva({
        sesion_clase: sesionSeleccionada,
        cliente: clienteSeleccionado,
      });

      // Mostrar mensaje de éxito con animación
      setSuccessMessage('✓ Reserva creada exitosamente');
      setTimeout(() => setSuccessMessage(''), 3000);

      cerrarModal();
      await cargarDatos();
    } catch (error) {
      console.error('Error al crear reserva:', error);

      // Verificar si es error de suscripción inactiva
      const errorMsg = error.response?.data?.error || error.response?.data?.non_field_errors?.[0] || error.message;

      if (errorMsg && errorMsg.toLowerCase().includes('membresía')) {
        // Redirigir a página de suscripciones (Ventas - Servicios)
        if (window.confirm('El cliente no tiene una membresía activa. ¿Deseas ir a la página de suscripciones para activar una?')) {
          window.location.href = '/ventas/servicios';
        }
      } else {
        alert('Error al crear la reserva: ' + errorMsg);
      }
    }
  };

  const cerrarModal = () => {
    setShowModal(false);
    setSedeSeleccionada('');
    setClienteSeleccionado('');
    setEspacioSeleccionado('');
    setSesionSeleccionada('');
    setClienteSearchTerm('');
  };

  const cancelarReserva = async (id) => {
    if (!window.confirm('¿Está seguro de cancelar esta reserva?')) {
      return;
    }

    try {
      await horariosService.cancelarReserva(id);

      // Mostrar mensaje de éxito con animación
      setSuccessMessage('✓ Reserva cancelada exitosamente');
      setTimeout(() => setSuccessMessage(''), 3000);

      await cargarDatos();
    } catch (error) {
      console.error('Error al cancelar reserva:', error);
      alert('Error al cancelar la reserva: ' + (error.response?.data?.error || error.message));
    }
  };

  const limpiarFiltros = () => {
    setEstadoFilter('');
    setSearchTerm('');
  };

  const reservasFiltradas = reservas.filter((reserva) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      reserva.cliente_nombre?.toLowerCase().includes(searchLower) ||
      reserva.sesion_actividad?.toLowerCase().includes(searchLower) ||
      reserva.codigo_reserva?.toLowerCase().includes(searchLower)
    );
  });

  const formatFecha = (fecha) => {
    if (!fecha) return '';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatHora = (hora) => {
    if (!hora) return '';
    return hora.substring(0, 5); // HH:MM
  };

  return (
    <div className="reservas-container">
      {/* Header */}
      <div className="page-header">
        <div>
          <h2>
            <span className="header-icon">🎫</span>
            Reservas de Clases
          </h2>
          <p className="subtitle">Gestiona las reservas de clases y actividades</p>
        </div>
        <button className="btn-primary" onClick={() => setShowModal(true)}>
          + Nueva Reserva
        </button>
      </div>

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon stat-icon-blue">📊</div>
          <div className="stat-content">
            <h3>{estadisticas.total}</h3>
            <p>Total de Reservas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-green">✓</div>
          <div className="stat-content">
            <h3>{estadisticas.confirmadas}</h3>
            <p>Confirmadas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-orange">📅</div>
          <div className="stat-content">
            <h3>{estadisticasSesiones.sesionesDisponibles}</h3>
            <p>Sesiones Disponibles</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-purple">🏆</div>
          <div className="stat-content">
            <h3>{estadisticas.completadas}</h3>
            <p>Completadas</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon stat-icon-red">✕</div>
          <div className="stat-content">
            <h3>{estadisticas.canceladas}</h3>
            <p>Canceladas</p>
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
              placeholder="Cliente, actividad, código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Estado</label>
            <select value={estadoFilter} onChange={(e) => setEstadoFilter(e.target.value)} className="filter-select">
              <option value="">Todos</option>
              <option value="confirmada">Confirmada</option>
              <option value="cancelada">Cancelada</option>
              <option value="completada">Completada</option>
              <option value="no_asistio">No Asistió</option>
            </select>
          </div>
        </div>
      </div>

      {/* Mensajes de Error */}
      {error && (
        <div className="alert alert-error">
          <span>{error}</span>
          <span className="alert-icon" onClick={() => setError(null)}>
            ✕
          </span>
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

      {/* Grid de Cards de Reservas */}
      {loading ? (
        <div className="loading-spinner">
          <span className="spinner">⏳</span>
          <p>Cargando reservas...</p>
        </div>
      ) : reservasFiltradas.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon">🎫</div>
          <p>No se encontraron reservas</p>
        </div>
      ) : (
        <div className="reservas-grid">
          {reservasFiltradas.map((reserva) => (
            <div key={reserva.id} className={`reserva-card reserva-card-${reserva.estado}`}>
              <div className="reserva-card-header">
                <div>
                  <h3 className="actividad-nombre">{reserva.sesion_actividad}</h3>
                  <span className="codigo-reserva">{reserva.codigo_reserva}</span>
                </div>
                <span className={`badge-estado badge-${reserva.estado}`}>
                  {reserva.estado === 'confirmada' && '✓ Confirmada'}
                  {reserva.estado === 'cancelada' && '✕ Cancelada'}
                  {reserva.estado === 'completada' && '🏆 Completada'}
                  {reserva.estado === 'no_asistio' && '⚠ No Asistió'}
                </span>
              </div>

              <div className="reserva-card-body">
                <div className="reserva-info-item">
                  <span className="info-icon">👤</span>
                  <div>
                    <span className="info-label">Cliente</span>
                    <span className="info-value">{reserva.cliente_nombre}</span>
                  </div>
                </div>

                <div className="reserva-info-item">
                  <span className="info-icon">🏋️</span>
                  <div>
                    <span className="info-label">Entrenador</span>
                    <span className="info-value">{reserva.sesion_entrenador || 'No asignado'}</span>
                  </div>
                </div>

                <div className="reserva-info-item">
                  <span className="info-icon">🕐</span>
                  <div>
                    <span className="info-label">Horario</span>
                    <span className="info-value">
                      {formatHora(reserva.sesion_hora_inicio)} - {formatHora(reserva.sesion_hora_fin)}
                    </span>
                  </div>
                </div>

                <div className="reserva-info-item">
                  <span className="info-icon">📍</span>
                  <div>
                    <span className="info-label">Sede y Espacio</span>
                    <span className="info-value">{reserva.sesion_sede} - {reserva.sesion_espacio}</span>
                  </div>
                </div>

                <div className="reserva-info-item">
                  <span className="info-icon">📅</span>
                  <div>
                    <span className="info-label">Fecha</span>
                    <span className="info-value">{formatFecha(reserva.sesion_fecha)}</span>
                  </div>
                </div>
              </div>

              {reserva.estado === 'confirmada' && (
                <div className="reserva-card-footer">
                  <button className="btn-cancelar-reserva" onClick={() => cancelarReserva(reserva.id)}>
                    ✕ Cancelar Reserva
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Modal Nueva Reserva */}
      {showModal && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Nueva Reserva</h3>
              <button className="btn-close" onClick={cerrarModal}>
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {/* Paso 1: Seleccionar Sede */}
              <div className="form-group">
                <label>1. Seleccionar Sede *</label>
                <select
                  value={sedeSeleccionada}
                  onChange={(e) => setSedeSeleccionada(e.target.value)}
                  className="form-input"
                  required
                >
                  <option value="">Seleccione una sede</option>
                  {sedes.map((sede) => (
                    <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                      {sede.nombre}
                    </option>
                  ))}
                </select>
              </div>

              {/* Paso 2: Seleccionar Cliente con búsqueda */}
              {sedeSeleccionada && (
                <>
                  <div className="form-group">
                    <label>Buscar Cliente</label>
                    <input
                      type="text"
                      value={clienteSearchTerm}
                      onChange={(e) => setClienteSearchTerm(e.target.value)}
                      className="form-input"
                      placeholder="Escribe el nombre del cliente..."
                    />
                  </div>

                  <div className="form-group">
                    <label>2. Seleccionar Cliente * ({clientes.length} disponibles)</label>
                    <select
                      value={clienteSeleccionado}
                      onChange={(e) => setClienteSeleccionado(e.target.value)}
                      className="form-input"
                      required
                    >
                      <option value="">Seleccione un cliente</option>
                      {clientes
                        .filter((cliente) => {
                          if (!clienteSearchTerm) return true;
                          const nombreCompleto = `${cliente.nombre || ''} ${cliente.apellido_paterno || ''} ${cliente.apellido_materno || ''}`.toLowerCase();
                          return nombreCompleto.includes(clienteSearchTerm.toLowerCase());
                        })
                        .map((cliente) => {
                          const nombreCompleto = `${cliente.nombre || ''} ${cliente.apellido_paterno || ''} ${cliente.apellido_materno || ''}`.trim();
                          return (
                            <option key={cliente.id} value={cliente.id}>
                              {nombreCompleto || `Cliente #${cliente.id}`}
                            </option>
                          );
                        })}
                    </select>
                    {clientes.length === 0 && sedeSeleccionada && (
                      <p style={{ color: 'var(--danger)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                        No hay clientes activos en esta sede
                      </p>
                    )}
                  </div>
                </>
              )}

              {/* Paso 3: Seleccionar Espacio */}
              {clienteSeleccionado && (
                <div className="form-group">
                  <label>3. Seleccionar Espacio *</label>
                  <select
                    value={espacioSeleccionado}
                    onChange={(e) => setEspacioSeleccionado(e.target.value)}
                    className="form-input"
                    required
                  >
                    <option value="">Seleccione un espacio</option>
                    {espacios.map((espacio) => (
                      <option key={espacio.id} value={espacio.id}>
                        {espacio.nombre}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Paso 4: Seleccionar Clase con Cards */}
              {espacioSeleccionado && (
                <div className="form-group">
                  <label>4. Seleccionar Clase * ({sesiones.length} disponibles)</label>
                  {sesiones.length === 0 ? (
                    <div className="no-sesiones-message">
                      <span>📅</span>
                      <p>No hay clases disponibles para este espacio</p>
                    </div>
                  ) : (
                    <div className="sesiones-grid">
                      {sesiones.map((sesion) => {
                        const actividad = sesion.horario_detalle?.tipo_actividad_detalle?.nombre || 'Actividad';
                        const color = sesion.horario_detalle?.tipo_actividad_detalle?.color_hex || '#3b82f6';
                        const fecha = formatFecha(sesion.fecha);
                        const horaInicio = formatHora(sesion.hora_inicio_efectiva);
                        const horaFin = formatHora(sesion.hora_fin_efectiva);
                        const disponibles = sesion.lugares_disponibles || 0;
                        const cupoTotal = sesion.cupo_efectivo || 0;
                        const entrenador = sesion.horario_detalle?.entrenador_detalle?.nombre_completo || 'Sin asignar';

                        return (
                          <div
                            key={sesion.id}
                            className={`sesion-card ${sesionSeleccionada === sesion.id ? 'sesion-card-selected' : ''}`}
                            onClick={() => setSesionSeleccionada(sesion.id)}
                            style={{ borderLeftColor: color }}
                          >
                            <div className="sesion-card-header">
                              <span className="sesion-actividad" style={{ color }}>{actividad}</span>
                              <span className="sesion-cupo">{disponibles}/{cupoTotal} 👥</span>
                            </div>
                            <div className="sesion-card-body">
                              <div className="sesion-info-row">
                                <span className="sesion-icon">📅</span>
                                <span className="sesion-text">{fecha}</span>
                              </div>
                              <div className="sesion-info-row">
                                <span className="sesion-icon">🕐</span>
                                <span className="sesion-text">{horaInicio} - {horaFin}</span>
                              </div>
                              <div className="sesion-info-row">
                                <span className="sesion-icon">🏋️</span>
                                <span className="sesion-text">{entrenador}</span>
                              </div>
                            </div>
                            {sesionSeleccionada === sesion.id && (
                              <div className="sesion-card-checkmark">✓</div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              <div className="modal-actions">
                <button type="button" className="btn-secondary" onClick={cerrarModal}>
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="btn-primary"
                  disabled={!sedeSeleccionada || !clienteSeleccionado || !espacioSeleccionado || !sesionSeleccionada}
                >
                  Crear Reserva
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReservasClases;
