import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Plus, Building2, Pencil, Trash2 } from 'lucide-react';
import sedeService from '../services/sedeService';
import ConfirmModal from './ConfirmModal';
import './SedeList.css';

function SedeList() {
  const [sedes, setSedes] = useState([]);
  const [filteredSedes, setFilteredSedes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [sedeToDelete, setSedeToDelete] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSedes();
  }, []);

  useEffect(() => {
    filterSedes();
  }, [sedes, searchTerm]);

  const fetchSedes = async () => {
    try {
      setLoading(true);
      const response = await sedeService.getSedes();
      setSedes(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar las sedes');
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

  const handleDeleteClick = (sede) => {
    setSedeToDelete(sede);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await sedeService.deleteSede(sedeToDelete.id);
      setSedes(sedes.filter(s => s.id !== sedeToDelete.id));
      setShowDeleteModal(false);
      setSedeToDelete(null);
      showSuccessMessage('Sede eliminada exitosamente');
    } catch (err) {
      setError('Error al eliminar la sede');
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setSedeToDelete(null);
  };

  const showSuccessMessage = (message) => {
    const successModal = document.createElement('div');
    successModal.className = 'success-modal-overlay';
    successModal.innerHTML = `
      <div class="success-modal">
        <div class="success-icon"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>
        <h2>¡Éxito!</h2>
        <p>${message}</p>
      </div>
    `;
    document.body.appendChild(successModal);
    setTimeout(() => successModal.remove(), 2000);
  };

  if (loading) {
    return <div className="loading">Cargando sedes...</div>;
  }

  return (
    <div className="sede-list-container">
      <div className="page-header">
        <h2>Gestión de Sedes</h2>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/sedes/new')}
        >
          <Plus size={18} />
          Nueva Sede
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar por nombre o dirección..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="table-container">
        <table className="sede-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Dirección</th>
              <th>Teléfono</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {filteredSedes.length === 0 ? (
              <tr>
                <td colSpan="4" className="no-data">
                  No se encontraron sedes
                </td>
              </tr>
            ) : (
              filteredSedes.map((sede) => (
                <tr key={sede.id}>
                  <td className="sede-nombre">{sede.nombre}</td>
                  <td>{sede.direccion}</td>
                  <td>{sede.telefono || 'N/A'}</td>
                  <td className="actions">
                    <button
                      className="btn-action btn-view"
                      onClick={() => navigate(`/espacios?sede=${sede.id}`)}
                      title="Ver espacios"
                    >
                      <Building2 size={18} />
                    </button>
                    <button
                      className="btn-action btn-edit"
                      onClick={() => navigate(`/sedes/edit/${sede.id}`)}
                      title="Editar"
                    >
                      <Pencil size={18} />
                    </button>
                    <button
                      className="btn-action btn-delete"
                      onClick={() => handleDeleteClick(sede)}
                      title="Eliminar"
                    >
                      <Trash2 size={18} />
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
        title="¿Eliminar sede?"
        message={`¿Estás seguro de que deseas eliminar la sede "${sedeToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default SedeList;
