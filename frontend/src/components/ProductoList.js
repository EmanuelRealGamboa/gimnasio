import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import inventarioService from '../services/inventarioService';
import ConfirmModal from './ConfirmModal';
import './Inventario.css';

function ProductoList() {
  const [productos, setProductos] = useState([]);
  const [filteredProductos, setFilteredProductos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoriaFilter, setCategoriaFilter] = useState('');
  const [stockFilter, setStockFilter] = useState('todos');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [productoToDelete, setProductoToDelete] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProductos();
    fetchCategorias();
  }, []);

  useEffect(() => {
    filterProductos();
  }, [productos, searchTerm, categoriaFilter, stockFilter]);

  const fetchProductos = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getProductos();
      setProductos(response.data);
    } catch (err) {
      console.error('Error al cargar productos:', err);
      showNotif('Error al cargar los productos', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategorias = async () => {
    try {
      const response = await inventarioService.getCategorias();
      setCategorias(response.data);
    } catch (err) {
      console.error('Error al cargar categorías:', err);
    }
  };

  const filterProductos = () => {
    let filtered = [...productos];

    // Filtrar por categoría
    if (categoriaFilter) {
      filtered = filtered.filter(p => p.categoria.toString() === categoriaFilter);
    }

    // Filtrar por stock
    if (stockFilter === 'con_stock') {
      filtered = filtered.filter(p => (p.stock_total || 0) > 0);
    } else if (stockFilter === 'sin_stock') {
      filtered = filtered.filter(p => (p.stock_total || 0) === 0);
    }

    // Filtrar por búsqueda
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(p =>
        p.nombre?.toLowerCase().includes(term) ||
        p.codigo?.toString().includes(term)
      );
    }

    setFilteredProductos(filtered);
  };

  const handleDeleteClick = (producto) => {
    setProductoToDelete(producto);
    setShowConfirmModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!productoToDelete) return;

    try {
      await inventarioService.deleteProducto(productoToDelete.producto_id);
      showNotif('✓ Producto eliminado exitosamente', 'success');
      setShowConfirmModal(false);
      setProductoToDelete(null);
      fetchProductos();
    } catch (err) {
      console.error('Error al eliminar:', err);

      // Detectar si es un error de protección por ventas asociadas
      const errorMsg = err.response?.data?.detail || err.message || '';
      if (errorMsg.includes('protected') || errorMsg.includes('referenced') || err.response?.status === 500) {
        showNotif('⚠️ No se puede eliminar: el producto tiene ventas asociadas. Puedes desactivarlo en su lugar.', 'error');
      } else {
        showNotif('Error al eliminar el producto', 'error');
      }

      setShowConfirmModal(false);
      setProductoToDelete(null);
    }
  };

  const handleCancelDelete = () => {
    setShowConfirmModal(false);
    setProductoToDelete(null);
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const getStockStatus = (stock) => {
    if (stock === 0) return { class: 'sin-stock', text: 'Sin Stock', color: '#ef4444' };
    if (stock < 10) return { class: 'stock-bajo', text: 'Stock Bajo', color: '#f59e0b' };
    return { class: 'con-stock', text: 'Disponible', color: '#22c55e' };
  };

  const getCategoriaName = (categoriaId) => {
    const cat = categorias.find(c => c.categoria_producto_id === categoriaId);
    return cat ? cat.nombre : 'N/A';
  };

  if (loading) {
    return (
      <div className="inventario-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando productos...</p>
        </div>
      </div>
    );
  }

  const totalStock = productos.reduce((sum, p) => sum + (p.stock_total || 0), 0);
  const productosSinStock = productos.filter(p => (p.stock_total || 0) === 0).length;
  const productosConStock = productos.filter(p => (p.stock_total || 0) > 0).length;

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
          <h1>📦 Productos</h1>
          <p className="inventario-subtitle">Gestiona los productos de tu inventario</p>
        </div>
        <div className="header-actions">
          <button
            className="btn-secondary"
            onClick={() => navigate('/inventario/categorias')}
          >
            📂 Categorías
          </button>
          <button
            className="btn-primary"
            onClick={() => navigate('/inventario/productos/new')}
          >
            <span>➕</span> Nuevo Producto
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)' }}>
            📦
          </div>
          <div className="stat-content">
            <div className="stat-label">Total Productos</div>
            <div className="stat-value">{productos.length}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            ✓
          </div>
          <div className="stat-content">
            <div className="stat-label">Con Stock</div>
            <div className="stat-value">{productosConStock}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
            ✗
          </div>
          <div className="stat-content">
            <div className="stat-label">Sin Stock</div>
            <div className="stat-value">{productosSinStock}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
            📊
          </div>
          <div className="stat-content">
            <div className="stat-label">Stock Total</div>
            <div className="stat-value">{totalStock}</div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por nombre o código..."
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

        <div className="filter-group">
          <label htmlFor="categoriaFilter">Categoría:</label>
          <select
            id="categoriaFilter"
            value={categoriaFilter}
            onChange={(e) => setCategoriaFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas</option>
            {categorias.map(cat => (
              <option key={cat.categoria_producto_id} value={cat.categoria_producto_id}>
                {cat.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="stockFilter">Stock:</label>
          <select
            id="stockFilter"
            value={stockFilter}
            onChange={(e) => setStockFilter(e.target.value)}
            className="filter-select"
          >
            <option value="todos">Todos</option>
            <option value="con_stock">Con Stock</option>
            <option value="sin_stock">Sin Stock</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th className="text-right">Precio</th>
              <th className="text-center">Stock</th>
              <th className="text-center">Estado</th>
              <th className="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredProductos.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center empty-state">
                  <div className="empty-icon">📦</div>
                  <p>No se encontraron productos</p>
                  <button
                    className="btn-primary"
                    onClick={() => navigate('/inventario/productos/new')}
                  >
                    Crear Primer Producto
                  </button>
                </td>
              </tr>
            ) : (
              filteredProductos.map((producto) => {
                const stock = producto.stock_total || 0;
                const stockStatus = getStockStatus(stock);
                return (
                  <tr key={producto.producto_id}>
                    <td className="font-mono">
                      {producto.codigo || 'N/A'}
                    </td>
                    <td>
                      <div className="table-cell-main">{producto.nombre}</div>
                    </td>
                    <td>
                      <span className="badge badge-secondary">
                        {getCategoriaName(producto.categoria)}
                      </span>
                    </td>
                    <td className="text-right font-mono">
                      ${producto.precio_unitario ? parseFloat(producto.precio_unitario).toFixed(2) : '0.00'}
                    </td>
                    <td className="text-center font-bold">
                      {stock}
                    </td>
                    <td className="text-center">
                      <span
                        className="stock-badge"
                        style={{ backgroundColor: stockStatus.color }}
                      >
                        {stockStatus.text}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn-action btn-action-edit"
                          onClick={() => navigate(`/inventario/productos/edit/${producto.producto_id}`)}
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn-action btn-action-delete"
                          onClick={() => handleDeleteClick(producto)}
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Confirm Delete Modal */}
      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="Eliminar Producto"
        message={`¿Estás seguro de que deseas eliminar el producto "${productoToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default ProductoList;
