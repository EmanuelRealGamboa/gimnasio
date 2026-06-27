import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ClipboardList,
  CheckCircle2,
  DollarSign,
  Gem,
  Ticket,
  CreditCard,
  Building2,
  Star,
  Calendar,
  Target,
  Lock,
  Unlock,
  Pencil,
  Trash2,
  Plus,
} from 'lucide-react';
import membresiaService from '../services/membresiaService';
import instalacionesService from '../services/instalacionesService';
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
  const [sedeFilter, setSedeFilter] = useState('');
  const [sedes, setSedes] = useState([]);
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
    fetchSedes();
    fetchMembresias();
    fetchEstadisticas();
  }, []);

  useEffect(() => {
    filterMembresias();
  }, [membresias, searchTerm, tipoFilter, activoFilter, sedeFilter]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

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

    if (sedeFilter) {
      filtered = filtered.filter(m => {
        // Mostrar membresías multi-sede o de la sede seleccionada
        return m.permite_todas_sedes || m.sede === parseInt(sedeFilter);
      });
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
        <div class="success-icon"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>
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
          <Plus size={18} /> Nueva Membresía
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {estadisticas && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)' }}>
              <ClipboardList size={26} />
            </div>
            <div className="stat-content">
              <h3>{estadisticas.total_membresias}</h3>
              <p>Total Membresías</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
              <CheckCircle2 size={26} />
            </div>
            <div className="stat-content">
              <h3>{estadisticas.activas}</h3>
              <p>Activas</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
              <DollarSign size={26} />
            </div>
            <div className="stat-content">
              <h3>{formatPrecio(estadisticas.precio_promedio)}</h3>
              <p>Precio Promedio</p>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%)' }}>
              <Gem size={26} />
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
            placeholder="Buscar por nombre..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-select">
          <select
            value={sedeFilter}
            onChange={(e) => setSedeFilter(e.target.value)}
          >
            <option value="">Todas las sedes</option>
            {sedes.map(sede => (
              <option key={sede.id} value={sede.id}>{sede.nombre}</option>
            ))}
          </select>
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

      {filteredMembresias.length === 0 ? (
        <div className="no-data-container">
          <div className="no-data-icon"><Ticket size={48} /></div>
          <p>No se encontraron membresías</p>
        </div>
      ) : (
        <div className="membresias-grid">
          {filteredMembresias.map((membresia) => (
            <div key={membresia.id} className="membresia-card">
              {/* Header: Icono y Badge de Estado */}
              <div className="membresia-card-header">
                <div className="membresia-avatar">
                  <span className="avatar-icon"><CreditCard size={26} /></span>
                </div>
                <span className={`badge-estado-top ${membresia.activo ? 'badge-activo' : 'badge-inactivo'}`}>
                  {membresia.activo ? <><CheckCircle2 size={14} /> ACTIVO</> : 'INACTIVO'}
                </span>
              </div>

              {/* Título del Plan */}
              <div className="membresia-card-title">
                <h3>{membresia.nombre_plan}</h3>
              </div>

              {/* Información con Iconos */}
              <div className="membresia-card-info">
                <div className="info-row">
                  <span className="info-icon"><Building2 size={20} /></span>
                  <div className="info-content">
                    {membresia.permite_todas_sedes ? (
                      <span className="badge-multi-sede"><Star size={16} /> Todas las sedes</span>
                    ) : (
                      <span>{membresia.sede_nombre || 'N/A'}</span>
                    )}
                  </div>
                </div>

                <div className="info-row">
                  <span className="info-icon"><DollarSign size={20} /></span>
                  <div className="info-content">
                    <span className="info-value-highlight">{formatPrecio(membresia.precio)}</span>
                  </div>
                </div>

                <div className="info-row">
                  <span className="info-icon"><Calendar size={20} /></span>
                  <div className="info-content">
                    <span>Duración: {membresia.duracion_dias ? `${membresia.duracion_dias} días` : 'N/A'}</span>
                  </div>
                </div>

                <div className="info-row">
                  <span className="info-icon"><Target size={20} /></span>
                  <div className="info-content">
                    <span>Espacios: {membresia.espacios_count || 0}</span>
                  </div>
                </div>
              </div>

              {/* Badge de Tipo */}
              <div className="membresia-card-type">
                <span className="badge-tipo-plan">{membresia.tipo_display}</span>
              </div>

              {/* Separador */}
              <div className="card-divider"></div>

              {/* Botones de Acción */}
              <div className="membresia-card-actions">
                <button
                  className="btn-action-detailed btn-view"
                  onClick={() => handleToggleActivo(membresia)}
                  title={membresia.activo ? 'Desactivar' : 'Activar'}
                >
                  <span className="btn-icon">{membresia.activo ? <Lock size={18} /> : <Unlock size={18} />}</span>
                  <span className="btn-text">{membresia.activo ? 'Desactivar' : 'Activar'}</span>
                </button>

                <button
                  className="btn-action-detailed btn-edit"
                  onClick={() => navigate(`/membresias/edit/${membresia.id}`)}
                  title="Editar"
                >
                  <span className="btn-icon"><Pencil size={18} /></span>
                  <span className="btn-text">Editar</span>
                </button>

                <button
                  className="btn-action-detailed btn-delete"
                  onClick={() => handleDeleteClick(membresia)}
                  title="Eliminar"
                >
                  <span className="btn-icon"><Trash2 size={18} /></span>
                  <span className="btn-text">Eliminar</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

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
