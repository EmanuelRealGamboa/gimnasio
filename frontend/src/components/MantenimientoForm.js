import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Pencil,
  Wrench,
  ClipboardList,
  Package,
  Tag,
  Calendar,
  Banknote,
  FileText,
  User,
  RefreshCw,
  Building2,
  AlertTriangle,
  CheckCircle2,
} from 'lucide-react';
import { mantenimientoService, activoService, proveedorService } from '../services/gestionEquiposService';
import './ActivoForm.css';

const MantenimientoForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState({
    activo: '',
    tipo_mantenimiento: 'preventivo',
    fecha_programada: '',
    costo: '',
    descripcion: '',
    proveedor_servicio: '',
    empleado_responsable: '',
    responsable_tipo: 'ninguno', // ninguno, proveedor, empleado
  });

  const [activos, setActivos] = useState([]);
  const [proveedores, setProveedores] = useState([]);
  const [empleados, setEmpleados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    cargarDatosIniciales();
    if (isEdit) {
      cargarMantenimiento();
    }
  }, [id]);

  const cargarDatosIniciales = async () => {
    try {
      const [activosRes, proveedoresRes] = await Promise.all([
        activoService.getAll(),
        proveedorService.getActivos(),
      ]);
      setActivos(activosRes.data);
      setProveedores(proveedoresRes.data);

      // Cargar empleados desde el endpoint de personal
      try {
        const empleadosRes = await fetch('http://localhost:8000/api/personal/empleados/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        if (empleadosRes.ok) {
          const empleadosData = await empleadosRes.json();
          setEmpleados(empleadosData);
        }
      } catch (error) {
        console.log('No se pudieron cargar empleados:', error);
      }
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      alert('Error al cargar datos del formulario');
    }
  };

  const showSuccessMessage = (message) => {
    const successModal = document.createElement('div');
    successModal.className = 'success-modal-overlay';
    successModal.innerHTML = `
      <div class="success-modal">
        <div class="success-icon"><svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>
        <h2>¡Éxito!</h2>
        <p>${message}</p>
      </div>
    `;
    document.body.appendChild(successModal);
    setTimeout(() => successModal.remove(), 2000);
  };

  const cargarMantenimiento = async () => {
    try {
      setLoading(true);
      const response = await mantenimientoService.getById(id);
      const mant = response.data;

      // Determinar tipo de responsable
      let responsable_tipo = 'ninguno';
      if (mant.proveedor_servicio) {
        responsable_tipo = 'proveedor';
      } else if (mant.empleado_responsable) {
        responsable_tipo = 'empleado';
      }

      setFormData({
        activo: mant.activo || '',
        tipo_mantenimiento: mant.tipo_mantenimiento || 'preventivo',
        fecha_programada: mant.fecha_programada || '',
        costo: mant.costo || '',
        descripcion: mant.descripcion || '',
        proveedor_servicio: mant.proveedor_servicio || '',
        empleado_responsable: mant.empleado_responsable || '',
        responsable_tipo: responsable_tipo,
      });
    } catch (error) {
      console.error('Error al cargar mantenimiento:', error);
      alert('Error al cargar el mantenimiento');
      navigate('/gestion-equipos/mantenimientos');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }

    // Si cambia el tipo de responsable, limpiar los responsables
    if (name === 'responsable_tipo') {
      setFormData(prev => ({
        ...prev,
        proveedor_servicio: '',
        empleado_responsable: '',
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.activo) newErrors.activo = 'El activo es obligatorio';
    if (!formData.tipo_mantenimiento) newErrors.tipo_mantenimiento = 'El tipo es obligatorio';
    if (!formData.fecha_programada) newErrors.fecha_programada = 'La fecha es obligatoria';
    if (!formData.descripcion.trim()) newErrors.descripcion = 'La descripción es obligatoria';
    if (!formData.costo || parseFloat(formData.costo) < 0) {
      newErrors.costo = 'El costo debe ser mayor o igual a 0';
    }

    // Validar responsable
    if (formData.responsable_tipo === 'proveedor' && !formData.proveedor_servicio) {
      newErrors.proveedor_servicio = 'Debes seleccionar un proveedor';
    }
    if (formData.responsable_tipo === 'empleado' && !formData.empleado_responsable) {
      newErrors.empleado_responsable = 'Debes seleccionar un empleado';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      alert('Por favor corrige los errores en el formulario');
      return;
    }

    try {
      setLoading(true);

      const dataToSend = {
        activo: parseInt(formData.activo),
        tipo_mantenimiento: formData.tipo_mantenimiento,
        fecha_programada: formData.fecha_programada,
        costo: parseFloat(formData.costo) || 0,
        descripcion: formData.descripcion.trim(),
      };

      // Agregar responsable según el tipo seleccionado
      if (formData.responsable_tipo === 'proveedor') {
        dataToSend.proveedor_servicio = parseInt(formData.proveedor_servicio);
        dataToSend.empleado_responsable = null;
      } else if (formData.responsable_tipo === 'empleado') {
        dataToSend.empleado_responsable = parseInt(formData.empleado_responsable);
        dataToSend.proveedor_servicio = null;
      } else {
        dataToSend.proveedor_servicio = null;
        dataToSend.empleado_responsable = null;
      }

      if (isEdit) {
        await mantenimientoService.update(id, dataToSend);
        showSuccessMessage('Mantenimiento actualizado exitosamente');
      } else {
        await mantenimientoService.create(dataToSend);
        showSuccessMessage('Mantenimiento creado exitosamente');
      }

      setTimeout(() => {
        navigate('/gestion-equipos/mantenimientos');
      }, 1500);
    } catch (error) {
      console.error('Error al guardar:', error);

      if (error.response?.data) {
        const serverErrors = error.response.data;
        const newErrors = {};
        let errorMessage = '';

        if (typeof serverErrors === 'object') {
          Object.keys(serverErrors).forEach(key => {
            const errorValue = serverErrors[key];
            if (Array.isArray(errorValue)) {
              newErrors[key] = errorValue[0];
              errorMessage += `${key}: ${errorValue[0]}\n`;
            } else if (typeof errorValue === 'string') {
              newErrors[key] = errorValue;
              errorMessage += `${key}: ${errorValue}\n`;
            }
          });
        }

        setErrors(newErrors);
        alert(errorMessage || 'Error al guardar. Revisa los campos marcados.');
      } else {
        alert('Error al guardar el mantenimiento. Verifica tu conexión.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEdit) {
    return (
      <div className="activo-form-container">
        <div className="loading-form">
          <div className="spinner"></div>
          <p>Cargando formulario...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="activo-form-container">
      {/* Header */}
      <div className="form-header">
        <Link to="/gestion-equipos/mantenimientos" className="btn-back-form">
          <ArrowLeft size={18} /> Volver al Listado
        </Link>
        <div className="form-header-info">
          <h1 className="form-title">
            {isEdit ? <><Pencil size={20} /> Editar Mantenimiento</> : <><Wrench size={20} /> Nuevo Mantenimiento</>}
          </h1>
          <p className="form-subtitle">
            {isEdit ? 'Actualiza la información del mantenimiento' : 'Programa un nuevo mantenimiento para un equipo'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="activo-form">
        {/* Sección: Información del Mantenimiento */}
        <div className="form-section-header">
          <span className="section-icon"><ClipboardList size={20} /></span>
          <h2 className="section-title">Información del Mantenimiento</h2>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><Package size={16} /></span>
              Equipo/Activo *
            </label>
            <select
              name="activo"
              value={formData.activo}
              onChange={handleChange}
              className={`field-select ${errors.activo ? 'input-error' : ''}`}
              required
            >
              <option value="">Seleccione un equipo</option>
              {activos.map(activo => (
                <option key={activo.activo_id} value={activo.activo_id}>
                  {activo.codigo} - {activo.nombre}
                </option>
              ))}
            </select>
            {errors.activo && (
              <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.activo}</span>
            )}
            <span className="field-hint">Equipo que recibirá mantenimiento</span>
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><Tag size={16} /></span>
              Tipo de Mantenimiento *
            </label>
            <select
              name="tipo_mantenimiento"
              value={formData.tipo_mantenimiento}
              onChange={handleChange}
              className={`field-select ${errors.tipo_mantenimiento ? 'input-error' : ''}`}
              required
            >
              <option value="preventivo">Preventivo</option>
              <option value="correctivo">Correctivo</option>
            </select>
            {errors.tipo_mantenimiento && (
              <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.tipo_mantenimiento}</span>
            )}
            <span className="field-hint">
              Preventivo: programado | Correctivo: reparación
            </span>
          </div>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><Calendar size={16} /></span>
              Fecha Programada *
            </label>
            <input
              type="date"
              name="fecha_programada"
              value={formData.fecha_programada}
              onChange={handleChange}
              className={`field-input ${errors.fecha_programada ? 'input-error' : ''}`}
              min={new Date().toISOString().split('T')[0]}
              required
            />
            {errors.fecha_programada && (
              <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.fecha_programada}</span>
            )}
            <span className="field-hint">Fecha en que se realizará el mantenimiento</span>
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><Banknote size={16} /></span>
              Costo Estimado (MXN) *
            </label>
            <input
              type="number"
              name="costo"
              value={formData.costo}
              onChange={handleChange}
              className={`field-input ${errors.costo ? 'input-error' : ''}`}
              placeholder="0.00"
              step="0.01"
              min="0"
              required
            />
            {errors.costo && (
              <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.costo}</span>
            )}
            <span className="field-hint">Costo estimado del mantenimiento</span>
          </div>
        </div>

        <div className="form-row single">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><FileText size={16} /></span>
              Descripción del Trabajo *
            </label>
            <textarea
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              className={`field-textarea ${errors.descripcion ? 'input-error' : ''}`}
              placeholder="Describe detalladamente el trabajo a realizar..."
              rows={4}
              required
            />
            {errors.descripcion && (
              <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.descripcion}</span>
            )}
            <span className="field-hint">
              Ej: Lubricación de banda, ajuste de velocidad, limpieza de motor
            </span>
          </div>
        </div>

        {/* Sección: Responsable */}
        <div className="form-section-header">
          <span className="section-icon"><User size={20} /></span>
          <h2 className="section-title">Responsable del Mantenimiento</h2>
        </div>

        <div className="form-row single">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon"><RefreshCw size={16} /></span>
              Tipo de Responsable
            </label>
            <select
              name="responsable_tipo"
              value={formData.responsable_tipo}
              onChange={handleChange}
              className="field-select"
            >
              <option value="ninguno">Sin Asignar (Asignar después)</option>
              <option value="proveedor">Proveedor Externo</option>
              <option value="empleado">Empleado Interno</option>
            </select>
            <span className="field-hint">
              Selecciona quién realizará el mantenimiento
            </span>
          </div>
        </div>

        {formData.responsable_tipo === 'proveedor' && (
          <div className="form-row single">
            <div className="form-field">
              <label className="field-label">
                <span className="label-icon"><Building2 size={16} /></span>
                Proveedor de Servicio *
              </label>
              <select
                name="proveedor_servicio"
                value={formData.proveedor_servicio}
                onChange={handleChange}
                className={`field-select ${errors.proveedor_servicio ? 'input-error' : ''}`}
                required
              >
                <option value="">Seleccione un proveedor</option>
                {proveedores.map(prov => (
                  <option key={prov.proveedor_id} value={prov.proveedor_id}>
                    {prov.nombre_empresa} - {prov.nombre_contacto}
                  </option>
                ))}
              </select>
              {errors.proveedor_servicio && (
                <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.proveedor_servicio}</span>
              )}
              <span className="field-hint">Empresa externa que realizará el servicio</span>
            </div>
          </div>
        )}

        {formData.responsable_tipo === 'empleado' && (
          <div className="form-row single">
            <div className="form-field">
              <label className="field-label">
                <span className="label-icon"><User size={16} /></span>
                Empleado Responsable *
              </label>
              <select
                name="empleado_responsable"
                value={formData.empleado_responsable}
                onChange={handleChange}
                className={`field-select ${errors.empleado_responsable ? 'input-error' : ''}`}
                required
              >
                <option value="">Seleccione un empleado</option>
                {empleados.map(emp => (
                  <option key={emp.empleado_id} value={emp.empleado_id}>
                    {emp.persona?.nombre_completo || `${emp.persona?.nombre} ${emp.persona?.apellido_paterno}`}
                  </option>
                ))}
              </select>
              {errors.empleado_responsable && (
                <span className="field-error"><AlertTriangle size={16} style={{ color: 'var(--warning)' }} /> {errors.empleado_responsable}</span>
              )}
              <span className="field-hint">Empleado del gimnasio que realizará el mantenimiento</span>
            </div>
          </div>
        )}

        {/* Botones de acción */}
        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/gestion-equipos/mantenimientos')}
            className="btn-cancel"
            disabled={loading}
          >
            Cancelar
          </button>
          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? (
              <span className="btn-loading">
                <span className="btn-spinner"></span>
                Guardando...
              </span>
            ) : (
              <>
                {isEdit ? <><CheckCircle2 size={18} /> Actualizar Mantenimiento</> : <><Wrench size={18} /> Crear Mantenimiento</>}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default MantenimientoForm;
