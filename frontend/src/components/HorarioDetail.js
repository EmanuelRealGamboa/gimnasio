import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Loader,
  ArrowLeft,
  Calendar,
  Pencil,
  Trash2,
  CheckCircle2,
  PauseCircle,
  XCircle,
  ClipboardList,
  MapPin,
  CalendarDays,
  BarChart3,
  FileText,
  ArrowRight,
  Clock,
} from 'lucide-react';
import horariosService from '../services/horariosService';
import ConfirmModal from './ConfirmModal';
import './HorarioDetail.css';

const HorarioDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [horario, setHorario] = useState(null);
  const [sesiones, setSesiones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modales de confirmación
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [horarioData, sesionesData] = await Promise.all([
        horariosService.getHorario(id),
        horariosService.getSesiones({ horario: id }),
      ]);

      setHorario(horarioData);
      setSesiones(Array.isArray(sesionesData) ? sesionesData : sesionesData.results || []);
      setError(null);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setError('Error al cargar el horario');
    } finally {
      setLoading(false);
    }
  };

  const formatFecha = (fecha) => {
    if (!fecha) return 'No definida';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatHora = (hora) => {
    if (!hora) return '';
    return hora.substring(0, 5); // HH:MM
  };

  const getDiaColor = (dia) => {
    const colores = {
      lunes: '#3b82f6',
      martes: '#10b981',
      miercoles: '#f59e0b',
      jueves: '#8b5cf6',
      viernes: '#ec4899',
      sabado: '#06b6d4',
      domingo: '#ef4444',
    };
    return colores[dia] || '#6b7280';
  };

  const confirmarEliminar = () => {
    setShowDeleteModal(true);
  };

  const handleEliminar = async () => {
    try {
      await horariosService.deleteHorario(id);
      setShowDeleteModal(false);
      setSuccessMessage('Horario eliminado exitosamente');
      setShowSuccessModal(true);
      // Navegar después de mostrar el modal de éxito
      setTimeout(() => {
        navigate('/horarios');
      }, 1500);
    } catch (error) {
      console.error('Error al eliminar horario:', error);
      setShowDeleteModal(false);
      setErrorMessage(error.response?.data?.error || error.message || 'Error al eliminar el horario');
      setShowErrorModal(true);
    }
  };

  if (loading) {
    return (
      <div className="horario-detail-container">
        <div className="loading-spinner">
          <span className="spinner"><Loader size={24} /></span>
          <p>Cargando horario...</p>
        </div>
      </div>
    );
  }

  if (error || !horario) {
    return (
      <div className="horario-detail-container">
        <div className="alert alert-error">
          <span>{error || 'Horario no encontrado'}</span>
          <button className="btn-secondary" onClick={() => navigate('/horarios')}>
            <ArrowLeft size={18} /> Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="horario-detail-container">
      {/* Header */}
      <div className="detail-header">
        <div>
          <h2>
            <span className="header-icon"><Calendar size={20} /></span>
            Detalle del Horario
          </h2>
          <p className="subtitle">{horario.tipo_actividad_nombre}</p>
        </div>
        <div className="header-actions">
          <button className="btn-secondary" onClick={() => navigate('/horarios')}>
            <ArrowLeft size={18} /> Volver
          </button>
          <button className="btn-edit" onClick={() => navigate(`/horarios/edit/${id}`)}>
            <Pencil size={18} /> Editar
          </button>
          {horario.estado === 'activo' && (
            <button className="btn-danger" onClick={confirmarEliminar}>
              <Trash2 size={18} /> Eliminar
            </button>
          )}
        </div>
      </div>

      {/* Estado Banner */}
      <div className={`estado-banner estado-${horario.estado}`}>
        <div className="estado-content">
          <span className="estado-icon">
            {horario.estado === 'activo' && <CheckCircle2 size={22} style={{ color: 'var(--success)' }} />}
            {horario.estado === 'suspendido' && <PauseCircle size={22} style={{ color: 'var(--warning)' }} />}
            {horario.estado === 'cancelado' && <XCircle size={22} style={{ color: 'var(--danger)' }} />}
          </span>
          <span className="estado-text">
            {horario.estado === 'activo' && 'Horario Activo'}
            {horario.estado === 'suspendido' && 'Horario Suspendido'}
            {horario.estado === 'cancelado' && 'Horario Cancelado'}
          </span>
        </div>
      </div>

      {/* Información Principal */}
      <div className="detail-grid">
        {/* Card: Información General */}
        <div className="detail-card">
          <div className="card-header">
            <h3><ClipboardList size={18} /> Información General</h3>
          </div>
          <div className="card-body">
            <div className="info-row">
              <span className="info-label">Tipo de Actividad:</span>
              <span className="info-value">{horario.tipo_actividad_nombre}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Día de la Semana:</span>
              <span className="badge-dia" style={{ backgroundColor: getDiaColor(horario.dia_semana) }}>
                {horario.dia_semana?.charAt(0).toUpperCase() + horario.dia_semana?.slice(1)}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Horario:</span>
              <div className="horario-display">
                <span className="hora-inicio">{formatHora(horario.hora_inicio)}</span>
                <span className="separador"><ArrowRight size={16} /></span>
                <span className="hora-fin">{formatHora(horario.hora_fin)}</span>
              </div>
            </div>
            <div className="info-row">
              <span className="info-label">Cupo Máximo:</span>
              <span className="info-value badge-cupo">{horario.cupo_maximo} personas</span>
            </div>
          </div>
        </div>

        {/* Card: Ubicación y Personal */}
        <div className="detail-card">
          <div className="card-header">
            <h3><MapPin size={18} /> Ubicación y Personal</h3>
          </div>
          <div className="card-body">
            <div className="info-row">
              <span className="info-label">Sede:</span>
              <span className="badge-sede">{horario.sede_nombre}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Espacio:</span>
              <span className="info-value">{horario.espacio_nombre}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Entrenador:</span>
              <span className="info-value">{horario.entrenador_nombre}</span>
            </div>
          </div>
        </div>

        {/* Card: Vigencia */}
        <div className="detail-card">
          <div className="card-header">
            <h3><CalendarDays size={18} /> Vigencia</h3>
          </div>
          <div className="card-body">
            <div className="info-row">
              <span className="info-label">Fecha Inicio:</span>
              <span className="info-value">{formatFecha(horario.fecha_inicio)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Fecha Fin:</span>
              <span className="info-value">{formatFecha(horario.fecha_fin)}</span>
            </div>
          </div>
        </div>

        {/* Card: Estadísticas */}
        <div className="detail-card">
          <div className="card-header">
            <h3><BarChart3 size={18} /> Estadísticas</h3>
          </div>
          <div className="card-body">
            <div className="info-row">
              <span className="info-label">Total de Sesiones:</span>
              <span className="info-value badge-count">{sesiones.length}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Sesiones Activas:</span>
              <span className="info-value badge-count">
                {sesiones.filter((s) => s.estado === 'programada').length}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Creado:</span>
              <span className="info-value info-small">{formatFecha(horario.fecha_creacion)}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Última modificación:</span>
              <span className="info-value info-small">{formatFecha(horario.fecha_modificacion)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Observaciones */}
      {horario.observaciones && (
        <div className="detail-card">
          <div className="card-header">
            <h3><FileText size={18} /> Observaciones</h3>
          </div>
          <div className="card-body">
            <p className="observaciones-text">{horario.observaciones}</p>
          </div>
        </div>
      )}

      {/* Sesiones Recientes */}
      <div className="detail-card">
        <div className="card-header">
          <h3><Calendar size={18} /> Sesiones Recientes</h3>
        </div>
        <div className="card-body">
          {sesiones.length === 0 ? (
            <div className="no-data">
              <p>No hay sesiones programadas para este horario</p>
            </div>
          ) : (
            <div className="sesiones-list">
              {sesiones.slice(0, 10).map((sesion) => (
                <div key={sesion.id} className="sesion-item">
                  <div className="sesion-fecha">{formatFecha(sesion.fecha)}</div>
                  <div className="sesion-hora">
                    {formatHora(sesion.hora_inicio)} - {formatHora(sesion.hora_fin)}
                  </div>
                  <span className={`sesion-estado estado-${sesion.estado}`}>
                    {sesion.estado === 'programada' && <><Calendar size={16} /> Programada</>}
                    {sesion.estado === 'en_curso' && <><Clock size={16} /> En Curso</>}
                    {sesion.estado === 'completada' && <><CheckCircle2 size={16} style={{ color: 'var(--success)' }} /> Completada</>}
                    {sesion.estado === 'cancelada' && <><XCircle size={16} style={{ color: 'var(--danger)' }} /> Cancelada</>}
                  </span>
                  <div className="sesion-reservas">
                    {sesion.reservas_count || 0} / {horario.cupo_maximo} reservas
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal de Confirmación de Eliminación */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleEliminar}
        title="Eliminar Horario"
        message="¿Está seguro de eliminar este horario? Esto eliminará también todas las sesiones asociadas. Esta acción no se puede deshacer."
        confirmText="Eliminar"
        cancelText="Cancelar"
        type="danger"
      />

      {/* Modal de Éxito */}
      <ConfirmModal
        isOpen={showSuccessModal}
        onClose={() => {
          setShowSuccessModal(false);
          navigate('/horarios');
        }}
        onConfirm={() => {
          setShowSuccessModal(false);
          navigate('/horarios');
        }}
        title="Éxito"
        message={successMessage}
        confirmText="Aceptar"
        cancelText=""
        type="success"
      />

      {/* Modal de Error */}
      <ConfirmModal
        isOpen={showErrorModal}
        onClose={() => setShowErrorModal(false)}
        onConfirm={() => setShowErrorModal(false)}
        title="Error"
        message={errorMessage}
        confirmText="Entendido"
        cancelText=""
        type="danger"
      />
    </div>
  );
};

export default HorarioDetail;
