import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import clienteService from '../services/clienteService';
import './GestionEquipos.css';
import './ClienteList.css';

function ClienteList() {
  const [clientes, setClientes] = useState([]);
  const [filteredClientes, setFilteredClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [nivelFilter, setNivelFilter] = useState('');
  const [estadisticas, setEstadisticas] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchClientes();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    filterClientes();
  }, [clientes, searchTerm, estadoFilter, nivelFilter]);

  const fetchClientes = async () => {
    try {
      setLoading(true);
      const response = await clienteService.getClientes();
      setClientes(response.data);
    } catch (err) {
      console.error('Error al cargar clientes:', err);
      alert('Error al cargar los clientes');
    } finally {
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const response = await clienteService.getEstadisticas();
      setEstadisticas(response.data);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const filterClientes = () => {
    let filtered = [...clientes];

    if (estadoFilter) {
      filtered = filtered.filter(cliente => cliente.estado === estadoFilter);
    }

    if (nivelFilter) {
      filtered = filtered.filter(cliente => cliente.nivel_experiencia === nivelFilter);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(cliente =>
        cliente.nombre?.toLowerCase().includes(term) ||
        cliente.apellido_paterno?.toLowerCase().includes(term) ||
        cliente.apellido_materno?.toLowerCase().includes(term) ||
        cliente.telefono?.includes(term) ||
        cliente.email?.toLowerCase().includes(term)
      );
    }

    setFilteredClientes(filtered);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este cliente?')) {
      try {
        await clienteService.deleteCliente(id);
        alert('✓ Cliente eliminado exitosamente');
        fetchClientes();
        fetchEstadisticas();
      } catch (err) {
        console.error('Error al eliminar:', err);
        alert('Error al eliminar el cliente');
      }
    }
  };

  const getEstadoColor = (estado) => {
    const colors = {
      'activo': '#10b981',
      'inactivo': '#6b7280',
      'suspendido': '#ef4444'
    };
    return colors[estado] || '#6b7280';
  };

  const getNivelColor = (nivel) => {
    const colors = {
      'principiante': '#60a5fa',
      'intermedio': '#f59e0b',
      'avanzado': '#a78bfa'
    };
    return colors[nivel] || '#60a5fa';
  };

  const getNivelIcon = (nivel) => {
    const icons = {
      'principiante': '🏁',
      'intermedio': '📊',
      'avanzado': '🎯'
    };
    return icons[nivel] || '🏁';
  };

  return (
    <div className="activo-list-container">
      {/* Header */}
      <div className="header">
        <div>
          <h1>Gestión de Clientes</h1>
          <p className="subtitle">Administración de clientes del gimnasio</p>
        </div>
        <Link to="/clientes/new" className="btn btn-primary">
          + Nuevo Cliente
        </Link>
      </div>

      {/* Estadísticas */}
      {estadisticas && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
              👥
            </div>
            <div className="stat-content">
              <div className="stat-label">Total Clientes</div>
              <div className="stat-value">{estadisticas.total_clientes || 0}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
              ✓
            </div>
            <div className="stat-content">
              <div className="stat-label">Activos</div>
              <div className="stat-value">{estadisticas.activos || 0}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%)' }}>
              🏁
            </div>
            <div className="stat-content">
              <div className="stat-label">Principiantes</div>
              <div className="stat-value">{estadisticas.principiantes || 0}</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%)' }}>
              🎯
            </div>
            <div className="stat-content">
              <div className="stat-label">Avanzados</div>
              <div className="stat-value">{estadisticas.avanzados || 0}</div>
            </div>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por nombre, teléfono o email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">🔄</span>
              Estado
            </label>
            <select
              value={estadoFilter}
              onChange={(e) => setEstadoFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="activo">✓ Activo</option>
              <option value="inactivo">⏸️ Inactivo</option>
              <option value="suspendido">🚫 Suspendido</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">📊</span>
              Nivel
            </label>
            <select
              value={nivelFilter}
              onChange={(e) => setNivelFilter(e.target.value)}
              className="filter-select"
            >
              <option value="">Todos los niveles</option>
              <option value="principiante">🏁 Principiante</option>
              <option value="intermedio">📊 Intermedio</option>
              <option value="avanzado">🎯 Avanzado</option>
            </select>
          </div>

          <button
            onClick={() => {
              setSearchTerm('');
              setEstadoFilter('');
              setNivelFilter('');
            }}
            className="btn-clear-filters"
          >
            <span className="clear-icon">✕</span>
            Limpiar filtros
          </button>
        </div>
      </div>

      {/* Cards de Clientes */}
      {loading ? (
        <div className="loading">Cargando clientes...</div>
      ) : filteredClientes.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">👥</div>
          <h3>No se encontraron clientes</h3>
          <p>Comienza agregando el primer cliente del gimnasio</p>
          <Link to="/clientes/nuevo" className="btn btn-primary">
            + Crear primer cliente
          </Link>
        </div>
      ) : (
        <>
          <div className="clientes-grid">
            {filteredClientes.map(cliente => (
              <div key={cliente.id} className="cliente-card">
                {/* Header de la card */}
                <div className="cliente-card-header">
                  <div className="cliente-avatar">
                    <span>{cliente.nombre?.charAt(0)}{cliente.apellido_paterno?.charAt(0)}</span>
                  </div>
                  <div
                    className="cliente-estado-badge"
                    style={{ backgroundColor: getEstadoColor(cliente.estado) }}
                  >
                    {cliente.estado === 'activo' && '✓'}
                    {cliente.estado === 'inactivo' && '⏸️'}
                    {cliente.estado === 'suspendido' && '🚫'}
                    <span>{cliente.estado?.charAt(0).toUpperCase() + cliente.estado?.slice(1)}</span>
                  </div>
                </div>

                {/* Información del cliente */}
                <div className="cliente-info">
                  <h3 className="cliente-nombre">
                    {cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}
                  </h3>

                  <div className="cliente-detalles">
                    <div className="detalle-item">
                      <span className="detalle-icon">📞</span>
                      <span className="detalle-text">{cliente.telefono || 'Sin teléfono'}</span>
                    </div>

                    {cliente.email && (
                      <div className="detalle-item">
                        <span className="detalle-icon">📧</span>
                        <span className="detalle-text">{cliente.email}</span>
                      </div>
                    )}

                    <div className="detalle-item">
                      <span className="detalle-icon">📅</span>
                      <span className="detalle-text">
                        Registro: {new Date(cliente.fecha_registro).toLocaleDateString('es-MX')}
                      </span>
                    </div>

                    {cliente.objetivo_fitness && (
                      <div className="detalle-item">
                        <span className="detalle-icon">🎯</span>
                        <span className="detalle-text">{cliente.objetivo_fitness}</span>
                      </div>
                    )}
                  </div>

                  {/* Nivel de experiencia */}
                  <div className="cliente-nivel">
                    <div
                      className="nivel-badge"
                      style={{ backgroundColor: getNivelColor(cliente.nivel_experiencia) }}
                    >
                      <span>{getNivelIcon(cliente.nivel_experiencia)}</span>
                      <span>
                        {cliente.nivel_experiencia?.charAt(0).toUpperCase() + cliente.nivel_experiencia?.slice(1)}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Acciones */}
                <div className="cliente-actions">
                  <Link
                    to={`/clientes/${cliente.id}`}
                    className="btn-action btn-action-view"
                  >
                    <span className="action-icon">👁️</span>
                    <span className="action-text">Ver Detalle</span>
                  </Link>

                  <Link
                    to={`/clientes/editar/${cliente.id}`}
                    className="btn-action btn-action-edit"
                  >
                    <span className="action-icon">✏️</span>
                    <span className="action-text">Editar</span>
                  </Link>

                  <button
                    onClick={() => handleDelete(cliente.id)}
                    className="btn-action btn-action-delete"
                  >
                    <span className="action-icon">🗑️</span>
                    <span className="action-text">Eliminar</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="footer-info">
            <p>
              <span className="footer-icon">📊</span>
              Mostrando <strong>{filteredClientes.length}</strong> de <strong>{clientes.length}</strong> clientes
            </p>
          </div>
        </>
      )}
    </div>
  );
}

export default ClienteList;
