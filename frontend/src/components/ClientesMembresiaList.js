import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import membresiaService from '../services/membresiaService';
import clienteService from '../services/clienteService';
import instalacionesService from '../services/instalacionesService';
import './Ventas.css';

function ClientesMembresiaList() {
  const [clientesConMembresia, setClientesConMembresia] = useState([]);
  const [filteredClientes, setFilteredClientes] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');
  const [sedeFilter, setSedeFilter] = useState('');
  const [sedes, setSedes] = useState([]);
  const [statusFilter, setStatusFilter] = useState('activas'); // activas, recientes, proximas_vencer, vencidas_canceladas
  const [stats, setStats] = useState({
    total_suscripciones: 0,
    activas: 0,
    vencidas: 0,
    ingresos_mes_actual: 0
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchSedes();
    fetchClientesConMembresia();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    if (searchTerm.length >= 2) {
      searchClientes();
    } else {
      setSearchResults([]);
    }
  }, [searchTerm]);

  useEffect(() => {
    filterClientesPorSede();
  }, [clientesConMembresia, sedeFilter, statusFilter]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const filterClientesPorSede = () => {
    let filtered = clientesConMembresia;

    // Filtrar por sede
    if (sedeFilter) {
      filtered = filtered.filter(cliente => {
        // Si la membresía permite todas las sedes, siempre incluirla
        if (cliente.suscripcion?.permite_todas_sedes) {
          return true;
        }
        // Filtrar por sede de suscripción
        return cliente.suscripcion?.sede_id === parseInt(sedeFilter);
      });
    }

    // Filtrar por estado de suscripción
    const hoy = new Date();
    filtered = filtered.filter(cliente => {
      const diasRestantes = cliente.suscripcion?.dias_restantes || 0;
      const estado = cliente.suscripcion?.estado;
      const fechaSuscripcion = cliente.suscripcion?.fecha_inicio ? new Date(cliente.suscripcion.fecha_inicio) : null;

      // Calcular días desde la suscripción
      const diasDesde = fechaSuscripcion ? Math.floor((hoy - fechaSuscripcion) / (1000 * 60 * 60 * 24)) : 999;

      switch (statusFilter) {
        case 'activas':
          return estado === 'activa' && diasRestantes > 5;
        case 'recientes':
          // Suscripciones activas de los últimos 7 días
          return estado === 'activa' && diasDesde <= 7;
        case 'proximas_vencer':
          // Suscripciones activas con 5 días o menos para vencer
          return estado === 'activa' && diasRestantes <= 5 && diasRestantes > 0;
        case 'vencidas_canceladas':
          return estado === 'vencida' || estado === 'cancelada';
        default:
          return true;
      }
    });

    setFilteredClientes(filtered);
  };

  const fetchClientesConMembresia = async () => {
    try {
      setLoading(true);
      const response = await membresiaService.getClientesConMembresia();
      console.log('Datos de clientes con membresía:', response.data);
      setClientesConMembresia(response.data);
    } catch (err) {
      console.error('Error al cargar clientes con membresía:', err);
      showNotif('Error al cargar los clientes con membresía', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const response = await membresiaService.getEstadisticasSuscripciones();
      setStats(response.data);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const searchClientes = async () => {
    try {
      setSearching(true);
      const response = await clienteService.searchClientes(searchTerm);
      setSearchResults(response.data.results || response.data);
    } catch (err) {
      console.error('Error al buscar clientes:', err);
    } finally {
      setSearching(false);
    }
  };

  const handleClienteClick = (clienteId) => {
    navigate(`/ventas/servicios/cliente/${clienteId}`);
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const getDiasRestantesColor = (dias) => {
    if (dias > 30) return '#22c55e'; // Verde - mucho tiempo
    if (dias > 15) return '#22c55e'; // Verde - tiempo suficiente
    if (dias > 7) return '#f59e0b';  // Amarillo - advertencia
    return '#ef4444'; // Rojo - urgente
  };

  const isVencida = (estado) => {
    return estado === 'vencida';
  };

  if (loading) {
    return (
      <div className="ventas-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando clientes...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ventas-container">
      {/* Notification */}
      {showNotification && (
        <div className={`notification ${notificationType} show`}>
          {notificationMessage}
        </div>
      )}

      {/* Header */}
      <div className="ventas-header">
        <div>
          <h1>🎫 Servicios - Membresías</h1>
          <p className="ventas-subtitle">Gestiona las suscripciones de los clientes</p>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            👥
          </div>
          <div className="stat-content">
            <div className="stat-label">Suscripciones Activas</div>
            <div className="stat-value">{stats.activas}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            💰
          </div>
          <div className="stat-content">
            <div className="stat-label">Ingresos del Mes</div>
            <div className="stat-value">${parseFloat(stats.ingresos_mes_actual).toFixed(2)}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
            ⏰
          </div>
          <div className="stat-content">
            <div className="stat-label">Vencidas</div>
            <div className="stat-value">{stats.vencidas}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #666666 0%, #2a2a2a 100%)' }}>
            📊
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Suscripciones</div>
            <div className="stat-value">{stats.total_suscripciones}</div>
          </div>
        </div>
      </div>

      {/* Search Bar and Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar cliente por nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          {searchTerm && (
            <button
              className="clear-search"
              onClick={() => setSearchTerm('')}
            >
              ✕
            </button>
          )}
        </div>
        <div className="filter-select">
          <select
            value={sedeFilter}
            onChange={(e) => setSedeFilter(e.target.value)}
            style={{
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid #334155',
              background: '#1e293b',
              color: '#e2e8f0',
              fontSize: '0.9rem',
              minWidth: '200px'
            }}
          >
            <option value="">Todas las sedes</option>
            {sedes.map(sede => (
              <option key={sede.id} value={sede.id}>{sede.nombre}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Status Filter Tabs */}
      <div className="status-filter-tabs">
        <button
          className={`filter-tab ${statusFilter === 'activas' ? 'active' : ''}`}
          onClick={() => setStatusFilter('activas')}
        >
          <span className="tab-icon">✅</span>
          <span className="tab-label">Activas</span>
        </button>
        <button
          className={`filter-tab ${statusFilter === 'recientes' ? 'active' : ''}`}
          onClick={() => setStatusFilter('recientes')}
        >
          <span className="tab-icon">🆕</span>
          <span className="tab-label">Recientes (7 días)</span>
        </button>
        <button
          className={`filter-tab ${statusFilter === 'proximas_vencer' ? 'active' : ''}`}
          onClick={() => setStatusFilter('proximas_vencer')}
        >
          <span className="tab-icon">⚠️</span>
          <span className="tab-label">Próximas a Vencer (≤5 días)</span>
        </button>
        <button
          className={`filter-tab ${statusFilter === 'vencidas_canceladas' ? 'active' : ''}`}
          onClick={() => setStatusFilter('vencidas_canceladas')}
        >
          <span className="tab-icon">❌</span>
          <span className="tab-label">Vencidas/Canceladas</span>
        </button>
      </div>

      {/* Search Results */}
      {searchTerm && searchResults.length > 0 && (
        <div className="search-results-section">
          <h3 className="section-title">Resultados de búsqueda</h3>
          <div className="clientes-grid">
            {searchResults.map((cliente) => {
              // Obtener el ID correcto dependiendo de la estructura
              const clienteId = cliente.persona_id || cliente.cliente_id || cliente.id;
              return (
                <div
                  key={clienteId}
                  className="cliente-card clickable"
                  onClick={() => handleClienteClick(clienteId)}
                >
                  <div className="cliente-card-header">
                    <div className="cliente-avatar">
                      {cliente.nombre?.charAt(0)}{cliente.apellido_paterno?.charAt(0)}
                    </div>
                    <div className="cliente-info">
                      <h3>{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}</h3>
                      <p className="cliente-email">{cliente.email}</p>
                    </div>
                  </div>
                  <div className="cliente-card-footer">
                    <span className={`badge badge-${cliente.estado}`}>
                      {cliente.estado}
                    </span>
                    {cliente.tiene_membresia_activa ? (
                      <span className="badge badge-success">✓ Con Membresía</span>
                    ) : (
                      <span className="badge badge-warning">Sin Membresía</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {searching && (
        <div className="loading-spinner-small">
          <div className="spinner-small"></div>
          <p>Buscando clientes...</p>
        </div>
      )}

      {/* Clientes con Membresía */}
      <div className="section">
        <h2 className="section-title">
          {statusFilter === 'activas' && '✅ Clientes con Membresía Activa'}
          {statusFilter === 'recientes' && '🆕 Clientes Recientes (Últimos 7 días)'}
          {statusFilter === 'proximas_vencer' && '⚠️ Membresías Próximas a Vencer'}
          {statusFilter === 'vencidas_canceladas' && '❌ Membresías Vencidas/Canceladas'}
          <span style={{
            marginLeft: '10px',
            fontSize: '0.9rem',
            color: '#666666',
            fontWeight: 'normal'
          }}>
            ({filteredClientes.length} {sedeFilter ? `en ${sedes.find(s => s.id === parseInt(sedeFilter))?.nombre}` : 'total'})
          </span>
        </h2>

        {filteredClientes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🎫</div>
            <p>No hay clientes con membresía activa {sedeFilter ? 'en esta sede' : ''}</p>
            <p className="empty-subtitle">
              {sedeFilter ? 'Prueba seleccionando otra sede' : 'Usa el buscador para encontrar clientes y suscribirlos'}
            </p>
          </div>
        ) : (
          <div className="clientes-grid">
            {filteredClientes.map((cliente) => (
              <div
                key={cliente.cliente_id}
                className="cliente-membresia-card clickable"
                onClick={() => handleClienteClick(cliente.cliente_id)}
              >
                <div className="cliente-card-header">
                  <div className="cliente-avatar">
                    {cliente.nombre?.charAt(0)}{cliente.apellido_paterno?.charAt(0)}
                  </div>
                  <div className="cliente-info">
                    <h3>{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}</h3>
                    <p className="cliente-email">{cliente.email}</p>
                    <p className="cliente-telefono">📞 {cliente.telefono}</p>
                  </div>
                </div>

                <div className="membresia-info">
                  <div className="membresia-plan">
                    <span className="membresia-icon">🎫</span>
                    <div>
                      <h4>{cliente.suscripcion.membresia_nombre}</h4>
                      <p>{cliente.suscripcion.membresia_tipo}</p>
                      {cliente.suscripcion.sede_nombre && (
                        <p className="membresia-sede">🏢 {cliente.suscripcion.sede_nombre}</p>
                      )}
                    </div>
                  </div>

                  <div className="membresia-fechas">
                    <div className="fecha-item">
                      <span className="fecha-label">Inicio</span>
                      <span className="fecha-value">{new Date(cliente.suscripcion.fecha_inicio).toLocaleDateString('es-MX')}</span>
                    </div>
                    <div className="fecha-item">
                      <span className="fecha-label">Vencimiento</span>
                      <span className="fecha-value">{new Date(cliente.suscripcion.fecha_fin).toLocaleDateString('es-MX')}</span>
                    </div>
                  </div>

                  <div className="membresia-status" style={{ display: 'flex', justifyContent: 'center', marginTop: '1rem', visibility: 'visible' }}>
                    {(() => {
                      const dias = cliente.suscripcion?.dias_restantes;
                      const estado = cliente.suscripcion?.estado;
                      console.log(`Cliente ${cliente.nombre}: estado=${estado}, dias=${dias}`);

                      if (isVencida(estado)) {
                        return (
                          <div className="membresia-vencida-badge">
                            <span>⚠️ VENCIDA</span>
                            <span className="vencida-text">Requiere renovación</span>
                          </div>
                        );
                      }

                      // Simple version: just show the number prominently
                      return (
                        <div
                          style={{
                            backgroundColor: getDiasRestantesColor(dias || 0),
                            color: 'white',
                            padding: '12px 24px',
                            borderRadius: '12px',
                            textAlign: 'center',
                            fontWeight: 'bold',
                            display: 'block',
                            visibility: 'visible',
                            opacity: 1,
                            width: 'auto',
                            margin: '0 auto',
                            fontSize: '28px'
                          }}
                        >
                          {dias !== undefined && dias !== null ? `${dias} días` : '? días'}
                        </div>
                      );
                    })()}
                  </div>
                </div>

                <div className="cliente-card-footer">
                  <span className={`badge badge-${cliente.suscripcion.estado}`}>
                    {cliente.suscripcion.estado}
                  </span>
                  <span className="badge badge-secondary">
                    {cliente.suscripcion.metodo_pago}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ClientesMembresiaList;
