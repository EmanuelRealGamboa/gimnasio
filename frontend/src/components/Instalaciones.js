import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import sedeService from '../services/sedeService';
import espacioService from '../services/espacioService';
import ConfirmModal from './ConfirmModal';
import './Instalaciones.css';

function Instalaciones() {
  const [activeTab, setActiveTab] = useState('sedes');
  const [sedes, setSedes] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [filteredSedes, setFilteredSedes] = useState([]);
  const [filteredEspacios, setFilteredEspacios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSede, setSelectedSede] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [itemToDelete, setItemToDelete] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    if (activeTab === 'sedes') {
      filterSedes();
    } else {
      filterEspacios();
    }
  }, [sedes, espacios, searchTerm, selectedSede, activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sedesResponse, espaciosResponse] = await Promise.all([
        sedeService.getSedes(),
        espacioService.getEspacios()
      ]);
      setSedes(sedesResponse.data);
      setEspacios(espaciosResponse.data);
      setError('');
    } catch (err) {
      setError('Error al cargar los datos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filterSedes = () => {
    let filtered = [...sedes];
    if (searchTerm) {
      filtered = filtered.filter(sede =>
        sede.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        sede.direccion.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    setFilteredSedes(filtered);
  };

  const filterEspacios = () => {
    let filtered = [...espacios];
    if (selectedSede) {
      filtered = filtered.filter(espacio => espacio.sede.toString() === selectedSede);
    }
    if (searchTerm) {
      filtered = filtered.filter(espacio =>
        espacio.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        espacio.descripcion.toLowerCase().includes(searchTerm.toLowerCase()) ||
        espacio.sede_nombre.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    setFilteredEspacios(filtered);
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setSearchTerm('');
    setSelectedSede('');
  };

  const handleDeleteClick = (item, type) => {
    setItemToDelete({ ...item, type });
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      if (itemToDelete.type === 'sede') {
        await sedeService.deleteSede(itemToDelete.id);
        setSedes(sedes.filter(s => s.id !== itemToDelete.id));
        showSuccessMessage('Sede eliminada exitosamente');
      } else {
        await espacioService.deleteEspacio(itemToDelete.id);
        setEspacios(espacios.filter(e => e.id !== itemToDelete.id));
        showSuccessMessage('Espacio eliminado exitosamente');
      }
      setShowDeleteModal(false);
      setItemToDelete(null);
    } catch (err) {
      setError(`Error al eliminar ${itemToDelete.type === 'sede' ? 'la sede' : 'el espacio'}`);
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setItemToDelete(null);
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

  const getStats = () => {
    const totalSedes = sedes.length;
    const totalEspacios = espacios.length;
    const capacidadTotal = espacios.reduce((sum, e) => sum + e.capacidad, 0);
    return { totalSedes, totalEspacios, capacidadTotal };
  };

  const stats = getStats();

  if (loading) {
    return <div className="loading">Cargando instalaciones...</div>;
  }

  return (
    <div className="instalaciones-container">
      <div className="page-header">
        <div>
          <h2>Gestión de Instalaciones</h2>
          <p className="subtitle">Administra las sedes y espacios del gimnasio</p>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
            🏢
          </div>
          <div className="stat-content">
            <h3>{stats.totalSedes}</h3>
            <p>Sedes Totales</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
            📦
          </div>
          <div className="stat-content">
            <h3>{stats.totalEspacios}</h3>
            <p>Espacios Totales</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
            👥
          </div>
          <div className="stat-content">
            <h3>{stats.capacidadTotal}</h3>
            <p>Capacidad Total</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'sedes' ? 'active' : ''}`}
            onClick={() => handleTabChange('sedes')}
          >
            <span className="tab-icon">🏢</span>
            Sedes
          </button>
          <button
            className={`tab ${activeTab === 'espacios' ? 'active' : ''}`}
            onClick={() => handleTabChange('espacios')}
          >
            <span className="tab-icon">📦</span>
            Espacios
          </button>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => navigate(activeTab === 'sedes' ? '/sedes/new' : '/espacios/new')}
        >
          + Nuevo {activeTab === 'sedes' ? 'Sede' : 'Espacio'}
        </button>
      </div>

      {/* Filtros */}
      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder={`🔍 Buscar ${activeTab === 'sedes' ? 'sedes' : 'espacios'}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        {activeTab === 'espacios' && (
          <div className="filter-select">
            <select
              value={selectedSede}
              onChange={(e) => setSelectedSede(e.target.value)}
            >
              <option value="">Todas las sedes</option>
              {sedes.map((sede) => (
                <option key={sede.id} value={sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Contenido según el tab activo */}
      <div className="tab-content">
        {activeTab === 'sedes' ? (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Dirección</th>
                  <th>Teléfono</th>
                  <th>Espacios</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredSedes.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="no-data">
                      No se encontraron sedes
                    </td>
                  </tr>
                ) : (
                  filteredSedes.map((sede) => {
                    const espaciosDeSede = espacios.filter(e => e.sede === sede.id).length;
                    return (
                      <tr key={sede.id}>
                        <td className="item-nombre">{sede.nombre}</td>
                        <td>{sede.direccion}</td>
                        <td>{sede.telefono || 'N/A'}</td>
                        <td>
                          <span className="badge-count">{espaciosDeSede} espacios</span>
                        </td>
                        <td className="actions">
                          <button
                            className="btn-action btn-view"
                            onClick={() => {
                              setActiveTab('espacios');
                              setSelectedSede(sede.id.toString());
                            }}
                            title="Ver espacios"
                          >
                            🏢
                          </button>
                          <button
                            className="btn-action btn-edit"
                            onClick={() => navigate(`/sedes/edit/${sede.id}`)}
                            title="Editar"
                          >
                            ✏️
                          </button>
                          <button
                            className="btn-action btn-delete"
                            onClick={() => handleDeleteClick(sede, 'sede')}
                            title="Eliminar"
                          >
                            🗑️
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Sede</th>
                  <th>Capacidad</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredEspacios.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="no-data">
                      No se encontraron espacios
                    </td>
                  </tr>
                ) : (
                  filteredEspacios.map((espacio) => (
                    <tr key={espacio.id}>
                      <td className="item-nombre">{espacio.nombre}</td>
                      <td>{espacio.descripcion || 'N/A'}</td>
                      <td>
                        <span className="badge-sede">{espacio.sede_nombre}</span>
                      </td>
                      <td className="capacidad">{espacio.capacidad} personas</td>
                      <td className="actions">
                        <button
                          className="btn-action btn-edit"
                          onClick={() => navigate(`/espacios/edit/${espacio.id}`)}
                          title="Editar"
                        >
                          ✏️
                        </button>
                        <button
                          className="btn-action btn-delete"
                          onClick={() => handleDeleteClick(espacio, 'espacio')}
                          title="Eliminar"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title={`¿Eliminar ${itemToDelete?.type === 'sede' ? 'sede' : 'espacio'}?`}
        message={`¿Estás seguro de que deseas eliminar ${itemToDelete?.type === 'sede' ? 'la sede' : 'el espacio'} "${itemToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default Instalaciones;
