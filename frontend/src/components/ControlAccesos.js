import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import accesosService from '../services/accesosService';
import instalacionesService from '../services/instalacionesService';
import './ControlAccesos.css';

const ControlAccesos = () => {
  const navigate = useNavigate();

  // Estados principales
  const [sedes, setSedes] = useState([]);
  const [sedeSeleccionada, setSedeSeleccionada] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Estados para resultados de búsqueda
  const [busquedaRealizada, setBusquedaRealizada] = useState(false);
  const [resultadosMultiples, setResultadosMultiples] = useState([]);
  const [clienteInfo, setClienteInfo] = useState(null);
  const [mensajeEstado, setMensajeEstado] = useState('');

  // Estados para modal
  const [mostrarModal, setMostrarModal] = useState(false);
  const [accesoAutorizado, setAccesoAutorizado] = useState(false);
  const [mostrarBienvenida, setMostrarBienvenida] = useState(false);

  // Estados para autocompletado
  const [sugerencias, setSugerencias] = useState([]);
  const [mostrarSugerencias, setMostrarSugerencias] = useState(false);
  const [searchTimeout, setSearchTimeout] = useState(null);

  useEffect(() => {
    cargarSedes();
  }, []);

  // Búsqueda en tiempo real mientras escribe
  useEffect(() => {
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    if (searchTerm.trim().length >= 3 && sedeSeleccionada) {
      const timeout = setTimeout(() => {
        buscarEnTiempoReal();
      }, 500); // Esperar 500ms después de que el usuario deje de escribir

      setSearchTimeout(timeout);
    } else {
      setSugerencias([]);
      setMostrarSugerencias(false);
    }

    return () => {
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
    };
  }, [searchTerm, sedeSeleccionada]);

  // Cerrar sugerencias al hacer clic fuera
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (mostrarSugerencias && !event.target.closest('.search-group')) {
        setMostrarSugerencias(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [mostrarSugerencias]);

  const cargarSedes = async () => {
    try {
      const sedesResponse = await instalacionesService.getSedes();
      const sedesData = Array.isArray(sedesResponse) ? sedesResponse : sedesResponse.data;
      setSedes(sedesData || []);

      // Seleccionar primera sede por defecto
      if (sedesData && sedesData.length > 0) {
        setSedeSeleccionada(sedesData[0].sede_id || sedesData[0].id);
      }
    } catch (error) {
      console.error('Error al cargar sedes:', error);
      setError('Error al cargar las sedes');
    }
  };

  const buscarEnTiempoReal = async () => {
    if (!searchTerm.trim() || !sedeSeleccionada) return;

    try {
      const resultado = await accesosService.buscarClientesRealTime(searchTerm, sedeSeleccionada);

      if (resultado.multiple && resultado.clientes) {
        setSugerencias(resultado.clientes);
        setMostrarSugerencias(true);
      } else if (resultado.encontrado && resultado.cliente) {
        // Un solo resultado
        setSugerencias([{
          cliente_id: resultado.cliente.cliente_id,
          nombre_completo: resultado.cliente.nombre_completo,
          telefono: resultado.cliente.telefono
        }]);
        setMostrarSugerencias(true);
      } else {
        setSugerencias([]);
        setMostrarSugerencias(false);
      }
    } catch (error) {
      // No mostrar error en búsqueda en tiempo real, solo limpiar sugerencias
      setSugerencias([]);
      setMostrarSugerencias(false);
    }
  };

  const seleccionarSugerencia = (cliente) => {
    setSearchTerm(cliente.nombre_completo);
    setMostrarSugerencias(false);
    setSugerencias([]);
    // Seleccionar el cliente directamente
    seleccionarCliente(cliente.cliente_id);
  };

  const buscarCliente = async (e) => {
    e.preventDefault();

    if (!searchTerm.trim()) {
      setError('Por favor ingresa un nombre, email o teléfono');
      return;
    }

    if (!sedeSeleccionada) {
      setError('Por favor selecciona una sede');
      return;
    }

    setLoading(true);
    setError(null);
    setBusquedaRealizada(false);
    setResultadosMultiples([]);
    setClienteInfo(null);

    try {
      const resultado = await accesosService.validarAcceso(searchTerm, sedeSeleccionada);

      setBusquedaRealizada(true);

      if (resultado.multiple) {
        // Múltiples resultados - mostrar lista para seleccionar
        setResultadosMultiples(resultado.clientes);
        setMensajeEstado(resultado.mensaje);
      } else if (resultado.encontrado && resultado.cliente) {
        // Un solo cliente encontrado
        setClienteInfo(resultado.cliente);
        mostrarModalAcceso(resultado.cliente);
      }
    } catch (error) {
      console.error('Error al buscar cliente:', error);

      if (error.response && error.response.status === 404) {
        setError('No se encontró ningún cliente con ese criterio de búsqueda');
        setBusquedaRealizada(true);
      } else {
        setError('Error al buscar el cliente. Por favor intenta de nuevo.');
      }
    } finally {
      setLoading(false);
    }
  };

  const seleccionarCliente = async (clienteId) => {
    setLoading(true);
    setError(null);

    try {
      const resultado = await accesosService.validarAcceso(
        clienteId.toString(),
        sedeSeleccionada
      );

      if (resultado.encontrado && resultado.cliente) {
        setClienteInfo(resultado.cliente);
        setResultadosMultiples([]);
        mostrarModalAcceso(resultado.cliente);
      }
    } catch (error) {
      console.error('Error al obtener información del cliente:', error);

      if (error.response && error.response.status === 404) {
        setError('No se encontró el cliente seleccionado');
        setBusquedaRealizada(true);
      } else {
        setError('Error al obtener la información del cliente. Por favor intenta de nuevo.');
      }
    } finally {
      setLoading(false);
    }
  };

  const mostrarModalAcceso = (cliente) => {
    setAccesoAutorizado(cliente.puede_acceder);
    setMostrarModal(true);
  };

  const confirmarAcceso = async () => {
    if (!clienteInfo) return;

    setLoading(true);

    try {
      const resultado = await accesosService.registrarAcceso(
        clienteInfo.cliente_id,
        sedeSeleccionada,
        ''
      );

      // Cerrar modal de confirmación
      setMostrarModal(false);

      // Mostrar animación de bienvenida
      setMostrarBienvenida(true);

      // Ocultar la animación después de 4 segundos
      setTimeout(() => {
        setMostrarBienvenida(false);
        resetearBusqueda();
      }, 4000);
    } catch (error) {
      console.error('Error al registrar acceso:', error);
      alert('Error al registrar el acceso');
    } finally {
      setLoading(false);
    }
  };

  const resetearBusqueda = () => {
    setSearchTerm('');
    setBusquedaRealizada(false);
    setResultadosMultiples([]);
    setClienteInfo(null);
    setError(null);
    setMensajeEstado('');
    setSugerencias([]);
    setMostrarSugerencias(false);
  };

  const cerrarModal = () => {
    setMostrarModal(false);
  };

  const irARegistroCliente = () => {
    navigate('/clientes/nuevo');
  };

  const irAComprarMembresia = () => {
    if (clienteInfo) {
      // Cerrar modal primero
      setMostrarModal(false);
      // Navegar a la página de comprar membresía
      navigate(`/ventas/servicios/cliente/${clienteInfo.cliente_id}`);
    }
  };

  const formatFecha = (fecha) => {
    if (!fecha) return 'N/A';
    return new Date(fecha).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="control-accesos-container">
      {/* Header */}
      <div className="accesos-header">
        <div className="header-left">
          <h1>
            <span className="header-icon">🚪</span>
            Control de Accesos
          </h1>
          <p className="subtitle">Valida y registra el acceso de clientes al gimnasio</p>
        </div>
      </div>

      {/* Formulario de búsqueda */}
      <div className="busqueda-card">
        <form onSubmit={buscarCliente}>
          <div className="busqueda-grid">
            {/* Selector de sede */}
            <div className="form-group">
              <label>Sede</label>
              <select
                value={sedeSeleccionada}
                onChange={(e) => setSedeSeleccionada(e.target.value)}
                className="form-select"
                required
              >
                <option value="">Selecciona una sede</option>
                {sedes.map(sede => (
                  <option key={sede.sede_id || sede.id} value={sede.sede_id || sede.id}>
                    {sede.nombre}
                  </option>
                ))}
              </select>
            </div>

            {/* Campo de búsqueda */}
            <div className="form-group search-group" style={{ position: 'relative' }}>
              <label>Buscar Cliente</label>
              <input
                type="text"
                placeholder="Nombre, email o teléfono... (mínimo 3 caracteres)"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() => {
                  if (sugerencias.length > 0) {
                    setMostrarSugerencias(true);
                  }
                }}
                className="form-input"
                disabled={loading}
                autoComplete="off"
              />

              {/* Dropdown de sugerencias */}
              {mostrarSugerencias && sugerencias.length > 0 && (
                <div className="sugerencias-dropdown">
                  {sugerencias.map((cliente) => (
                    <div
                      key={cliente.cliente_id}
                      className="sugerencia-item"
                      onClick={() => seleccionarSugerencia(cliente)}
                    >
                      <div className="sugerencia-nombre">
                        <strong>{cliente.nombre_completo}</strong>
                      </div>
                      <div className="sugerencia-telefono">
                        📱 {cliente.telefono}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Botón de búsqueda */}
            <div className="form-group button-group">
              <button
                type="submit"
                className="btn-buscar"
                disabled={loading || !sedeSeleccionada}
              >
                {loading ? '⏳ Buscando...' : '🔍 Buscar'}
              </button>
              {busquedaRealizada && (
                <button
                  type="button"
                  className="btn-limpiar"
                  onClick={resetearBusqueda}
                >
                  ✕ Limpiar
                </button>
              )}
            </div>
          </div>
        </form>

        {/* Mensajes de error */}
        {error && (
          <div className="alert alert-error">
            <span>⚠️ {error}</span>
            {error.includes('No se encontró') && (
              <button className="btn-registro" onClick={irARegistroCliente}>
                ➕ Registrar nuevo cliente
              </button>
            )}
          </div>
        )}
      </div>

      {/* Resultados de búsqueda múltiple */}
      {resultadosMultiples.length > 0 && (
        <div className="resultados-card">
          <h3>📋 {mensajeEstado}</h3>
          <div className="resultados-list">
            {resultadosMultiples.map(cliente => (
              <div key={cliente.cliente_id} className="resultado-item" onClick={() => seleccionarCliente(cliente.cliente_id)}>
                <div className="resultado-info">
                  <h4>{cliente.nombre_completo}</h4>
                  <p>📧 {cliente.email || 'Sin email'}</p>
                  <p>📞 {cliente.telefono || 'Sin teléfono'}</p>
                </div>
                <button className="btn-seleccionar">Seleccionar →</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Modal de confirmación de acceso */}
      {mostrarModal && clienteInfo && (
        <div className="modal-overlay" onClick={cerrarModal}>
          <div className={`modal-content ${accesoAutorizado ? 'acceso-autorizado' : 'acceso-denegado'}`} onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>
                {accesoAutorizado ? (
                  <><span className="status-icon">✓</span> Acceso Autorizado</>
                ) : (
                  <><span className="status-icon">✕</span> Acceso Denegado</>
                )}
              </h2>
              <button className="btn-cerrar-modal" onClick={cerrarModal}>✕</button>
            </div>

            <div className="modal-body">
              {/* Información del cliente */}
              <div className="cliente-card">
                <div className="cliente-foto">
                  {clienteInfo.foto_url ? (
                    <img src={clienteInfo.foto_url} alt={clienteInfo.nombre_completo} />
                  ) : (
                    <div className="foto-placeholder">👤</div>
                  )}
                </div>
                <div className="cliente-datos">
                  <h3>{clienteInfo.nombre_completo}</h3>
                  <p>📧 {clienteInfo.email || 'Sin email'}</p>
                  <p>📞 {clienteInfo.telefono || 'Sin teléfono'}</p>
                  <p>📊 Total de accesos: <strong>{clienteInfo.total_accesos}</strong></p>
                  {clienteInfo.ultimo_acceso && (
                    <p>🕐 Último acceso: {formatFecha(clienteInfo.ultimo_acceso)}</p>
                  )}
                </div>
              </div>

              {/* Estado de membresía */}
              {accesoAutorizado ? (
                <div className="membresia-card membresia-activa">
                  <h4>💳 Membresía Activa</h4>
                  <div className="membresia-info">
                    <p><strong>Plan:</strong> {clienteInfo.membresia_nombre}</p>
                    <p><strong>Tipo:</strong> {clienteInfo.membresia_tipo}</p>
                    <p><strong>Válida desde:</strong> {formatFecha(clienteInfo.fecha_inicio)}</p>
                    <p><strong>Válida hasta:</strong> {formatFecha(clienteInfo.fecha_fin)}</p>
                    <p className="dias-restantes">
                      <strong>⏱️ Días restantes:</strong> {clienteInfo.dias_restantes}
                    </p>
                    {clienteInfo.permite_todas_sedes ? (
                      <p className="badge-multisede">⭐ Acceso a todas las sedes</p>
                    ) : (
                      <p><strong>Sede:</strong> {clienteInfo.sede_suscripcion_nombre}</p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="membresia-card membresia-inactiva">
                  <h4>⚠️ {clienteInfo.tiene_membresia_activa ? 'Membresía No Válida Para Esta Sede' : 'Sin Membresía Activa'}</h4>
                  <p className="motivo-denegado">{clienteInfo.motivo_denegado}</p>

                  {/* Mostrar info de membresía existente si tiene una */}
                  {clienteInfo.tiene_membresia_activa && (
                    <div className="membresia-info" style={{ marginTop: '1rem', fontSize: '0.9rem' }}>
                      <p><strong>Membresía actual:</strong> {clienteInfo.membresia_nombre}</p>
                      <p><strong>Válida en:</strong> {clienteInfo.sede_suscripcion_nombre || 'No especificada'}</p>
                      <p><strong>Válida hasta:</strong> {formatFecha(clienteInfo.fecha_fin)}</p>
                    </div>
                  )}

                  {/* Botón para comprar o actualizar membresía */}
                  <button className="btn-comprar" onClick={irAComprarMembresia}>
                    {clienteInfo.tiene_membresia_activa ? '🔄 Comprar Membresía para Esta Sede' : '🛒 Comprar Membresía'}
                  </button>
                </div>
              )}
            </div>

            <div className="modal-footer">
              {accesoAutorizado ? (
                <>
                  <button className="btn-confirmar" onClick={confirmarAcceso} disabled={loading}>
                    {loading ? '⏳ Registrando...' : '✓ Confirmar Acceso'}
                  </button>
                  <button className="btn-cancelar" onClick={cerrarModal}>
                    Cancelar
                  </button>
                </>
              ) : (
                <button className="btn-cerrar" onClick={cerrarModal}>
                  Cerrar
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal de animación de bienvenida */}
      {mostrarBienvenida && (
        <div className="bienvenida-overlay">
          <div className="bienvenida-modal">
            <div className="bienvenida-icono">✓</div>
            <h1 className="bienvenida-titulo">¡Bienvenido a tu gimnasio!</h1>
            <p className="bienvenida-mensaje">Que tengas un excelente entrenamiento</p>
            <div className="bienvenida-decoracion">
              <span className="emoji-animado">💪</span>
              <span className="emoji-animado">🏋️</span>
              <span className="emoji-animado">⚡</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ControlAccesos;
