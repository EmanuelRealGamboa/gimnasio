import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Plus, Pencil, Trash2 } from 'lucide-react';
import espacioService from '../services/espacioService';
import sedeService from '../services/sedeService';
import ConfirmModal from './ConfirmModal';
import './EspacioList.css';

function EspacioList() {
  const [espacios, setEspacios] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [filteredEspacios, setFilteredEspacios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSede, setSelectedSede] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [espacioToDelete, setEspacioToDelete] = useState(null);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    fetchSedes();
    fetchEspacios();
  }, []);

  useEffect(() => {
    // Si hay un parámetro de sede en la URL, seleccionarlo
    const sedeParam = searchParams.get('sede');
    if (sedeParam) {
      setSelectedSede(sedeParam);
    }
  }, [searchParams]);

  useEffect(() => {
    filterEspacios();
  }, [espacios, searchTerm, selectedSede]);

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchEspacios = async () => {
    try {
      setLoading(true);
      const response = await espacioService.getEspacios();
      setEspacios(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar los espacios');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filterEspacios = () => {
    let filtered = [...espacios];

    // Filtrar por sede
    if (selectedSede) {
      filtered = filtered.filter(espacio => espacio.sede.toString() === selectedSede);
    }

    // Filtrar por búsqueda
    if (searchTerm) {
      filtered = filtered.filter(espacio =>
        espacio.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        espacio.descripcion.toLowerCase().includes(searchTerm.toLowerCase()) ||
        espacio.sede_nombre.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredEspacios(filtered);
  };

  const handleDeleteClick = (espacio) => {
    setEspacioToDelete(espacio);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = async () => {
    try {
      await espacioService.deleteEspacio(espacioToDelete.id);
      setEspacios(espacios.filter(e => e.id !== espacioToDelete.id));
      setShowDeleteModal(false);
      setEspacioToDelete(null);
      showSuccessMessage('Espacio eliminado exitosamente');
    } catch (err) {
      setError('Error al eliminar el espacio');
      console.error(err);
      setShowDeleteModal(false);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setEspacioToDelete(null);
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
    return <div className="loading">Cargando espacios...</div>;
  }

  return (
    <div className="espacio-list-container">
      <div className="page-header">
        <h2>Gestión de Espacios</h2>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/espacios/new')}
        >
          <Plus size={18} />
          Nuevo Espacio
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="filters-container">
        <div className="search-box">
          <input
            type="text"
            placeholder="Buscar por nombre, descripción o sede..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
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
      </div>

      <div className="table-container">
        <table className="espacio-table">
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
                  <td className="espacio-nombre">{espacio.nombre}</td>
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
                      <Pencil size={18} />
                    </button>
                    <button
                      className="btn-action btn-delete"
                      onClick={() => handleDeleteClick(espacio)}
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
        title="¿Eliminar espacio?"
        message={`¿Estás seguro de que deseas eliminar el espacio "${espacioToDelete?.nombre}"? Esta acción no se puede deshacer.`}
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />
    </div>
  );
}

export default EspacioList;
