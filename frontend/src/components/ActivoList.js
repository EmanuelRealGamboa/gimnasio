import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { activoService, categoriaActivoService } from '../services/gestionEquiposService';
import './GestionEquipos.css';

const ActivoList = () => {
  const [activos, setActivos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState({
    search: '',
    categoria: '',
    estado: '',
  });

  useEffect(() => {
    cargarDatos();
    cargarCategorias();
  }, []);

  useEffect(() => {
    aplicarFiltros();
  }, [filtros]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const response = await activoService.getAll();
      setActivos(response.data);
    } catch (error) {
      console.error('Error al cargar activos:', error);
      alert('Error al cargar los activos');
    } finally {
      setLoading(false);
    }
  };

  const cargarCategorias = async () => {
    try {
      const response = await categoriaActivoService.getAll();
      setCategorias(response.data);
    } catch (error) {
      console.error('Error al cargar categorías:', error);
    }
  };

  const aplicarFiltros = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filtros.search) params.search = filtros.search;
      if (filtros.categoria) params.categoria = filtros.categoria;
      if (filtros.estado) params.estado = filtros.estado;

      const response = await activoService.getAll(params);
      setActivos(response.data);
    } catch (error) {
      console.error('Error al filtrar:', error);
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

  const handleEliminar = async (id, codigo) => {
    if (window.confirm(`¿Estás seguro de eliminar el activo ${codigo}?`)) {
      try {
        await activoService.delete(id);
        showSuccessMessage('Activo eliminado exitosamente');
        cargarDatos();
      } catch (error) {
        console.error('Error al eliminar:', error);
        alert('Error al eliminar el activo');
      }
    }
  };

  const handleCambiarEstado = async (id, nuevoEstado) => {
    try {
      await activoService.cambiarEstado(id, nuevoEstado);
      showSuccessMessage('Estado actualizado exitosamente');
      cargarDatos();
    } catch (error) {
      console.error('Error al cambiar estado:', error);
      alert('Error al cambiar el estado');
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const getEstadoBadgeClass = (estado) => {
    const classes = {
      'activo': 'badge-success',
      'mantenimiento': 'badge-warning',
      'baja': 'badge-danger',
      'inactivo': 'badge-secondary'
    };
    return classes[estado] || 'badge-secondary';
  };

  return (
    <div className="activo-list-container">
      <div className="header">
        <div>
          <h1>Gestión de Activos</h1>
          <p className="subtitle">Inventario de equipos y bienes del gimnasio</p>
        </div>
        <Link to="/gestion-equipos/activos/new" className="btn btn-primary">
          + Nuevo Activo
        </Link>
      </div>

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por código, nombre, marca, modelo..."
            value={filtros.search}
            onChange={(e) => setFiltros({ ...filtros, search: e.target.value })}
            className="search-input"
          />
        </div>

        <div className="filters-row">
          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">📁</span>
              Categoría
            </label>
            <select
              value={filtros.categoria}
              onChange={(e) => setFiltros({ ...filtros, categoria: e.target.value })}
              className="filter-select"
            >
              <option value="">Todas las categorías</option>
              {categorias.map(cat => (
                <option key={cat.categoria_activo_id} value={cat.categoria_activo_id}>
                  {cat.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">
              <span className="filter-icon">🔄</span>
              Estado
            </label>
            <select
              value={filtros.estado}
              onChange={(e) => setFiltros({ ...filtros, estado: e.target.value })}
              className="filter-select"
            >
              <option value="">Todos los estados</option>
              <option value="activo">✓ Activo</option>
              <option value="mantenimiento">🔧 En Mantenimiento</option>
              <option value="inactivo">⏸️ Inactivo</option>
              <option value="baja">🚫 Dado de Baja</option>
            </select>
          </div>

          <button
            onClick={() => setFiltros({ search: '', categoria: '', estado: '' })}
            className="btn-clear-filters"
          >
            <span className="clear-icon">✕</span>
            Limpiar filtros
          </button>
        </div>
      </div>

      {/* Cards de activos */}
      {loading ? (
        <div className="loading">Cargando activos...</div>
      ) : activos.length === 0 ? (
        <div className="empty-state">
          <p>No se encontraron activos</p>
          <Link to="/gestion-equipos/activos/new" className="btn btn-primary">
            Crear primer activo
          </Link>
        </div>
      ) : (
        <>
          <div className="activos-grid">
            {activos.map(activo => (
              <div key={activo.activo_id} className="activo-card">
                <div className="activo-card-header">
                  <div className="activo-codigo">{activo.codigo}</div>
                  <span className={`badge-estado ${getEstadoBadgeClass(activo.estado)}`}>
                    {activo.estado_display}
                  </span>
                </div>

                {/* Imagen del activo */}
                <div className="activo-card-image">
                  {activo.imagen ? (
                    <img
                      src={activo.imagen.startsWith('http') ? activo.imagen : `https://carefree-fulfillment-production.up.railway.app${activo.imagen}`}
                      alt={activo.nombre}
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = 'https://via.placeholder.com/400x250/1e293b/60a5fa?text=Sin+Imagen';
                      }}
                    />
                  ) : (
                    <div className="activo-card-placeholder">
                      <span className="placeholder-icon">
                        {activo.categoria_nombre?.includes('Cardiovascular') ? '🏃' :
                         activo.categoria_nombre?.includes('Fuerza') ? '💪' :
                         activo.categoria_nombre?.includes('Pesas') ? '🏋️' :
                         activo.categoria_nombre?.includes('Funcional') ? '🤸' :
                         activo.categoria_nombre?.includes('Mobiliario') ? '🪑' : '📦'}
                      </span>
                      <span className="placeholder-text">Sin Imagen</span>
                    </div>
                  )}
                </div>

                <div className="activo-card-body">
                  <h3 className="activo-nombre">
                    <Link to={`/gestion-equipos/activos/${activo.activo_id}`}>
                      {activo.nombre}
                    </Link>
                  </h3>

                  <div className="activo-info-simple">
                    <div className="info-row">
                      <span className="info-icon">📁</span>
                      <span className="info-text">{activo.categoria_nombre}</span>
                    </div>

                    {activo.marca && (
                      <div className="info-row">
                        <span className="info-icon">🏷️</span>
                        <span className="info-text">{activo.marca} {activo.modelo ? `- ${activo.modelo}` : ''}</span>
                      </div>
                    )}

                    <div className="info-row">
                      <span className="info-icon">🏢</span>
                      <span className="info-text">{activo.sede_nombre}</span>
                    </div>

                    <div className="info-row">
                      <span className="info-icon">💰</span>
                      <span className="info-text">{formatCurrency(activo.valor)}</span>
                    </div>
                  </div>

                  {/* Alertas importantes */}
                  {activo.proximo_mantenimiento && activo.proximo_mantenimiento.dias_restantes <= 15 && (
                    <div className="mantenimiento-badge">
                      <span className="badge-icon">🔧</span>
                      <span>Mantenimiento en {activo.proximo_mantenimiento.dias_restantes} días</span>
                    </div>
                  )}

                  {activo.en_mantenimiento && (
                    <div className="en-mantenimiento-badge">
                      <span className="badge-icon">⚠️</span>
                      <span>En mantenimiento</span>
                    </div>
                  )}
                </div>

                <div className="activo-card-footer">
                  <Link
                    to={`/gestion-equipos/activos/${activo.activo_id}`}
                    className="btn-ver-detalles"
                  >
                    <span className="btn-icon">📋</span>
                    <span className="btn-text">Ver Detalles Completos</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <div className="footer-info">
            <p>Total de activos: {activos.length}</p>
          </div>
        </>
      )}
    </div>
  );
};

export default ActivoList;
