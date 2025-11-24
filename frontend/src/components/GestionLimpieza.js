import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import limpiezaService from '../services/limpiezaService';
import instalacionesService from '../services/instalacionesService';
import './GestionLimpieza.css';

function GestionLimpieza() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('asignaciones');
  const [loading, setLoading] = useState(false);

  // Estado para filtros globales
  const [sedes, setSedes] = useState([]);
  const [sedeFilter, setSedeFilter] = useState('');
  const [fechaFilter, setFechaFilter] = useState(new Date().toISOString().split('T')[0]);

  // Estados para cada tab
  const [asignaciones, setAsignaciones] = useState([]);
  const [personal, setPersonal] = useState([]);
  const [tareas, setTareas] = useState([]);
  const [horarios, setHorarios] = useState([]);
  const [estadisticas, setEstadisticas] = useState(null);

  // Estado para modal de crear asignación
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [espacios, setEspacios] = useState([]);
  const [nuevaAsignacion, setNuevaAsignacion] = useState({
    sede: '',             // PASO 1: Seleccionar sede
    personal_limpieza: '', // PASO 2: Seleccionar empleado de esa sede
    espacio: '',          // PASO 3: Seleccionar espacio de esa sede
    tarea: '',            // PASO 4: Seleccionar tarea según tipo de espacio
    fecha: new Date().toISOString().split('T')[0], // PASO 5: Fecha de asignación
    notas: ''             // PASO 6: Notas opcionales
    // hora_inicio se guardará automáticamente al crear
    // hora_fin se guardará cuando empleado confirme desde app móvil
  });

  // Estado para modal de crear tarea
  const [showCreateTareaModal, setShowCreateTareaModal] = useState(false);
  const [showEditTareaModal, setShowEditTareaModal] = useState(false);
  const [tareaToEdit, setTareaToEdit] = useState(null);
  const [nuevaTarea, setNuevaTarea] = useState({
    nombre: '',
    descripcion: '',
    tipo_espacio: '',
    duracion_estimada: 30,
    prioridad: 'media',
    activo: true
  });

  // Estados para modales de confirmación
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [confirmAction, setConfirmAction] = useState(null);
  const [confirmMessage, setConfirmMessage] = useState('');
  const [showEditAsignacionModal, setShowEditAsignacionModal] = useState(false);
  const [asignacionToEdit, setAsignacionToEdit] = useState(null);

  // Estados para modal de éxito
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchSedes();
    fetchEspacios();
  }, []);

  useEffect(() => {
    if (activeTab === 'asignaciones') {
      fetchAsignaciones();
    } else if (activeTab === 'personal') {
      fetchPersonal();
    } else if (activeTab === 'tareas') {
      fetchTareas();
    } else if (activeTab === 'horarios') {
      fetchHorarios();
    } else if (activeTab === 'reportes') {
      fetchEstadisticas();
    }
  }, [activeTab, sedeFilter, fechaFilter]);

  // Cargar datos necesarios para el modal cuando se abra
  useEffect(() => {
    if (showCreateModal) {
      if (personal.length === 0) fetchPersonal();
      if (tareas.length === 0) fetchTareas();
    }
  }, [showCreateModal]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar sedes:', error);
    }
  };

  const fetchEspacios = async () => {
    try {
      const response = await instalacionesService.getEspacios();
      setEspacios(response.data.results || response.data);
    } catch (error) {
      console.error('Error al cargar espacios:', error);
    }
  };

  const fetchAsignaciones = async () => {
    setLoading(true);
    try {
      const params = {
        fecha: fechaFilter
      };
      if (sedeFilter) params.sede = sedeFilter;

      const data = await limpiezaService.getAsignaciones(params);
      setAsignaciones(data);
    } catch (error) {
      console.error('Error al cargar asignaciones:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchPersonal = async (filters = {}) => {
    setLoading(true);
    try {
      const params = { ...filters };
      // Solo aplicar filtro de sede si se pasa explícitamente o si estamos en el tab de personal
      if (activeTab === 'personal' && sedeFilter) {
        params.sede = sedeFilter;
      }

      const data = await limpiezaService.getPersonal(params);
      setPersonal(data);
    } catch (error) {
      console.error('Error al cargar personal:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTareas = async () => {
    setLoading(true);
    try {
      const data = await limpiezaService.getTareas({ activo: true });
      setTareas(data);
    } catch (error) {
      console.error('Error al cargar tareas:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHorarios = async () => {
    setLoading(true);
    try {
      const params = {};
      if (sedeFilter) params.sede = sedeFilter;

      const data = await limpiezaService.getHorarios(params);
      setHorarios(data);
    } catch (error) {
      console.error('Error al cargar horarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEstadisticas = async () => {
    setLoading(true);
    try {
      const params = {};
      if (sedeFilter) params.sede = sedeFilter;

      const data = await limpiezaService.getEstadisticas(params);
      setEstadisticas(data);
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarcarCompletada = async (asignacionId) => {
    try {
      // Por ahora, usar un ID de ejemplo - esto debería venir del usuario logueado
      await limpiezaService.marcarCompletada(asignacionId, {
        completada_por: 1, // ID del empleado que completa
        observaciones_completado: ''
      });
      fetchAsignaciones(); // Refrescar lista
      handleSuccess('Tarea marcada como completada');
    } catch (error) {
      console.error('Error al marcar tarea como completada:', error);
      alert('Error al marcar tarea como completada');
    }
  };

  const handleMarcarEnProgreso = async (asignacionId) => {
    try {
      await limpiezaService.marcarEnProgreso(asignacionId);
      fetchAsignaciones();
      handleSuccess('Tarea marcada como en progreso');
    } catch (error) {
      console.error('Error al marcar tarea en progreso:', error);
      alert('Error al marcar tarea en progreso');
    }
  };

  const getEstadoIcon = (estado) => {
    const icons = {
      'pendiente': '⏳',
      'en_progreso': '🔄',
      'completada': '✅',
      'cancelada': '❌'
    };
    return icons[estado] || '📋';
  };

  const getPrioridadIcon = (prioridad) => {
    const icons = {
      'alta': '🔴',
      'media': '🟡',
      'baja': '🟢'
    };
    return icons[prioridad] || '⚪';
  };

  const handleCrearAsignacion = async (e) => {
    e.preventDefault();

    // Validar que todos los campos estén llenos
    if (!nuevaAsignacion.sede || !nuevaAsignacion.personal_limpieza || !nuevaAsignacion.espacio || !nuevaAsignacion.tarea) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    // Convertir a números y validar
    const personalLimpiezaId = parseInt(nuevaAsignacion.personal_limpieza);
    const tareaId = parseInt(nuevaAsignacion.tarea);
    const espacioId = parseInt(nuevaAsignacion.espacio);

    if (isNaN(personalLimpiezaId) || isNaN(tareaId) || isNaN(espacioId)) {
      alert('Error: Los datos seleccionados no son válidos. Por favor, intenta de nuevo.');
      console.error('Valores inválidos:', {
        personal_limpieza: nuevaAsignacion.personal_limpieza,
        tarea: nuevaAsignacion.tarea,
        espacio: nuevaAsignacion.espacio
      });
      return;
    }

    try {
      // Enviar solo los campos necesarios (sin sede, sin hora_inicio, sin hora_fin)
      const dataToSend = {
        personal_limpieza: personalLimpiezaId,
        tarea: tareaId,
        espacio: espacioId,
        fecha: nuevaAsignacion.fecha,
        notas: nuevaAsignacion.notas || ''
        // hora_inicio se guardará automáticamente en el backend
        // hora_fin se guardará cuando empleado confirme desde app móvil
      };

      console.log('Datos a enviar:', dataToSend);
      await limpiezaService.crearAsignacion(dataToSend);
      setShowCreateModal(false);
      setNuevaAsignacion({
        sede: '',
        personal_limpieza: '',
        tarea: '',
        espacio: '',
        fecha: new Date().toISOString().split('T')[0],
        notas: ''
      });
      fetchAsignaciones();
      handleSuccess('Asignación creada exitosamente');
    } catch (error) {
      console.error('Error completo al crear asignación:', error);
      console.error('Respuesta del servidor:', error.response?.data);
      const errorMsg = error.response?.data
        ? JSON.stringify(error.response.data, null, 2)
        : error.message;
      alert(`Error al crear la asignación:\n${errorMsg}`);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;

    // Si cambia la sede, resetear empleado y espacio
    if (name === 'sede') {
      setNuevaAsignacion(prev => ({
        ...prev,
        sede: value,
        personal_limpieza: '',
        espacio: '',
        tarea: ''
      }));
    }
    // Si cambia el espacio, resetear tarea
    else if (name === 'espacio') {
      setNuevaAsignacion(prev => ({
        ...prev,
        espacio: value,
        tarea: ''
      }));
    }
    else {
      setNuevaAsignacion(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleCrearTarea = async (e) => {
    e.preventDefault();

    if (!nuevaTarea.nombre || !nuevaTarea.tipo_espacio || !nuevaTarea.duracion_estimada) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      await limpiezaService.crearTarea(nuevaTarea);
      setShowCreateTareaModal(false);
      setNuevaTarea({
        nombre: '',
        descripcion: '',
        tipo_espacio: '',
        duracion_estimada: 30,
        prioridad: 'media',
        activo: true
      });
      fetchTareas();
      handleSuccess('Tarea creada exitosamente');
    } catch (error) {
      console.error('Error al crear tarea:', error);
      alert('Error al crear la tarea');
    }
  };

  const handleTareaInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNuevaTarea(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleEditTarea = (tarea) => {
    setTareaToEdit(tarea);
    setNuevaTarea({
      nombre: tarea.nombre,
      descripcion: tarea.descripcion || '',
      tipo_espacio: tarea.tipo_espacio,
      duracion_estimada: tarea.duracion_estimada,
      prioridad: tarea.prioridad,
      activo: tarea.activo
    });
    setShowEditTareaModal(true);
  };

  const handleActualizarTarea = async (e) => {
    e.preventDefault();

    if (!nuevaTarea.nombre || !nuevaTarea.tipo_espacio || !nuevaTarea.duracion_estimada) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      await limpiezaService.actualizarTarea(tareaToEdit.id, nuevaTarea);
      setShowEditTareaModal(false);
      setTareaToEdit(null);
      setNuevaTarea({
        nombre: '',
        descripcion: '',
        tipo_espacio: '',
        duracion_estimada: 30,
        prioridad: 'media',
        activo: true
      });
      fetchTareas();
      handleSuccess('Tarea actualizada exitosamente');
    } catch (error) {
      console.error('Error al actualizar tarea:', error);
      alert('Error al actualizar la tarea');
    }
  };

  const handleDeleteTarea = (tarea) => {
    setConfirmMessage(`¿Estás seguro de que deseas eliminar la tarea "${tarea.nombre}"?`);
    setConfirmAction(() => async () => {
      try {
        await limpiezaService.eliminarTarea(tarea.id);
        fetchTareas();
        handleSuccess('Tarea eliminada exitosamente');
      } catch (error) {
        console.error('Error al eliminar tarea:', error);
        alert('Error al eliminar la tarea');
      }
    });
    setShowConfirmModal(true);
  };

  const handleEditAsignacion = (asignacion) => {
    setAsignacionToEdit(asignacion);
    setNuevaAsignacion({
      sede: asignacion.espacio?.sede || '',
      personal_limpieza: asignacion.personal_limpieza,
      espacio: asignacion.espacio,
      tarea: asignacion.tarea,
      fecha: asignacion.fecha,
      notas: asignacion.notas || ''
    });
    setShowEditAsignacionModal(true);
  };

  const handleActualizarAsignacion = async (e) => {
    e.preventDefault();

    if (!nuevaAsignacion.personal_limpieza || !nuevaAsignacion.espacio || !nuevaAsignacion.tarea) {
      alert('Por favor completa todos los campos obligatorios');
      return;
    }

    try {
      const dataToSend = {
        personal_limpieza: parseInt(nuevaAsignacion.personal_limpieza),
        tarea: parseInt(nuevaAsignacion.tarea),
        espacio: parseInt(nuevaAsignacion.espacio),
        fecha: nuevaAsignacion.fecha,
        notas: nuevaAsignacion.notas || ''
      };

      await limpiezaService.actualizarAsignacion(asignacionToEdit.id, dataToSend);
      setShowEditAsignacionModal(false);
      setAsignacionToEdit(null);
      setNuevaAsignacion({
        sede: '',
        personal_limpieza: '',
        tarea: '',
        espacio: '',
        fecha: new Date().toISOString().split('T')[0],
        notas: ''
      });
      fetchAsignaciones();
      handleSuccess('Asignación actualizada exitosamente');
    } catch (error) {
      console.error('Error al actualizar asignación:', error);
      alert('Error al actualizar la asignación');
    }
  };

  const handleDeleteAsignacion = (asignacion) => {
    setConfirmMessage(`¿Estás seguro de que deseas eliminar esta asignación de "${asignacion.tarea_nombre}"?`);
    setConfirmAction(() => async () => {
      try {
        await limpiezaService.eliminarAsignacion(asignacion.id);
        fetchAsignaciones();
        handleSuccess('Asignación eliminada exitosamente');
      } catch (error) {
        console.error('Error al eliminar asignación:', error);
        alert('Error al eliminar la asignación');
      }
    });
    setShowConfirmModal(true);
  };

  const handleConfirm = async () => {
    if (confirmAction) {
      await confirmAction();
    }
    setShowConfirmModal(false);
    setConfirmAction(null);
    setConfirmMessage('');
  };

  const handleSuccess = (message) => {
    setSuccessMessage(message);
    setShowSuccessModal(true);
    // Auto-cerrar después de 3 segundos
    setTimeout(() => {
      setShowSuccessModal(false);
      setSuccessMessage('');
    }, 3000);
  };

  return (
    <div className="gestion-limpieza-container">
      {/* Header */}
      <div className="limpieza-header">
        <div>
          <h1>🧹 Gestión de Limpieza</h1>
          <p className="limpieza-subtitle">
            Administra el personal, horarios, tareas y asignaciones de limpieza
          </p>
        </div>
      </div>

      {/* Tabs Navigation */}
      <div className="tabs-navigation">
        <button
          className={`tab-button ${activeTab === 'asignaciones' ? 'active' : ''}`}
          onClick={() => setActiveTab('asignaciones')}
        >
          📋 Asignaciones
        </button>
        <button
          className={`tab-button ${activeTab === 'tareas' ? 'active' : ''}`}
          onClick={() => setActiveTab('tareas')}
        >
          📝 Catálogo de Tareas
        </button>
        <button
          className={`tab-button ${activeTab === 'personal' ? 'active' : ''}`}
          onClick={() => setActiveTab('personal')}
        >
          👥 Personal
        </button>
        <button
          className={`tab-button ${activeTab === 'horarios' ? 'active' : ''}`}
          onClick={() => setActiveTab('horarios')}
        >
          🕐 Horarios
        </button>
        <button
          className={`tab-button ${activeTab === 'reportes' ? 'active' : ''}`}
          onClick={() => setActiveTab('reportes')}
        >
          📊 Reportes
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {/* ========================================
            TAB: ASIGNACIONES
        ======================================== */}
        {activeTab === 'asignaciones' && (
          <div className="asignaciones-tab">
            {/* Filtros */}
            <div className="section-card">
              <div className="filters-row">
                <div className="filter-group">
                  <label>Fecha</label>
                  <input
                    type="date"
                    className="filter-input"
                    value={fechaFilter}
                    onChange={(e) => setFechaFilter(e.target.value)}
                  />
                </div>
                <div className="filter-group">
                  <label>Sede</label>
                  <select
                    className="filter-select"
                    value={sedeFilter}
                    onChange={(e) => setSedeFilter(e.target.value)}
                  >
                    <option value="">Todas las sedes</option>
                    {sedes.map(sede => (
                      <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                    ))}
                  </select>
                </div>
                <div className="filter-group">
                  <label>&nbsp;</label>
                  <button className="btn-secondary" onClick={fetchAsignaciones}>
                    🔄 Actualizar
                  </button>
                </div>
                <div className="filter-group">
                  <label>&nbsp;</label>
                  <button className="btn-primary" onClick={() => setShowCreateModal(true)}>
                    ➕ Nueva Asignación
                  </button>
                </div>
              </div>
            </div>

            {/* Estadísticas rápidas */}
            {asignaciones.length > 0 && (
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
                    📋
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Total Tareas</div>
                    <div className="stat-value">{asignaciones.length}</div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
                    ✅
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Completadas</div>
                    <div className="stat-value">
                      {asignaciones.filter(a => a.estado === 'completada').length}
                    </div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                    ⏳
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">Pendientes</div>
                    <div className="stat-value">
                      {asignaciones.filter(a => a.estado === 'pendiente').length}
                    </div>
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
                    🔄
                  </div>
                  <div className="stat-content">
                    <div className="stat-label">En Progreso</div>
                    <div className="stat-value">
                      {asignaciones.filter(a => a.estado === 'en_progreso').length}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Lista de Asignaciones */}
            <div className="section-card">
              <h2 className="section-title">
                📋 Asignaciones del {new Date(fechaFilter).toLocaleDateString('es-MX')}
              </h2>

              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Cargando asignaciones...</p>
                </div>
              ) : asignaciones.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📋</div>
                  <p>No hay asignaciones para esta fecha</p>
                  <p className="empty-subtitle">Cambia la fecha o crea una nueva asignación</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Estado</th>
                        <th>Tarea</th>
                        <th>Personal</th>
                        <th>Espacio</th>
                        <th>Sede</th>
                        <th>Fecha</th>
                        <th>Prioridad</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {asignaciones.map((asignacion) => (
                        <tr key={asignacion.id}>
                          <td>
                            <span className={`badge badge-${asignacion.estado}`}>
                              {getEstadoIcon(asignacion.estado)} {asignacion.estado_display}
                            </span>
                          </td>
                          <td>
                            <strong>{asignacion.tarea_nombre}</strong>
                            <br />
                            <small style={{ color: '#6b7280' }}>
                              {asignacion.tarea_duracion} min
                            </small>
                          </td>
                          <td>{asignacion.personal_nombre}</td>
                          <td>{asignacion.espacio_nombre}</td>
                          <td>{asignacion.sede_nombre}</td>
                          <td>
                            {new Date(asignacion.fecha).toLocaleDateString('es-MX', {
                              day: '2-digit',
                              month: '2-digit',
                              year: 'numeric'
                            })}
                          </td>
                          <td>
                            <span className={`badge badge-${asignacion.tarea_prioridad}`}>
                              {getPrioridadIcon(asignacion.tarea_prioridad)} {asignacion.tarea_prioridad}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                              {asignacion.estado === 'pendiente' && (
                                <>
                                  <button
                                    className="btn-secondary btn-small"
                                    onClick={() => handleMarcarEnProgreso(asignacion.id)}
                                    title="Iniciar tarea"
                                  >
                                    ▶️ Iniciar
                                  </button>
                                  <button
                                    className="btn-warning btn-small"
                                    onClick={() => handleEditAsignacion(asignacion)}
                                    title="Editar asignación"
                                  >
                                    ✏️
                                  </button>
                                  <button
                                    className="btn-danger btn-small"
                                    onClick={() => handleDeleteAsignacion(asignacion)}
                                    title="Eliminar asignación"
                                  >
                                    🗑️
                                  </button>
                                </>
                              )}
                              {asignacion.estado === 'en_progreso' && (
                                <button
                                  className="btn-primary btn-small"
                                  onClick={() => handleMarcarCompletada(asignacion.id)}
                                >
                                  ✅ Completar
                                </button>
                              )}
                              {asignacion.estado === 'completada' && (
                                <span style={{ color: '#16a34a', fontWeight: 600 }}>
                                  ✅ Completada
                                </span>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================
            TAB: CATÁLOGO DE TAREAS
        ======================================== */}
        {activeTab === 'tareas' && (
          <div className="tareas-tab">
            <div className="section-card">
              <h2 className="section-title">📝 Catálogo de Tareas de Limpieza</h2>

              {/* Botón para crear nueva tarea */}
              <div style={{ marginBottom: '2rem' }}>
                <button className="btn-primary" onClick={() => setShowCreateTareaModal(true)}>
                  ➕ Nueva Tarea
                </button>
              </div>

              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Cargando tareas...</p>
                </div>
              ) : tareas.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">📝</div>
                  <p>No hay tareas de limpieza en el catálogo</p>
                  <p className="empty-subtitle">Crea tareas para asignarlas al personal de limpieza</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Tipo de Espacio</th>
                        <th>Duración</th>
                        <th>Prioridad</th>
                        <th>Estado</th>
                        <th>Descripción</th>
                        <th>Acciones</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tareas.map((tarea) => (
                        <tr key={tarea.id}>
                          <td>
                            <strong>{tarea.nombre}</strong>
                          </td>
                          <td>
                            <span className="badge" style={{
                              background: '#f0f9ff',
                              color: '#0369a1'
                            }}>
                              {tarea.tipo_espacio_display}
                            </span>
                          </td>
                          <td>
                            <span style={{ color: '#6b7280' }}>
                              ⏱️ {tarea.duracion_estimada} min
                            </span>
                          </td>
                          <td>
                            <span className={`badge badge-${tarea.prioridad}`}>
                              {getPrioridadIcon(tarea.prioridad)} {tarea.prioridad_display}
                            </span>
                          </td>
                          <td>
                            <span className={`badge badge-${tarea.activo ? 'activo' : 'inactivo'}`}>
                              {tarea.activo ? '✅ Activo' : '❌ Inactivo'}
                            </span>
                          </td>
                          <td>
                            <small style={{ color: '#6b7280' }}>
                              {tarea.descripcion || 'Sin descripción'}
                            </small>
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              <button
                                className="btn-warning btn-small"
                                onClick={() => handleEditTarea(tarea)}
                                title="Editar tarea"
                              >
                                ✏️ Editar
                              </button>
                              <button
                                className="btn-danger btn-small"
                                onClick={() => handleDeleteTarea(tarea)}
                                title="Eliminar tarea"
                              >
                                🗑️
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================
            TAB: PERSONAL
        ======================================== */}
        {activeTab === 'personal' && (
          <div className="personal-tab">
            <div className="section-card">
              <h2 className="section-title">👥 Personal de Limpieza</h2>

              {/* Filtros */}
              <div className="filters-row">
                <div className="filter-group">
                  <label>Sede</label>
                  <select
                    value={sedeFilter}
                    onChange={(e) => setSedeFilter(e.target.value)}
                    className="filter-select"
                  >
                    <option value="">Todas las sedes</option>
                    {sedes.map(sede => (
                      <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                    ))}
                  </select>
                </div>
                <div className="filter-group">
                  <label>&nbsp;</label>
                  <button className="btn-secondary" onClick={fetchPersonal}>
                    🔄 Actualizar
                  </button>
                </div>
              </div>

              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Cargando personal...</p>
                </div>
              ) : personal.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-icon">👥</div>
                  <p>No hay personal de limpieza registrado</p>
                  <p className="empty-subtitle">Agrega empleados de limpieza desde el módulo de Personal</p>
                </div>
              ) : (
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Nombre</th>
                        <th>Sede</th>
                        <th>Turno</th>
                        <th>Email</th>
                        <th>Teléfono</th>
                        <th>Espacios Asignados</th>
                        <th>Tareas Pendientes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {personal.map((p) => (
                        <tr key={p.empleado_id}>
                          <td>
                            <strong>{p.empleado_nombre}</strong>
                          </td>
                          <td>{p.sede_nombre}</td>
                          <td>
                            <span className="badge" style={{
                              background: p.turno?.toLowerCase().includes('matutino') ? '#dbeafe' :
                                         p.turno?.toLowerCase().includes('vespertino') ? '#fef3c7' : '#f3f4f6',
                              color: p.turno?.toLowerCase().includes('matutino') ? '#1e40af' :
                                     p.turno?.toLowerCase().includes('vespertino') ? '#92400e' : '#4b5563'
                            }}>
                              {p.turno}
                            </span>
                          </td>
                          <td>{p.email || 'N/A'}</td>
                          <td>{p.telefono || 'N/A'}</td>
                          <td>
                            {p.espacios_asignados && p.espacios_asignados.length > 0 ? (
                              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                {p.espacios_asignados.map((espacio, idx) => (
                                  <span
                                    key={idx}
                                    className="badge"
                                    style={{
                                      background: '#f0f9ff',
                                      color: '#0369a1',
                                      fontSize: '0.75rem'
                                    }}
                                  >
                                    {espacio.nombre}
                                  </span>
                                ))}
                              </div>
                            ) : (
                              <span style={{ color: '#9ca3af' }}>Sin espacios</span>
                            )}
                          </td>
                          <td>
                            <span className="badge" style={{
                              background: p.tareas_pendientes_count > 0 ? '#fef3c7' : '#f3f4f6',
                              color: p.tareas_pendientes_count > 0 ? '#92400e' : '#6b7280'
                            }}>
                              {p.tareas_pendientes_count} {p.tareas_pendientes_count === 1 ? 'tarea' : 'tareas'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================
            TAB: HORARIOS
        ======================================== */}
        {activeTab === 'horarios' && (
          <div className="horarios-tab">
            <div className="section-card">
              <h2 className="section-title">🕐 Horarios de Limpieza</h2>
              <p style={{ color: '#6b7280', marginBottom: '2rem' }}>
                Este tab mostrará los horarios recurrentes (próximamente)
              </p>
              <div className="empty-state">
                <div className="empty-icon">🕐</div>
                <p>Horarios de limpieza</p>
                <p className="empty-subtitle">En desarrollo...</p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================
            TAB: REPORTES
        ======================================== */}
        {activeTab === 'reportes' && (
          <div className="reportes-tab">
            <div className="section-card">
              <h2 className="section-title">📊 Reportes y Estadísticas</h2>
              {loading ? (
                <div className="loading-spinner">
                  <div className="spinner"></div>
                  <p>Cargando estadísticas...</p>
                </div>
              ) : estadisticas ? (
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
                      ✅
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Tareas Completadas</div>
                      <div className="stat-value">{estadisticas.tareas_completadas}</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                      ⏳
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Tareas Pendientes</div>
                      <div className="stat-value">{estadisticas.tareas_pendientes}</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
                      📈
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Tasa de Cumplimiento</div>
                      <div className="stat-value">{estadisticas.tasa_cumplimiento}%</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
                      ⭐
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Calificación Promedio</div>
                      <div className="stat-value">{estadisticas.calificacion_promedio}/5</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
                      👥
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Total Personal</div>
                      <div className="stat-value">{estadisticas.total_personal}</div>
                    </div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
                      🏢
                    </div>
                    <div className="stat-content">
                      <div className="stat-label">Espacios Limpios Hoy</div>
                      <div className="stat-value">{estadisticas.espacios_limpios_hoy}</div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">📊</div>
                  <p>No hay estadísticas disponibles</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ========================================
          MODAL: CREAR NUEVA ASIGNACIÓN
      ======================================== */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>➕ Nueva Asignación de Tarea</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleCrearAsignacion}>
              <div className="modal-body">
                {/* PASO 1: Seleccionar Sede */}
                <div className="form-row">
                  <div className="form-group">
                    <label>1️⃣ Sede *</label>
                    <select
                      name="sede"
                      value={nuevaAsignacion.sede}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar sede...</option>
                      {sedes.map(sede => (
                        <option key={sede.id} value={sede.id}>
                          {sede.nombre}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* PASO 2: Seleccionar Empleado de Limpieza (filtrado por sede) */}
                  <div className="form-group">
                    <label>2️⃣ Personal de Limpieza *</label>
                    <select
                      name="personal_limpieza"
                      value={nuevaAsignacion.personal_limpieza}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                      disabled={!nuevaAsignacion.sede}
                    >
                      <option value="">
                        {!nuevaAsignacion.sede ? 'Primero selecciona una sede...' : 'Seleccionar empleado...'}
                      </option>
                      {personal
                        .filter(p => !nuevaAsignacion.sede || p.sede_id === parseInt(nuevaAsignacion.sede))
                        .map(p => (
                          <option key={p.empleado_id} value={p.empleado_id}>
                            {p.empleado_nombre}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* PASO 3: Seleccionar Espacio (filtrado por sede) */}
                <div className="form-row">
                  <div className="form-group">
                    <label>3️⃣ Espacio a Limpiar *</label>
                    <select
                      name="espacio"
                      value={nuevaAsignacion.espacio}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                      disabled={!nuevaAsignacion.sede}
                    >
                      <option value="">
                        {!nuevaAsignacion.sede ? 'Primero selecciona una sede...' : 'Seleccionar espacio...'}
                      </option>
                      {espacios
                        .filter(espacio => !nuevaAsignacion.sede || espacio.sede === parseInt(nuevaAsignacion.sede))
                        .map(espacio => (
                          <option key={espacio.id} value={espacio.id}>
                            {espacio.nombre}
                          </option>
                        ))}
                    </select>
                  </div>

                  {/* PASO 4: Seleccionar Tarea */}
                  <div className="form-group">
                    <label>4️⃣ Tarea a Realizar *</label>
                    <select
                      name="tarea"
                      value={nuevaAsignacion.tarea}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar tarea...</option>
                      {tareas.filter(t => t.activo).map(tarea => (
                        <option key={tarea.id} value={tarea.id}>
                          {tarea.nombre} ({tarea.duracion_estimada} min) - {tarea.tipo_espacio_display}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* PASO 5: Fecha de Asignación */}
                <div className="form-row">
                  <div className="form-group">
                    <label>5️⃣ Fecha de Asignación *</label>
                    <input
                      type="date"
                      name="fecha"
                      value={nuevaAsignacion.fecha}
                      onChange={handleInputChange}
                      required
                      className="filter-input"
                    />
                    <small style={{ color: '#6b7280', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                      ⏰ La hora de inicio se guardará automáticamente al crear la asignación
                    </small>
                  </div>

                  <div className="form-group" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                    <div style={{
                      background: '#f0fdf4',
                      border: '1px solid #86efac',
                      padding: '0.75rem',
                      borderRadius: '8px',
                      fontSize: '0.85rem'
                    }}>
                      <strong style={{ color: '#16a34a' }}>ℹ️ Confirmación desde App Móvil</strong>
                      <p style={{ margin: '0.25rem 0 0 0', color: '#15803d' }}>
                        El empleado confirmará la finalización desde la app móvil
                      </p>
                    </div>
                  </div>
                </div>

                {/* PASO 6: Notas Opcionales */}
                <div className="form-group">
                  <label>6️⃣ Notas/Instrucciones (Opcional)</label>
                  <textarea
                    name="notas"
                    value={nuevaAsignacion.notas}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="Instrucciones especiales para el personal de limpieza..."
                    className="filter-input"
                    style={{ resize: 'vertical' }}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  ✅ Crear Asignación
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================
          MODAL: CREAR NUEVA TAREA
      ======================================== */}
      {showCreateTareaModal && (
        <div className="modal-overlay" onClick={() => setShowCreateTareaModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>➕ Nueva Tarea de Limpieza</h2>
              <button className="modal-close" onClick={() => setShowCreateTareaModal(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleCrearTarea}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label>Nombre de la Tarea *</label>
                    <input
                      type="text"
                      name="nombre"
                      value={nuevaTarea.nombre}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-input"
                      placeholder="Ej: Limpieza profunda de baños"
                    />
                  </div>

                  <div className="form-group">
                    <label>Tipo de Espacio *</label>
                    <select
                      name="tipo_espacio"
                      value={nuevaTarea.tipo_espacio}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar tipo...</option>
                      <option value="bano">Baño</option>
                      <option value="vestidor">Vestidor</option>
                      <option value="gimnasio">Gimnasio</option>
                      <option value="alberca">Alberca</option>
                      <option value="recepcion">Recepción</option>
                      <option value="oficina">Oficina</option>
                      <option value="estacionamiento">Estacionamiento</option>
                      <option value="areas_comunes">Áreas Comunes</option>
                      <option value="otro">Otro</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Duración Estimada (minutos) *</label>
                    <input
                      type="number"
                      name="duracion_estimada"
                      value={nuevaTarea.duracion_estimada}
                      onChange={handleTareaInputChange}
                      required
                      min="5"
                      max="480"
                      className="filter-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Prioridad *</label>
                    <select
                      name="prioridad"
                      value={nuevaTarea.prioridad}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="baja">🟢 Baja</option>
                      <option value="media">🟡 Media</option>
                      <option value="alta">🔴 Alta</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Descripción (Opcional)</label>
                  <textarea
                    name="descripcion"
                    value={nuevaTarea.descripcion}
                    onChange={handleTareaInputChange}
                    rows="4"
                    placeholder="Describe en detalle esta tarea de limpieza..."
                    className="filter-input"
                    style={{ resize: 'vertical' }}
                  />
                </div>

                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      name="activo"
                      checked={nuevaTarea.activo}
                      onChange={handleTareaInputChange}
                      style={{ width: '20px', height: '20px' }}
                    />
                    <span>Tarea activa (disponible para asignar)</span>
                  </label>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowCreateTareaModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  ✅ Crear Tarea
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================
          MODAL: EDITAR TAREA
      ======================================== */}
      {showEditTareaModal && tareaToEdit && (
        <div className="modal-overlay" onClick={() => setShowEditTareaModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>✏️ Editar Tarea de Limpieza</h2>
              <button className="modal-close" onClick={() => setShowEditTareaModal(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleActualizarTarea}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group">
                    <label>Nombre de la Tarea *</label>
                    <input
                      type="text"
                      name="nombre"
                      value={nuevaTarea.nombre}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-input"
                      placeholder="Ej: Limpieza profunda de baños"
                    />
                  </div>

                  <div className="form-group">
                    <label>Tipo de Espacio *</label>
                    <select
                      name="tipo_espacio"
                      value={nuevaTarea.tipo_espacio}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar tipo...</option>
                      <option value="bano">Baño</option>
                      <option value="vestidor">Vestidor</option>
                      <option value="gimnasio">Gimnasio</option>
                      <option value="alberca">Alberca</option>
                      <option value="recepcion">Recepción</option>
                      <option value="oficina">Oficina</option>
                      <option value="estacionamiento">Estacionamiento</option>
                      <option value="areas_comunes">Áreas Comunes</option>
                      <option value="otro">Otro</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Duración Estimada (minutos) *</label>
                    <input
                      type="number"
                      name="duracion_estimada"
                      value={nuevaTarea.duracion_estimada}
                      onChange={handleTareaInputChange}
                      required
                      min="5"
                      max="480"
                      className="filter-input"
                    />
                  </div>

                  <div className="form-group">
                    <label>Prioridad *</label>
                    <select
                      name="prioridad"
                      value={nuevaTarea.prioridad}
                      onChange={handleTareaInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="baja">🟢 Baja</option>
                      <option value="media">🟡 Media</option>
                      <option value="alta">🔴 Alta</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Descripción (Opcional)</label>
                  <textarea
                    name="descripcion"
                    value={nuevaTarea.descripcion}
                    onChange={handleTareaInputChange}
                    rows="4"
                    placeholder="Describe en detalle esta tarea de limpieza..."
                    className="filter-input"
                    style={{ resize: 'vertical' }}
                  />
                </div>

                <div className="form-group">
                  <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                    <input
                      type="checkbox"
                      name="activo"
                      checked={nuevaTarea.activo}
                      onChange={handleTareaInputChange}
                      style={{ width: '20px', height: '20px' }}
                    />
                    <span>Tarea activa (disponible para asignar)</span>
                  </label>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowEditTareaModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  ✅ Actualizar Tarea
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================
          MODAL: EDITAR ASIGNACIÓN
      ======================================== */}
      {showEditAsignacionModal && asignacionToEdit && (
        <div className="modal-overlay" onClick={() => setShowEditAsignacionModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>✏️ Editar Asignación de Tarea</h2>
              <button className="modal-close" onClick={() => setShowEditAsignacionModal(false)}>
                ✕
              </button>
            </div>

            <form onSubmit={handleActualizarAsignacion}>
              <div className="modal-body">
                {/* PASO 1: Seleccionar Sede */}
                <div className="form-row">
                  <div className="form-group">
                    <label>1️⃣ Sede *</label>
                    <select
                      name="sede"
                      value={nuevaAsignacion.sede}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar sede...</option>
                      {sedes.map(sede => (
                        <option key={sede.id} value={sede.id}>
                          {sede.nombre}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* PASO 2: Seleccionar Empleado de Limpieza (filtrado por sede) */}
                  <div className="form-group">
                    <label>2️⃣ Personal de Limpieza *</label>
                    <select
                      name="personal_limpieza"
                      value={nuevaAsignacion.personal_limpieza}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                      disabled={!nuevaAsignacion.sede}
                    >
                      <option value="">
                        {!nuevaAsignacion.sede ? 'Primero selecciona una sede...' : 'Seleccionar empleado...'}
                      </option>
                      {personal
                        .filter(p => !nuevaAsignacion.sede || p.sede_id === parseInt(nuevaAsignacion.sede))
                        .map(p => (
                          <option key={p.empleado_id} value={p.empleado_id}>
                            {p.empleado_nombre}
                          </option>
                        ))}
                    </select>
                  </div>
                </div>

                {/* PASO 3: Seleccionar Espacio (filtrado por sede) */}
                <div className="form-row">
                  <div className="form-group">
                    <label>3️⃣ Espacio a Limpiar *</label>
                    <select
                      name="espacio"
                      value={nuevaAsignacion.espacio}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                      disabled={!nuevaAsignacion.sede}
                    >
                      <option value="">
                        {!nuevaAsignacion.sede ? 'Primero selecciona una sede...' : 'Seleccionar espacio...'}
                      </option>
                      {espacios
                        .filter(espacio => !nuevaAsignacion.sede || espacio.sede === parseInt(nuevaAsignacion.sede))
                        .map(espacio => (
                          <option key={espacio.id} value={espacio.id}>
                            {espacio.nombre}
                          </option>
                        ))}
                    </select>
                  </div>

                  {/* PASO 4: Seleccionar Tarea */}
                  <div className="form-group">
                    <label>4️⃣ Tarea a Realizar *</label>
                    <select
                      name="tarea"
                      value={nuevaAsignacion.tarea}
                      onChange={handleInputChange}
                      required
                      className="filter-select"
                    >
                      <option value="">Seleccionar tarea...</option>
                      {tareas.filter(t => t.activo).map(tarea => (
                        <option key={tarea.id} value={tarea.id}>
                          {tarea.nombre} ({tarea.duracion_estimada} min) - {tarea.tipo_espacio_display}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* PASO 5: Fecha de Asignación */}
                <div className="form-row">
                  <div className="form-group">
                    <label>5️⃣ Fecha de Asignación *</label>
                    <input
                      type="date"
                      name="fecha"
                      value={nuevaAsignacion.fecha}
                      onChange={handleInputChange}
                      required
                      className="filter-input"
                    />
                  </div>
                </div>

                {/* PASO 6: Notas Opcionales */}
                <div className="form-group">
                  <label>6️⃣ Notas/Instrucciones (Opcional)</label>
                  <textarea
                    name="notas"
                    value={nuevaAsignacion.notas}
                    onChange={handleInputChange}
                    rows="3"
                    placeholder="Instrucciones especiales para el personal de limpieza..."
                    className="filter-input"
                    style={{ resize: 'vertical' }}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setShowEditAsignacionModal(false)}
                >
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  ✅ Actualizar Asignación
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================
          MODAL: CONFIRMACIÓN
      ======================================== */}
      {showConfirmModal && (
        <div className="modal-overlay" onClick={() => setShowConfirmModal(false)}>
          <div className="modal-content confirm-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚠️ Confirmar Acción</h2>
              <button className="modal-close" onClick={() => setShowConfirmModal(false)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <p style={{ fontSize: '1.1rem', textAlign: 'center', margin: '1rem 0' }}>
                {confirmMessage}
              </p>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => setShowConfirmModal(false)}
              >
                Cancelar
              </button>
              <button
                type="button"
                className="btn-danger"
                onClick={handleConfirm}
              >
                ✅ Confirmar
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de éxito */}
      {showSuccessModal && (
        <div className="modal-overlay" onClick={() => setShowSuccessModal(false)}>
          <div className="modal-content success-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header success-header">
              <h2>✅ Éxito</h2>
              <button className="modal-close" onClick={() => setShowSuccessModal(false)}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              <div className="success-icon">✓</div>
              <p className="success-message">
                {successMessage}
              </p>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn-primary"
                onClick={() => setShowSuccessModal(false)}
              >
                Aceptar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default GestionLimpieza;
