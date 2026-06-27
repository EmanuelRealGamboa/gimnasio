import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Pencil,
  Clock,
  RefreshCw,
  CheckCircle2,
  XCircle,
  ClipboardList,
  ShieldCheck,
  Wrench,
  Package,
  Calendar,
  Siren,
  AlertTriangle,
  Banknote,
  User,
  Building2,
  FileText,
  FileSpreadsheet,
  BarChart3,
} from 'lucide-react';
import { mantenimientoService } from '../services/gestionEquiposService';
import './ActivoDetail.css';

const MantenimientoDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [mantenimiento, setMantenimiento] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarMantenimiento();
  }, [id]);

  const cargarMantenimiento = async () => {
    try {
      setLoading(true);
      const response = await mantenimientoService.getById(id);
      setMantenimiento(response.data);
    } catch (error) {
      console.error('Error al cargar mantenimiento:', error);
      alert('Error al cargar el mantenimiento');
      navigate('/gestion-equipos/mantenimientos');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const getEstadoColor = (estado) => {
    const colors = {
      'pendiente': '#f59e0b',
      'en_proceso': '#3b82f6',
      'completado': '#10b981',
      'cancelado': '#6b7280'
    };
    return colors[estado] || '#6b7280';
  };

  const getEstadoIcon = (estado) => {
    const icons = {
      'pendiente': <Clock size={16} />,
      'en_proceso': <RefreshCw size={16} />,
      'completado': <CheckCircle2 size={16} />,
      'cancelado': <XCircle size={16} />
    };
    return icons[estado] || <ClipboardList size={16} />;
  };

  const getTipoIcon = (tipo) => {
    return tipo === 'preventivo' ? <ShieldCheck size={48} /> : <Wrench size={48} />;
  };

  if (loading) {
    return (
      <div className="activo-detail-container">
        <div className="loading">Cargando mantenimiento...</div>
      </div>
    );
  }

  if (!mantenimiento) {
    return (
      <div className="activo-detail-container">
        <div className="empty-state">
          <p>Mantenimiento no encontrado</p>
          <Link to="/gestion-equipos/mantenimientos" className="btn btn-primary">
            Volver al Listado
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="activo-detail-container">
      {/* Header */}
      <div className="detail-header">
        <Link to="/gestion-equipos/mantenimientos" className="btn-back">
          <ArrowLeft size={16} /> Volver al Listado
        </Link>
        <div className="header-actions">
          {mantenimiento.estado === 'pendiente' && (
            <Link
              to={`/gestion-equipos/mantenimientos/edit/${id}`}
              className="btn btn-edit"
            >
              <Pencil size={16} /> Editar
            </Link>
          )}
        </div>
      </div>

      {/* Hero Section */}
      <div className="detail-hero mantenimiento-hero">
        <div className="hero-icon-large">
          {getTipoIcon(mantenimiento.tipo_mantenimiento)}
        </div>
        <div className="hero-info">
          <div className="hero-badge" style={{ backgroundColor: getEstadoColor(mantenimiento.estado) }}>
            <span>{getEstadoIcon(mantenimiento.estado)}</span>
            <span>{mantenimiento.estado_display}</span>
          </div>
          <h1 className="hero-title">
            {mantenimiento.tipo_display}
          </h1>
          <p className="hero-subtitle">
            {mantenimiento.activo_codigo} - {mantenimiento.activo_nombre}
          </p>
        </div>
      </div>

      {/* Grid de Detalles */}
      <div className="detail-grid">
        {/* Información del Activo */}
        <div className="detail-section">
          <div className="section-header">
            <span className="section-icon"><Package size={20} /></span>
            <h2 className="section-title">Información del Activo</h2>
          </div>
          <div className="section-content">
            <div className="info-row">
              <span className="info-label">Código</span>
              <span className="info-value">{mantenimiento.activo_codigo}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Nombre</span>
              <span className="info-value">{mantenimiento.activo_nombre}</span>
            </div>
            {mantenimiento.activo_categoria && (
              <div className="info-row">
                <span className="info-label">Categoría</span>
                <span className="info-value">{mantenimiento.activo_categoria}</span>
              </div>
            )}
          </div>
        </div>

        {/* Fechas */}
        <div className="detail-section">
          <div className="section-header">
            <span className="section-icon"><Calendar size={20} /></span>
            <h2 className="section-title">Fechas</h2>
          </div>
          <div className="section-content">
            <div className="info-row">
              <span className="info-label">Fecha Programada</span>
              <span className="info-value">
                {new Date(mantenimiento.fecha_programada).toLocaleDateString('es-MX', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                })}
              </span>
            </div>
            {mantenimiento.fecha_ejecucion && (
              <div className="info-row">
                <span className="info-label">Fecha de Ejecución</span>
                <span className="info-value">
                  {new Date(mantenimiento.fecha_ejecucion).toLocaleDateString('es-MX', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric'
                  })}
                </span>
              </div>
            )}
            {mantenimiento.dias_para_mantenimiento !== null && (
              <div className="info-row">
                <span className="info-label">Estado de Tiempo</span>
                <span className="info-value">
                  {mantenimiento.dias_para_mantenimiento < 0 ? (
                    <span style={{ color: '#ef4444' }}>
                      <Siren size={16} /> Vencido hace {Math.abs(mantenimiento.dias_para_mantenimiento)} días
                    </span>
                  ) : mantenimiento.dias_para_mantenimiento === 0 ? (
                    <span style={{ color: '#f59e0b' }}><AlertTriangle size={16} /> Hoy</span>
                  ) : (
                    <span style={{ color: '#3b82f6' }}>
                      <Calendar size={16} /> En {mantenimiento.dias_para_mantenimiento} día{mantenimiento.dias_para_mantenimiento > 1 ? 's' : ''}
                    </span>
                  )}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Costo */}
        <div className="detail-section">
          <div className="section-header">
            <span className="section-icon"><Banknote size={20} /></span>
            <h2 className="section-title">Información Financiera</h2>
          </div>
          <div className="section-content">
            <div className="info-row">
              <span className="info-label">Costo</span>
              <span className="info-value" style={{ color: '#10b981', fontWeight: 700, fontSize: '18px' }}>
                {formatCurrency(mantenimiento.costo)}
              </span>
            </div>
          </div>
        </div>

        {/* Responsable */}
        <div className="detail-section">
          <div className="section-header">
            <span className="section-icon"><User size={20} /></span>
            <h2 className="section-title">Responsable</h2>
          </div>
          <div className="section-content">
            {mantenimiento.responsable ? (
              <>
                <div className="info-row">
                  <span className="info-label">Tipo</span>
                  <span className="info-value">
                    {mantenimiento.responsable.tipo === 'externo' ? <><Building2 size={16} /> Proveedor Externo</> : <><User size={16} /> Empleado Interno</>}
                  </span>
                </div>
                <div className="info-row">
                  <span className="info-label">Nombre</span>
                  <span className="info-value">{mantenimiento.responsable.nombre}</span>
                </div>
              </>
            ) : (
              <div className="info-row">
                <span className="info-value" style={{ color: '#94a3b8' }}>
                  Sin responsable asignado
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Descripción */}
        <div className="detail-section full-width">
          <div className="section-header">
            <span className="section-icon"><FileText size={20} /></span>
            <h2 className="section-title">Descripción del Trabajo</h2>
          </div>
          <div className="section-content">
            <p className="description-text">{mantenimiento.descripcion || 'Sin descripción'}</p>
          </div>
        </div>

        {/* Observaciones */}
        {mantenimiento.observaciones && (
          <div className="detail-section full-width">
            <div className="section-header">
              <span className="section-icon"><FileSpreadsheet size={20} /></span>
              <h2 className="section-title">Observaciones</h2>
            </div>
            <div className="section-content">
              <p className="description-text">{mantenimiento.observaciones}</p>
            </div>
          </div>
        )}

        {/* Auditoría */}
        <div className="detail-section full-width">
          <div className="section-header">
            <span className="section-icon"><BarChart3 size={20} /></span>
            <h2 className="section-title">Información de Auditoría</h2>
          </div>
          <div className="section-content">
            <div className="audit-grid">
              {mantenimiento.creado_por && (
                <div className="info-row">
                  <span className="info-label">Creado por</span>
                  <span className="info-value">{mantenimiento.creado_por}</span>
                </div>
              )}
              <div className="info-row">
                <span className="info-label">Fecha de creación</span>
                <span className="info-value">
                  {new Date(mantenimiento.fecha_creacion).toLocaleString('es-MX')}
                </span>
              </div>
              <div className="info-row">
                <span className="info-label">Última actualización</span>
                <span className="info-value">
                  {new Date(mantenimiento.fecha_actualizacion).toLocaleString('es-MX')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Botón volver */}
      <div style={{ marginTop: '32px', textAlign: 'center' }}>
        <Link to="/gestion-equipos/mantenimientos" className="btn-back-to-dashboard">
          <ArrowLeft size={18} /> Volver al Listado de Mantenimientos
        </Link>
      </div>
    </div>
  );
};

export default MantenimientoDetail;
