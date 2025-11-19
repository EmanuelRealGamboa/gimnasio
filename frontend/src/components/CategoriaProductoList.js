import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import inventarioService from '../services/inventarioService';
import ConfirmModal from './ConfirmModal';
import './Inventario.css';

function CategoriaProductoList() {
  const [categorias, setCategorias] = useState([]);
  const [filteredCategorias, setFilteredCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [categoriaToDelete, setCategoriaToDelete] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCategorias();
  }, []);

  useEffect(() => {
    filterCategorias();
  }, [categorias, searchTerm]);

  const fetchCategorias = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getCategorias();
      setCategorias(response.data);
    } catch (err) {
      console.error('Error al cargar categorías:', err);
      showNotif('Error al cargar las categorías', 'error');
    } finally {
      setLoading(false);
    }
  };

  const filterCategorias = () => {
    let filtered = [...categorias];

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(categoria =>
        categoria.nombre?.toLowerCase().includes(term)
      );
    }

    setFilteredCategorias(filtered);
  };

  const handleDeleteClick = (categoria) => {
    setCategoriaToDelete(categoria);
    setShowConfirmModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!categoriaToDelete) return;

    try {
      await inventarioService.deleteCategoria(categoriaToDelete.categoria_producto_id);
      showNotif('✓ Categoría eliminada exitosamente', 'success');
      setShowConfirmModal(false);
      setCategoriaToDelete(null);
      fetchCategorias();
    } catch (err) {
      console.error('Error al eliminar:', err);
      showNotif('Error al eliminar la categoría', 'error');
      setShowConfirmModal(false);
      setCategoriaToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
    setCategoriaToDelete(null);
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  if (loading) {
    return (
      <div className="inventario-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando categorías...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="inventario-container">
      {/* Notification */}
      {showNotification && (
        <div className={`notification ${notificationType} show`}>
          {notificationMessage}
        </div>
      )}

      {/* Header */}
      <div className="inventario-header">
        <div>
          <h1>📦 Categorías de Productos</h1>
          <p className="inventario-subtitle">Gestiona las categorías de tu inventario</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => navigate('/inventario/categorias/new')}
        >
          <span>➕</span> Nueva Categoría
        </button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #666666 0%, #2a2a2a 100%)' }}>
            📦
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Categorías</div>
            <div className="stat-value">{categorias.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            🔍
          </div>
          <div className="stat-content">
            <div className="stat-label">Filtradas</div>
            <div className="stat-value">{filteredCategorias.length}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por nombre de categoría..."
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
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre</th>
              <th className="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredCategorias.length === 0 ? (
              <tr>
                <td colSpan="3" className="text-center empty-state">
                  <div className="empty-icon">📦</div>
                  <p>No se encontraron categorías</p>
                  <button
                    className="btn-primary"
                    onClick={() => navigate('/inventario/categorias/new')}
                  >
                    Crear Primera Categoría
                  </button>
                </td>
              </tr>
            ) : (
              filteredCategorias.map((categoria) => (
                <tr key={categoria.categoria_producto_id}>
                  <td className="font-mono">#{categoria.categoria_producto_id}</td>
                  <td>
                    <div className="table-cell-main">{categoria.nombre}</div>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-action btn-action-edit"
                        onClick={() => navigate(`/inventario/categorias/edit/${categoria.categoria_producto_id}`)}
                        title="Editar"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-action btn-action-delete"
                        onClick={() => handleDeleteClick(categoria)}
                        title="Eliminar"
                      >
                        🗑️
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Confirm Delete Modal */}
      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Eliminar Categoría"
        message={`¿Estás seguro de que deseas eliminar la categoría "${categoriaToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default CategoriaProductoList;
