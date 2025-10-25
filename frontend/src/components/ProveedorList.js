import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import proveedorService from '../services/proveedorService';
import ConfirmModal from './ConfirmModal';
import './ProveedorList.css';

function ProveedorList() {
  const [proveedores, setProveedores] = useState([]);
  const [filteredProveedores, setFilteredProveedores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [proveedorToDelete, setProveedorToDelete] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProveedores();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    filterProveedores();
  }, [proveedores, searchTerm, statusFilter]);

  const fetchProveedores = async () => {
    try {
      setLoading(true);
      const response = await proveedorService.getProveedores();
      setProveedores(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar los proveedores');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const response = await proveedorService.getEstadisticas();
      setEstadisticas(response.data);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const filterProveedores = () => {
    let filtered = [...proveedores];

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(prov =>
        prov.nombre_empresa.toLowerCase().includes(term) ||
        (prov.nombre_contacto && prov.nombre_contacto.toLowerCase().includes(term)) ||
        (prov.telefono && prov.telefono.includes(term)) ||
        (prov.email && prov.email.toLowerCase().includes(term))
      );
    }

    if (statusFilter !== 'all') {
      const isActive = statusFilter === 'active';
      filtered = filtered.filter(prov => prov.activo === isActive);
    }

    setFilteredProveedores(filtered);
  };

  const handleDeleteClick = (proveedor) => {
    setProveedorToDelete(proveedor);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await proveedorService.deleteProveedor(proveedorToDelete.proveedor_id);
      setProveedores(proveedores.filter(p => p.proveedor_id !== proveedorToDelete.proveedor_id));
      setShowDeleteModal(false);
      setProveedorToDelete(null);
      showSuccessMessage('Proveedor eliminado exitosamente');
      fetchEstadisticas();
    } catch (err) {
      setError('Error al eliminar el proveedor');
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setProveedorToDelete(null);
  };

  const handleToggleActivo = async (proveedor) => {
    try {
      await proveedorService.toggleActivo(proveedor.proveedor_id);
      fetchProveedores();
      fetchEstadisticas();
      const msg = 'Proveedor ' + (proveedor.activo ? 'desactivado' : 'activado') + ' exitosamente';
      showSuccessMessage(msg);
    } catch (err) {
      setError('Error al cambiar el estado del proveedor');
      console.error(err);
    }
  };

  const showSuccessMessage = (message) => {
    const successModal = document.createElement('div');
    successModal.className = 'success-modal-overlay';
    successModal.innerHTML = '<div class="success-modal"><div class="success-icon">✓</div><h2>¡Éxito!</h2><p>' + message + '</p></div>';
    document.body.appendChild(successModal);
    setTimeout(() => successModal.remove(), 2000);
  };

  const getInitials = (nombre) => {
    const words = nombre.split(' ');
    if (words.length >= 2) {
      return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase();
    }
    return nombre.substring(0, 2).toUpperCase();
  };

  if (loading) {
    return <div className="loading">Cargando proveedores...</div>;
  }

  return (
    <div className="proveedor-list-container">
      <div className="header">
        <div>
          <h1>Gestión de Proveedores</h1>
          <p className="subtitle">Administración de proveedores de servicios</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/gestion-equipos/proveedores/new')}>
          + Nuevo Proveedor
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {estadisticas && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>📋</div>
            <div className="stat-content">
              <h3>{estadisticas.total_proveedores}</h3>
              <p>Total Proveedores</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>✓</div>
            <div className="stat-content">
              <h3>{estadisticas.proveedores_activos}</h3>
              <p>Activos</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)' }}>⏸</div>
            <div className="stat-content">
              <h3>{estadisticas.proveedores_inactivos}</h3>
              <p>Inactivos</p>
            </div>
          </div>
        </div>
      )}

      <div className="filters-container">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input type="text" placeholder="Buscar..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
        </div>
        <div className="filter-group">
          <button className={`filter-btn ${statusFilter === 'all' ? 'active' : ''}`} onClick={() => setStatusFilter('all')}>Todos</button>
          <button className={`filter-btn ${statusFilter === 'active' ? 'active' : ''}`} onClick={() => setStatusFilter('active')}>Activos</button>
          <button className={`filter-btn ${statusFilter === 'inactive' ? 'active' : ''}`} onClick={() => setStatusFilter('inactive')}>Inactivos</button>
        </div>
      </div>

      <div className="proveedores-grid">
        {filteredProveedores.length === 0 ? (
          <div className="no-data">No se encontraron proveedores</div>
        ) : (
          filteredProveedores.map((proveedor) => (
            <div key={proveedor.proveedor_id} className="proveedor-card">
              <div className="card-header-prov">
                <div className="proveedor-avatar">{getInitials(proveedor.nombre_empresa)}</div>
                <div className="proveedor-info">
                  <h3 className="proveedor-nombre">{proveedor.nombre_empresa}</h3>
                  <span className={`estado-badge ${proveedor.activo ? 'activo' : 'inactivo'}`}>
                    {proveedor.activo ? 'Activo' : 'Inactivo'}
                  </span>
                </div>
              </div>
              <div className="card-body-prov">
                {proveedor.nombre_contacto && (
                  <div className="info-item-prov">
                    <span className="info-icon">👤</span>
                    <span className="info-text">{proveedor.nombre_contacto}</span>
                  </div>
                )}
                <div className="info-item-prov">
                  <span className="info-icon">📱</span>
                  <span className="info-text">{proveedor.telefono}</span>
                </div>
                {proveedor.email && (
                  <div className="info-item-prov">
                    <span className="info-icon">📧</span>
                    <span className="info-text">{proveedor.email}</span>
                  </div>
                )}
              </div>
              <div className="card-actions-prov">
                <button className="btn-action btn-edit" onClick={() => navigate(`/gestion-equipos/proveedores/edit/${proveedor.proveedor_id}`)} title="Editar">
                  ✏️ Editar
                </button>
                <button className={`btn-action ${proveedor.activo ? 'btn-toggle-off' : 'btn-toggle-on'}`} onClick={() => handleToggleActivo(proveedor)} title={proveedor.activo ? 'Desactivar' : 'Activar'}>
                  {proveedor.activo ? '🔒' : '🔓'}
                </button>
                <button className="btn-action btn-delete" onClick={() => handleDeleteClick(proveedor)} title="Eliminar">
                  🗑️
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <ConfirmModal isOpen={showDeleteModal} onClose={handleCancelDelete} onConfirm={handleConfirmDelete} title="¿Eliminar proveedor?" message={`¿Estás seguro de que deseas eliminar a ${proveedorToDelete?.nombre_empresa}?`} confirmText="Eliminar" cancelText="Cancelar" type="danger" />
    </div>
  );
}

export default ProveedorList;
