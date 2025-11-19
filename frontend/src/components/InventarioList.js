import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import inventarioService from '../services/inventarioService';
import sedeService from '../services/sedeService';
import './Inventario.css';

function InventarioList() {
  const [inventario, setInventario] = useState([]);
  const [filteredInventario, setFilteredInventario] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [sedeFilter, setSedeFilter] = useState('');
  const [stockFilter, setStockFilter] = useState('todos');
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [editFormData, setEditFormData] = useState({
    cantidad_actual: '',
    cantidad_minima: '',
    cantidad_maxima: '',
    ubicacion_almacen: ''
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchInventario();
    fetchSedes();
  }, []);

  useEffect(() => {
    filterInventario();
  }, [inventario, searchTerm, sedeFilter, stockFilter]);

  const fetchInventario = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getInventario();
      setInventario(response.data);
    } catch (err) {
      console.error('Error al cargar inventario:', err);
      showNotif('Error al cargar el inventario', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const filterInventario = () => {
    let filtered = [...inventario];

    // Filtrar por sede
    if (sedeFilter) {
      filtered = filtered.filter(item => item.sede === parseInt(sedeFilter));
    }

    // Filtrar por stock
    if (stockFilter === 'con_stock') {
      filtered = filtered.filter(item => item.cantidad_actual > 0);
    } else if (stockFilter === 'sin_stock') {
      filtered = filtered.filter(item => item.cantidad_actual === 0);
    } else if (stockFilter === 'stock_bajo') {
      filtered = filtered.filter(item => item.cantidad_actual > 0 && item.cantidad_actual <= item.minimo);
    }

    // Filtrar por búsqueda
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(item =>
        item.producto?.nombre?.toLowerCase().includes(term) ||
        item.producto?.codigo?.toString().includes(term)
      );
    }

    setFilteredInventario(filtered);
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const handleEditClick = (item) => {
    setEditingItem(item);
    setEditFormData({
      cantidad_actual: item.cantidad_actual,
      cantidad_minima: item.cantidad_minima,
      cantidad_maxima: item.cantidad_maxima,
      ubicacion_almacen: item.ubicacion_almacen || ''
    });
    setShowEditModal(true);
  };

  const handleEditFormChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveEdit = async () => {
    if (!editingItem) return;

    try {
      setLoading(true);
      await inventarioService.updateInventario(editingItem.inventario_id, {
        producto_id: editingItem.producto.producto_id,
        sede: editingItem.sede,
        cantidad_actual: parseInt(editFormData.cantidad_actual),
        cantidad_minima: parseInt(editFormData.cantidad_minima),
        cantidad_maxima: parseInt(editFormData.cantidad_maxima),
        ubicacion_almacen: editFormData.ubicacion_almacen
      });

      showNotif('✓ Stock actualizado exitosamente', 'success');
      setShowEditModal(false);
      setEditingItem(null);
      await fetchInventario(); // Recargar inventario
    } catch (err) {
      console.error('Error al actualizar inventario:', err);
      showNotif('Error al actualizar el stock', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelEdit = () => {
    setShowEditModal(false);
    setEditingItem(null);
  };

  const getStockStatus = (cantidadActual, minimo) => {
    if (cantidadActual === 0) return { class: 'sin-stock', text: 'Sin Stock', color: '#ef4444' };
    if (cantidadActual <= minimo) return { class: 'stock-bajo', text: 'Stock Bajo', color: '#f59e0b' };
    return { class: 'con-stock', text: 'Normal', color: '#22c55e' };
  };

  const getSedeName = (sedeId) => {
    const sede = sedes.find(s => s.id === sedeId);
    return sede ? sede.nombre : 'N/A';
  };

  if (loading) {
    return (
      <div className="inventario-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando inventario...</p>
        </div>
      </div>
    );
  }

  const totalProductos = inventario.length;
  const productosSinStock = inventario.filter(item => item.cantidad_actual === 0).length;
  const productosStockBajo = inventario.filter(item => item.cantidad_actual > 0 && item.cantidad_actual <= item.cantidad_minima).length;
  const productosConStock = inventario.filter(item => item.cantidad_actual > item.cantidad_minima).length;

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
          <h1>📊 Inventario por Sede</h1>
          <p className="inventario-subtitle">Consulta el inventario disponible en cada sede</p>
        </div>
        <div style={{display: 'flex', gap: '1rem'}}>
          <button
            className="btn-primary"
            onClick={fetchInventario}
            disabled={loading}
          >
            🔄 {loading ? 'Actualizando...' : 'Actualizar'}
          </button>
          <button
            className="btn-secondary"
            onClick={() => navigate('/inventario/productos')}
          >
            ← Ver Productos
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
            <div className="stat-label">Total Registros</div>
            <div className="stat-value">{totalProductos}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            ✓
          </div>
          <div className="stat-content">
            <div className="stat-label">Stock Normal</div>
            <div className="stat-value">{productosConStock}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
            ⚠
          </div>
          <div className="stat-content">
            <div className="stat-label">Stock Bajo</div>
            <div className="stat-value">{productosStockBajo}</div>
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
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Buscar por producto o código..."
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
          <label htmlFor="sedeFilter">Sede:</label>
          <select
            id="sedeFilter"
            value={sedeFilter}
            onChange={(e) => setSedeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas</option>
            {sedes.map(sede => (
              <option key={sede.id} value={sede.id}>
                {sede.nombre}
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
            <option value="con_stock">Stock Normal</option>
            <option value="stock_bajo">Stock Bajo</option>
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
              <th>Producto</th>
              <th>Sede</th>
              <th className="text-center">Cantidad Actual</th>
              <th className="text-center">Stock Mínimo</th>
              <th className="text-center">Estado</th>
              <th className="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredInventario.length === 0 ? (
              <tr>
                <td colSpan="7" className="text-center empty-state">
                  <div className="empty-icon">📦</div>
                  <p>No se encontraron registros de inventario</p>
                </td>
              </tr>
            ) : (
              filteredInventario.map((item) => {
                const stockStatus = getStockStatus(item.cantidad_actual, item.cantidad_minima);
                return (
                  <tr key={item.inventario_id}>
                    <td className="font-mono">
                      {item.producto?.codigo || 'N/A'}
                    </td>
                    <td>
                      <div className="table-cell-main">{item.producto?.nombre || 'N/A'}</div>
                    </td>
                    <td>
                      <span className="badge badge-secondary">
                        {getSedeName(item.sede)}
                      </span>
                    </td>
                    <td className="text-center font-bold">
                      {item.cantidad_actual}
                    </td>
                    <td className="text-center text-muted">
                      {item.cantidad_minima}
                    </td>
                    <td className="text-center">
                      <span
                        className="stock-badge"
                        style={{ backgroundColor: stockStatus.color }}
                      >
                        {stockStatus.text}
                      </span>
                    </td>
                    <td className="text-center">
                      <button
                        className="btn-icon"
                        onClick={() => handleEditClick(item)}
                        title="Editar stock"
                      >
                        ✏️
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de Edición */}
      {showEditModal && editingItem && (
        <div className="modal-overlay" onClick={handleCancelEdit}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>✏️ Editar Stock</h2>
              <button className="modal-close" onClick={handleCancelEdit}>✕</button>
            </div>

            <div className="modal-body">
              <div className="modal-info">
                <p><strong>Producto:</strong> {editingItem.producto?.nombre}</p>
                <p><strong>Sede:</strong> {getSedeName(editingItem.sede)}</p>
                <p><strong>Código:</strong> {editingItem.producto?.codigo}</p>
              </div>

              <div className="form-grid">
                <div className="form-group">
                  <label htmlFor="cantidad_actual">
                    Cantidad Actual <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    id="cantidad_actual"
                    name="cantidad_actual"
                    value={editFormData.cantidad_actual}
                    onChange={handleEditFormChange}
                    min="0"
                    placeholder="0"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="cantidad_minima">
                    Stock Mínimo <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    id="cantidad_minima"
                    name="cantidad_minima"
                    value={editFormData.cantidad_minima}
                    onChange={handleEditFormChange}
                    min="0"
                    placeholder="5"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="cantidad_maxima">
                    Stock Máximo <span className="required">*</span>
                  </label>
                  <input
                    type="number"
                    id="cantidad_maxima"
                    name="cantidad_maxima"
                    value={editFormData.cantidad_maxima}
                    onChange={handleEditFormChange}
                    min="0"
                    placeholder="1000"
                  />
                </div>

                <div className="form-group full-width">
                  <label htmlFor="ubicacion_almacen">
                    Ubicación en Almacén
                  </label>
                  <input
                    type="text"
                    id="ubicacion_almacen"
                    name="ubicacion_almacen"
                    value={editFormData.ubicacion_almacen}
                    onChange={handleEditFormChange}
                    placeholder="Ej: Anaquel A3"
                  />
                  <small className="form-help">Ubicación física del producto en el almacén</small>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                className="btn-secondary"
                onClick={handleCancelEdit}
                disabled={loading}
              >
                Cancelar
              </button>
              <button
                className="btn-primary"
                onClick={handleSaveEdit}
                disabled={loading}
              >
                {loading ? 'Guardando...' : '💾 Guardar Cambios'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default InventarioList;
