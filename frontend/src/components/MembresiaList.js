import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import membresiaService from '../services/membresiaService';
import ConfirmModal from './ConfirmModal';
import './MembresiaList.css';

function MembresiaList() {
  const [membresias, setMembresias] = useState([]);
  const [filteredMembresias, setFilteredMembresias] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [tipoFilter, setTipoFilter] = useState('');
  const [activoFilter, setActivoFilter] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [membresiaToDelete, setMembresiaToDelete] = useState(null);
  const [estadisticas, setEstadisticas] = useState(null);
  const navigate = useNavigate();

  const tiposMembresia = [
    { value: 'mensual', label: 'Mensual' },
    { value: 'trimestral', label: 'Trimestral' },
    { value: 'semestral', label: 'Semestral' },
    { value: 'anual', label: 'Anual' },
    { value: 'pase_dia', label: 'Pase del Día' },
    { value: 'pase_semana', label: 'Pase Semanal' }
  ];

  useEffect(() => {
    fetchMembresias();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    filterMembresias();
  }, [membresias, searchTerm, tipoFilter, activoFilter]);

  const fetchMembresias = async () => {
    try {
      setLoading(true);
      const response = await membresiaService.getMembresias();
      setMembresias(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar las membresías');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    try {
      const response = await membresiaService.getEstadisticas();
      setEstadisticas(response.data);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    }
  };

  const filterMembresias = () => {
    let filtered = [...membresias];

    if (tipoFilter) {
      filtered = filtered.filter(m => m.tipo === tipoFilter);
    }

    if (activoFilter !== '') {
      const isActivo = activoFilter === 'true';
      filtered = filtered.filter(m => m.activo === isActivo);
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(m =>
        m.nombre_plan.toLowerCase().includes(term)
      );
    }

    setFilteredMembresias(filtered);
  };

  const handleDeleteClick = (membresia) => {
    setMembresiaToDelete(membresia);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await membresiaService.deleteMembresia(membresiaToDelete.id);
      setMembresias(membresias.filter(m => m.id !== membresiaToDelete.id));
      setShowDeleteModal(false);
      setMembresiaToDelete(null);
      showSuccessMessage('Membresía eliminada exitosamente');
      fetchEstadisticas();
    } catch (err) {
      setError('Error al eliminar la membresía');
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleToggleActivo = async (membresia) => {
    try {
      await membresiaService.toggleActivo(membresia.id);
      fetchMembresias();
      fetchEstadisticas();
      showSuccessMessage(`Membresía ${membresia.activo ? 'desactivada' : 'activada'} exitosamente`);
    } catch (err) {
      setError('Error al cambiar estado de la membresía');
      console.error(err);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setMembresiaToDelete(null);
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

  const formatPrecio = (precio) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(precio);
  };

  if (loading) {
    return <div className="loading">Cargando membresías...</div>;
  }

  return (
    <div className="membresia-list-container">
      <div className="page-header">
        <div>
          <h2>Gestión de Membresías</h2>
          <p className="subtitle">Administra los planes de membresía del gimnasio</p>
        </div>
        <button
          className="btn-primary"
          onClick={() => navigate('/membresias/new')}
        >
          + Nueva Membresía
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {estadisticas && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
              📋
            </div>
            <div className="stat-content">
              <h3>{estadisticas.total_membresias}</h3>
              <p>Total Membresías</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
              ✓
            </div>
            <div className="stat-content">
              <h3>{estadisticas.activas}</h3>
              <p>Activas</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
              💰
            </div>
            <div className="stat-content">
              <h3>{formatPrecio(estadisticas.precio_promedio)}</h3>
              <p>Precio Promedio</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
              💎
            </div>
            <div className="stat-content">
              <h3>{formatPrecio(estadisticas.precio_maximo)}</h3>
              <p>Precio Máximo</p>
            </div>
          </div>
        </div>
      )}

      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="🔍 Buscar por nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-select">
          <select
            value={tipoFilter}
            onChange={(e) => setTipoFilter(e.target.value)}
          >
            <option value="">Todos los tipos</option>
            {tiposMembresia.map(tipo => (
              <option key={tipo.value} value={tipo.value}>{tipo.label}</option>
            ))}
          </select>
        </div>
        <div className="filter-select">
          <select
            value={activoFilter}
            onChange={(e) => setActivoFilter(e.target.value)}
          >
            <option value="">Todas</option>
            <option value="true">Activas</option>
            <option value="false">Inactivas</option>
          </select>
        </div>
      </div>

      <div className="table-container">
        <table className="membresia-table">
          <thead>
            <tr>
              <th>Nombre del Plan</th>
              <th>Tipo</th>
              <th>Precio</th>
              <th>Duración</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredMembresias.length === 0 ? (
              <tr>
                <td colSpan="6" className="no-data">
                  No se encontraron membresías
                </td>
              </tr>
            ) : (
              filteredMembresias.map((membresia) => (
                <tr key={membresia.id}>
                  <td className="membresia-nombre">{membresia.nombre_plan}</td>
                  <td>
                    <span className="badge-tipo">
                      {membresia.tipo_display}
                    </span>
                  </td>
                  <td style={{ fontWeight: '600', color: '#10b981' }}>
                    {formatPrecio(membresia.precio)}
                  </td>
                  <td>{membresia.duracion_dias ? `${membresia.duracion_dias} días` : 'N/A'}</td>
                  <td>
                    <span className={`badge-estado ${membresia.activo ? 'badge-activo' : 'badge-inactivo'}`}>
                      {membresia.activo ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="actions">
                    <button
                      className="btn-action btn-view"
                      onClick={() => handleToggleActivo(membresia)}
                      title={membresia.activo ? 'Desactivar' : 'Activar'}
                    >
                      {membresia.activo ? '🔒' : '🔓'}
                    </button>
                    <button
                      className="btn-action btn-edit"
                      onClick={() => navigate(`/membresias/edit/${membresia.id}`)}
                      title="Editar"
                    >
                      ✏️
                    </button>
                    <button
                      className="btn-action btn-delete"
                      onClick={() => handleDeleteClick(membresia)}
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

      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={handleCancelDelete}
        onConfirm={handleConfirmDelete}
        title="¿Eliminar membresía?"
        message={`¿Estás seguro de que deseas eliminar la membresía "${membresiaToDelete?.nombre_plan}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default MembresiaList;
