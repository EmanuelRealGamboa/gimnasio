import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import membresiaService from '../services/membresiaService';
import clienteService from '../services/clienteService';
import SuscribirMembresiaModal from './SuscribirMembresiaModal';
import ConfirmModal from './ConfirmModal';
import './Ventas.css';

function ClienteMembresiaDetail() {
  const { clienteId } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [suscripciones, setSuscripciones] = useState([]);
  const [suscripcionActiva, setSuscripcionActiva] = useState(null);
  const [suscripcionVencida, setSuscripcionVencida] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showSuscribirModal, setShowSuscribirModal] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');

  useEffect(() => {
    fetchClienteData();
  }, [clienteId]);

  const fetchClienteData = async () => {
    try {
      setLoading(true);
      // Obtener datos del cliente
      const clienteResponse = await clienteService.getCliente(clienteId);
      setCliente(clienteResponse.data);

      // Obtener suscripciones del cliente
      const suscripcionesResponse = await membresiaService.getSuscripcionesByCliente(clienteId);
      const suscripcionesData = suscripcionesResponse.data.results || suscripcionesResponse.data;
      setSuscripciones(suscripcionesData);

      // Identificar suscripción activa
      const activa = suscripcionesData.find(s => s.estado === 'activa');
      setSuscripcionActiva(activa || null);

      // Identificar la última suscripción vencida (si no hay activa)
      if (!activa) {
        const vencida = suscripcionesData.find(s => s.estado === 'vencida');
        setSuscripcionVencida(vencida || null);
      } else {
        setSuscripcionVencida(null);
      }
    } catch (err) {
      console.error('Error al cargar datos del cliente:', err);
      showNotif('Error al cargar los datos del cliente', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSuscribirClick = () => {
    setShowSuscribirModal(true);
  };

  const handleSuscripcionCreada = () => {
    setShowSuscribirModal(false);
    showNotif('✓ Suscripción creada exitosamente', 'success');
    fetchClienteData();
  };

  const handleCancelarClick = () => {
    setConfirmAction({
      type: 'cancelar',
      title: 'Cancelar Suscripción',
      message: `¿Estás seguro de que deseas cancelar la suscripción de ${cliente?.nombre}? Esta acción no se puede deshacer.`,
      action: handleCancelarSuscripcion
    });
    setShowConfirmModal(true);
  };

  const handleCancelarSuscripcion = async () => {
    try {
      await membresiaService.cancelarSuscripcion(suscripcionActiva.id);
      setShowConfirmModal(false);
      showNotif('✓ Suscripción cancelada exitosamente', 'success');
      fetchClienteData();
    } catch (err) {
      console.error('Error al cancelar suscripción:', err);
      showNotif('Error al cancelar la suscripción', 'error');
      setShowConfirmModal(false);
    }
  };

  const handleRenovarClick = () => {
    const suscripcionARenovar = suscripcionActiva || suscripcionVencida;

    if (!suscripcionARenovar) {
      showNotif('Error: No se encontró una suscripción para renovar', 'error');
      return;
    }

    setConfirmAction({
      type: 'renovar',
      title: 'Renovar Suscripción',
      message: `¿Deseas renovar la suscripción de ${cliente?.nombre} con el plan ${suscripcionARenovar.membresia_info?.nombre_plan}?`,
      action: () => handleRenovarSuscripcion(suscripcionARenovar.id)
    });
    setShowConfirmModal(true);
  };

  const handleRenovarSuscripcion = async (suscripcionId) => {
    try {
      if (!suscripcionId) {
        throw new Error('ID de suscripción no válido');
      }
      await membresiaService.renovarSuscripcion(suscripcionId, 'efectivo');
      setShowConfirmModal(false);
      showNotif('✓ Suscripción renovada exitosamente', 'success');
      fetchClienteData();
    } catch (err) {
      console.error('Error al renovar suscripción:', err);
      showNotif('Error al renovar la suscripción', 'error');
      setShowConfirmModal(false);
    }
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  const getEstadoBadgeClass = (estado) => {
    switch (estado) {
      case 'activa':
        return 'badge-success';
      case 'vencida':
        return 'badge-warning';
      case 'cancelada':
        return 'badge-danger';
      default:
        return 'badge-secondary';
    }
  };

  const getDiasRestantesColor = (dias) => {
    if (dias > 30) return '#22c55e'; // Verde - mucho tiempo
    if (dias > 15) return '#22c55e'; // Verde - tiempo suficiente
    if (dias > 7) return '#f59e0b';  // Amarillo - advertencia
    return '#ef4444'; // Rojo - urgente
  };

  if (loading) {
    return (
      <div className="ventas-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando información del cliente...</p>
        </div>
      </div>
    );
  }

  if (!cliente) {
    return (
      <div className="ventas-container">
        <div className="empty-state">
          <div className="empty-icon">❌</div>
          <p>No se encontró el cliente</p>
          <button className="btn-primary" onClick={() => navigate('/ventas/servicios')}>
            Volver
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ventas-container">
      {/* Notification */}
      {showNotification && (
        <div className={`notification ${notificationType} show`}>
          {notificationMessage}
        </div>
      )}

      {/* Header */}
      <div className="ventas-header">
        <button className="btn-back" onClick={() => navigate('/ventas/servicios')}>
          ← Volver
        </button>
        <div>
          <h1>👤 Detalle del Cliente</h1>
          <p className="ventas-subtitle">Información y gestión de membresía</p>
        </div>
      </div>

      {/* Cliente Info Card */}
      <div className="cliente-detail-card">
        <div className="cliente-detail-header">
          <div className="cliente-avatar-large">
            {cliente.nombre?.charAt(0)}{cliente.apellido_paterno?.charAt(0)}
          </div>
          <div className="cliente-detail-info">
            <h2>{cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}</h2>
            <div className="cliente-detail-meta">
              <span>📧 {cliente.email}</span>
              <span>📞 {cliente.telefono}</span>
              <span className={`badge badge-${cliente.estado}`}>{cliente.estado}</span>
            </div>
          </div>
        </div>

        {cliente.objetivo_fitness && (
          <div className="cliente-detail-section">
            <h3>🎯 Objetivo Fitness</h3>
            <p>{cliente.objetivo_fitness}</p>
          </div>
        )}

        <div className="cliente-detail-section">
          <h3>📊 Información Adicional</h3>
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Nivel de Experiencia</span>
              <span className="info-value">{cliente.nivel_experiencia}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Fecha de Registro</span>
              <span className="info-value">{new Date(cliente.fecha_registro).toLocaleDateString('es-MX')}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Suscripción Activa */}
      {suscripcionActiva ? (
        <div className="suscripcion-activa-section">
          <div className="section-header">
            <h2>🎫 Membresía Activa</h2>
            <div className="section-actions">
              <button className="btn-success" onClick={handleSuscribirClick}>
                ➕ Adquirir Otra Membresía
              </button>
              <button className="btn-secondary" onClick={handleRenovarClick}>
                🔄 Renovar
              </button>
              <button className="btn-danger" onClick={handleCancelarClick}>
                ❌ Cancelar
              </button>
            </div>
          </div>

          <div className="membresia-active-card">
            <div className="membresia-active-header">
              <div>
                <h3>{suscripcionActiva.membresia_info?.nombre_plan}</h3>
                <p className="membresia-tipo">{suscripcionActiva.membresia_info?.tipo_display}</p>
              </div>
              <span className={`badge ${getEstadoBadgeClass(suscripcionActiva.estado)}`}>
                {suscripcionActiva.estado_display}
              </span>
            </div>

            <div className="membresia-active-body">
              <div className="membresia-dates">
                <div className="date-box">
                  <span className="date-label">Fecha de Inicio</span>
                  <span className="date-value">{new Date(suscripcionActiva.fecha_inicio).toLocaleDateString('es-MX')}</span>
                </div>
                <div className="date-box">
                  <span className="date-label">Fecha de Vencimiento</span>
                  <span className="date-value">{new Date(suscripcionActiva.fecha_fin).toLocaleDateString('es-MX')}</span>
                </div>
              </div>

              <div className="membresia-progress">
                <div
                  className="dias-restantes-large"
                  style={{
                    backgroundColor: getDiasRestantesColor(suscripcionActiva.dias_restantes),
                    color: 'white'
                  }}
                >
                  <span className="dias-numero-large">{suscripcionActiva.dias_restantes}</span>
                  <span className="dias-label-large">días restantes</span>
                </div>
              </div>

              <div className="membresia-details">
                <div className="detail-item">
                  <span className="detail-label">💰 Precio Pagado</span>
                  <span className="detail-value">${parseFloat(suscripcionActiva.precio_pagado).toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">💳 Método de Pago</span>
                  <span className="detail-value">{suscripcionActiva.metodo_pago_display}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">📅 Fecha de Suscripción</span>
                  <span className="detail-value">{new Date(suscripcionActiva.fecha_suscripcion).toLocaleDateString('es-MX')}</span>
                </div>
                {suscripcionActiva.sede_nombre && (
                  <div className="detail-item">
                    <span className="detail-label">🏢 Sede</span>
                    <span className="detail-value">{suscripcionActiva.sede_nombre}</span>
                  </div>
                )}
              </div>

              {/* Espacios Disponibles */}
              {suscripcionActiva.espacios_disponibles && suscripcionActiva.espacios_disponibles.length > 0 && (
                <div className="espacios-section">
                  <h4>🎯 Espacios Incluidos</h4>
                  {suscripcionActiva.membresia_info?.permite_todas_sedes && (
                    <div className="multi-sede-badge-info">
                      ⭐ Esta membresía da acceso a todas las sedes del gimnasio
                    </div>
                  )}
                  <div className="espacios-grid">
                    {suscripcionActiva.espacios_disponibles.map((espacio) => (
                      <div key={espacio.id} className="espacio-card">
                        <div className="espacio-icon">🏋️</div>
                        <div className="espacio-info">
                          <span className="espacio-nombre">{espacio.nombre}</span>
                          {espacio.sede && (
                            <span className="espacio-sede">📍 {espacio.sede}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {suscripcionActiva.membresia_info?.descripcion && (
                <div className="membresia-description">
                  <h4>Descripción</h4>
                  <p>{suscripcionActiva.membresia_info.descripcion}</p>
                </div>
              )}

              {suscripcionActiva.membresia_info?.beneficios && (
                <div className="membresia-beneficios">
                  <h4>Beneficios</h4>
                  <p>{suscripcionActiva.membresia_info.beneficios}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : suscripcionVencida ? (
        <div className="suscripcion-vencida-section">
          <div className="section-header">
            <h2>⚠️ Membresía Vencida</h2>
          </div>

          <div className="membresia-vencida-card">
            <div className="membresia-vencida-header">
              <div>
                <h3>{suscripcionVencida.membresia_info?.nombre_plan}</h3>
                <p className="membresia-tipo">{suscripcionVencida.membresia_info?.tipo_display}</p>
              </div>
              <span className={`badge ${getEstadoBadgeClass(suscripcionVencida.estado)}`}>
                {suscripcionVencida.estado_display}
              </span>
            </div>

            <div className="membresia-vencida-body">
              <div className="vencida-info">
                <p className="vencida-mensaje">
                  ⏰ Esta membresía venció el <strong>{new Date(suscripcionVencida.fecha_fin).toLocaleDateString('es-MX')}</strong>
                </p>
                <p className="vencida-descripcion">
                  El cliente puede renovar esta membresía o seleccionar un nuevo plan.
                </p>
              </div>

              <div className="membresia-details">
                <div className="detail-item">
                  <span className="detail-label">💰 Precio Original</span>
                  <span className="detail-value">${parseFloat(suscripcionVencida.precio_pagado).toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">📅 Fecha de Vencimiento</span>
                  <span className="detail-value">{new Date(suscripcionVencida.fecha_fin).toLocaleDateString('es-MX')}</span>
                </div>
                {suscripcionVencida.sede_nombre && (
                  <div className="detail-item">
                    <span className="detail-label">🏢 Sede</span>
                    <span className="detail-value">{suscripcionVencida.sede_nombre}</span>
                  </div>
                )}
              </div>

              <div className="vencida-actions">
                <button className="btn-renovar-vencida" onClick={handleRenovarClick}>
                  🔄 Renovar Esta Membresía
                </button>
                <button className="btn-cambiar-plan" onClick={handleSuscribirClick}>
                  🎫 Suscribir a Otro Plan
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="no-suscripcion-section">
          <div className="empty-state">
            <div className="empty-icon">🎫</div>
            <p>Este cliente no tiene una membresía activa</p>
            <button className="btn-primary" onClick={handleSuscribirClick}>
              ➕ Suscribir a Membresía
            </button>
          </div>
        </div>
      )}

      {/* Historial de Suscripciones */}
      {suscripciones.length > 0 && (
        <div className="historial-section">
          <h2>📋 Historial de Suscripciones</h2>
          <div className="historial-table">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Plan</th>
                  <th>Tipo</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Precio</th>
                  <th>Método Pago</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {suscripciones.map((suscripcion) => (
                  <tr key={suscripcion.id}>
                    <td>{suscripcion.membresia_info?.nombre_plan}</td>
                    <td>{suscripcion.membresia_info?.tipo_display}</td>
                    <td>{new Date(suscripcion.fecha_inicio).toLocaleDateString('es-MX')}</td>
                    <td>{new Date(suscripcion.fecha_fin).toLocaleDateString('es-MX')}</td>
                    <td>${parseFloat(suscripcion.precio_pagado).toFixed(2)}</td>
                    <td>{suscripcion.metodo_pago_display}</td>
                    <td>
                      <span className={`badge ${getEstadoBadgeClass(suscripcion.estado)}`}>
                        {suscripcion.estado_display}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Suscribir Modal */}
      <SuscribirMembresiaModal
        isOpen={showSuscribirModal}
        onClose={() => setShowSuscribirModal(false)}
        cliente={cliente}
        onSuccess={handleSuscripcionCreada}
      />

      {/* Confirm Modal */}
      {confirmAction && (
        <ConfirmModal
          isOpen={showConfirmModal}
          onClose={() => setShowConfirmModal(false)}
          onConfirm={confirmAction.action}
          title={confirmAction.title}
          message={confirmAction.message}
          confirmText={confirmAction.type === 'cancelar' ? 'Cancelar Suscripción' : 'Renovar'}
          cancelText="Volver"
          type={confirmAction.type === 'cancelar' ? 'danger' : 'warning'}
        />
      )}
    </div>
  );
}

export default ClienteMembresiaDetail;
