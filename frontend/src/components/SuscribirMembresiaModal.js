import { useState, useEffect } from 'react';
import membresiaService from '../services/membresiaService';
import instalacionesService from '../services/instalacionesService';
import './Ventas.css';

function SuscribirMembresiaModal({ isOpen, onClose, cliente, onSuccess }) {
  const [membresias, setMembresias] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [selectedSede, setSelectedSede] = useState(null);
  const [selectedMembresia, setSelectedMembresia] = useState(null);
  const [formData, setFormData] = useState({
    fecha_inicio: new Date().toISOString().split('T')[0],
    metodo_pago: 'efectivo',
    notas: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isOpen) {
      fetchSedes();
      // Reset form
      setSelectedSede(null);
      setSelectedMembresia(null);
      setMembresias([]);
      setFormData({
        fecha_inicio: new Date().toISOString().split('T')[0],
        metodo_pago: 'efectivo',
        notas: ''
      });
      setErrors({});
    }
  }, [isOpen]);

  useEffect(() => {
    if (selectedSede) {
      fetchMembresiasPorSede(selectedSede);
    } else {
      setMembresias([]);
      setSelectedMembresia(null);
    }
  }, [selectedSede]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchMembresiasPorSede = async (sedeId) => {
    try {
      const response = await membresiaService.getMembresiasActivas(sedeId);
      setMembresias(response.data);
    } catch (err) {
      console.error('Error al cargar membresías:', err);
    }
  };

  const handleMembresiaSelect = (membresia) => {
    setSelectedMembresia(membresia);
    setErrors({});
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!selectedSede) {
      newErrors.sede = 'Debes seleccionar una sede';
    }

    if (!selectedMembresia) {
      newErrors.membresia = 'Debes seleccionar una membresía';
    }

    if (!formData.fecha_inicio) {
      newErrors.fecha_inicio = 'La fecha de inicio es requerida';
    }

    if (!formData.metodo_pago) {
      newErrors.metodo_pago = 'El método de pago es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateFechaFin = () => {
    if (!selectedMembresia || !formData.fecha_inicio) return null;

    const fechaInicio = new Date(formData.fecha_inicio);
    const duracionDias = selectedMembresia.duracion_dias || 30;
    const fechaFin = new Date(fechaInicio);
    fechaFin.setDate(fechaFin.getDate() + duracionDias);

    return fechaFin.toISOString().split('T')[0];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Obtener el ID correcto del cliente
      const clienteId = cliente.persona_id || cliente.id || cliente.cliente_id;

      if (!clienteId) {
        setErrors({ general: 'No se pudo identificar el cliente' });
        setLoading(false);
        return;
      }

      const dataToSend = {
        cliente: clienteId,
        membresia: selectedMembresia.id,
        fecha_inicio: formData.fecha_inicio,
        fecha_fin: calculateFechaFin(),
        precio_pagado: parseFloat(selectedMembresia.precio),
        metodo_pago: formData.metodo_pago,
        notas: formData.notas || '',
        sede_suscripcion: selectedSede  // Agregar la sede seleccionada
      };

      console.log('Datos a enviar:', dataToSend);

      await membresiaService.createSuscripcion(dataToSend);
      onSuccess();
    } catch (err) {
      console.error('Error al crear suscripción:', err);
      console.error('Respuesta del servidor:', err.response?.data);
      if (err.response?.data) {
        // Mostrar errores específicos del backend
        const backendErrors = err.response.data;
        if (typeof backendErrors === 'string') {
          setErrors({ general: backendErrors });
        } else {
          setErrors(backendErrors);
        }
      } else {
        setErrors({ general: 'Error al crear la suscripción' });
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const fechaFin = calculateFechaFin();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>➕ Suscribir a Membresía</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Cliente Info */}
          <div className="cliente-info-box">
            <div className="cliente-avatar-small">
              {cliente?.nombre?.charAt(0)}{cliente?.apellido_paterno?.charAt(0)}
            </div>
            <div>
              <h3>{cliente?.nombre} {cliente?.apellido_paterno} {cliente?.apellido_materno}</h3>
              <p>{cliente?.email}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Selección de Sede */}
            <div className="form-section">
              <h3>Selecciona una Sede</h3>
              {errors.sede && <div className="error-message">{errors.sede}</div>}

              <div className="sedes-selector">
                {sedes.length === 0 ? (
                  <p className="text-muted">Cargando sedes...</p>
                ) : (
                  <div className="sede-buttons">
                    {sedes.map((sede) => (
                      <button
                        key={sede.id}
                        type="button"
                        className={`sede-option-btn ${selectedSede === sede.id ? 'selected' : ''}`}
                        onClick={() => setSelectedSede(sede.id)}
                      >
                        <span className="sede-icon">🏢</span>
                        <span className="sede-name">{sede.nombre}</span>
                        {selectedSede === sede.id && <span className="check-icon">✓</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Selección de Membresía */}
            {selectedSede && (
              <div className="form-section">
                <h3>Selecciona un Plan</h3>
                {errors.membresia && <div className="error-message">{errors.membresia}</div>}

                <div className="membresias-grid">
                  {membresias.length === 0 ? (
                    <p className="text-muted">No hay membresías activas disponibles para esta sede</p>
                  ) : (
                    membresias.map((membresia) => (
                    <div
                      key={membresia.id}
                      className={`membresia-option-card ${selectedMembresia?.id === membresia.id ? 'selected' : ''}`}
                      onClick={() => handleMembresiaSelect(membresia)}
                    >
                      <div className="membresia-option-header">
                        <h4>{membresia.nombre_plan}</h4>
                        <span className="membresia-tipo-badge">{membresia.tipo_display}</span>
                      </div>

                      <div className="membresia-option-price">
                        <span className="price-symbol">$</span>
                        <span className="price-amount">{parseFloat(membresia.precio).toFixed(2)}</span>
                      </div>

                      {membresia.duracion_dias && (
                        <div className="membresia-option-duration">
                          📅 {membresia.duracion_dias} días
                        </div>
                      )}

                      {membresia.descripcion && (
                        <p className="membresia-option-description">{membresia.descripcion}</p>
                      )}

                      {membresia.espacios_count > 0 && (
                        <div className="membresia-espacios-badge">
                          🎯 {membresia.espacios_count} espacio{membresia.espacios_count !== 1 ? 's' : ''} incluido{membresia.espacios_count !== 1 ? 's' : ''}
                        </div>
                      )}

                      {membresia.permite_todas_sedes && (
                        <div className="membresia-multi-sede-badge">
                          ⭐ Acceso a todas las sedes
                        </div>
                      )}

                      {selectedMembresia?.id === membresia.id && (
                        <div className="selected-indicator">✓</div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
            )}

            {/* Detalles de la Suscripción */}
            {selectedMembresia && (
              <div className="form-section">
                <h3>Detalles de la Suscripción</h3>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="fecha_inicio">
                      Fecha de Inicio <span className="required">*</span>
                    </label>
                    <input
                      type="date"
                      id="fecha_inicio"
                      name="fecha_inicio"
                      value={formData.fecha_inicio}
                      onChange={handleInputChange}
                      className={errors.fecha_inicio ? 'error' : ''}
                      required
                    />
                    {errors.fecha_inicio && <span className="error-message">{errors.fecha_inicio}</span>}
                  </div>

                  <div className="form-group">
                    <label>Fecha de Vencimiento</label>
                    <input
                      type="date"
                      value={fechaFin || ''}
                      disabled
                      className="input-disabled"
                    />
                    <small className="text-muted">Se calcula automáticamente</small>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="metodo_pago">
                      Método de Pago <span className="required">*</span>
                    </label>
                    <select
                      id="metodo_pago"
                      name="metodo_pago"
                      value={formData.metodo_pago}
                      onChange={handleInputChange}
                      className={errors.metodo_pago ? 'error' : ''}
                      required
                    >
                      <option value="efectivo">Efectivo</option>
                      <option value="transferencia">Transferencia</option>
                      <option value="tarjeta">Tarjeta</option>
                    </select>
                    {errors.metodo_pago && <span className="error-message">{errors.metodo_pago}</span>}
                  </div>

                  <div className="form-group">
                    <label>Precio a Pagar</label>
                    <div className="price-display">
                      ${parseFloat(selectedMembresia.precio).toFixed(2)}
                    </div>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="notas">Notas (Opcional)</label>
                  <textarea
                    id="notas"
                    name="notas"
                    value={formData.notas}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="Notas adicionales sobre esta suscripción..."
                  />
                </div>
              </div>
            )}

            {errors.general && (
              <div className="error-message-box">
                {errors.general}
              </div>
            )}
          </form>
        </div>

        <div className="modal-footer">
          <button
            type="button"
            className="btn-secondary"
            onClick={onClose}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="button"
            className="btn-primary"
            onClick={handleSubmit}
            disabled={loading || !selectedMembresia}
          >
            {loading ? 'Procesando...' : 'Suscribir Cliente'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default SuscribirMembresiaModal;
