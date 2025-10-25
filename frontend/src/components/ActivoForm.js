import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { activoService, categoriaActivoService } from '../services/gestionEquiposService';
import sedeService from '../services/sedeService';
import espacioService from '../services/espacioService';
import './ActivoForm.css';

const ActivoForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState({
    codigo: '',
    nombre: '',
    categoria: '',
    fecha_compra: '',
    valor: '',
    estado: 'activo',
    ubicacion: '',
    sede: '',
    espacio: '',
    descripcion: '',
    marca: '',
    modelo: '',
    numero_serie: '',
    imagen: null,
  });

  const [categorias, setCategorias] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [espaciosFiltrados, setEspaciosFiltrados] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [codigoExistente, setCodigoExistente] = useState(false);

  useEffect(() => {
    cargarDatosIniciales();
    if (isEdit) {
      cargarActivo();
    }
  }, [id]);

  useEffect(() => {
    if (formData.sede) {
      const espaciosDeSede = espacios.filter(esp => esp.sede === parseInt(formData.sede));
      setEspaciosFiltrados(espaciosDeSede);
    } else {
      setEspaciosFiltrados([]);
    }
  }, [formData.sede, espacios]);

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

  const cargarDatosIniciales = async () => {
    try {
      const [categoriasRes, sedesRes, espaciosRes] = await Promise.all([
        categoriaActivoService.getActivas(),
        sedeService.getSedes(),
        espacioService.getEspacios(),
      ]);
      setCategorias(categoriasRes.data);
      setSedes(sedesRes.data);
      setEspacios(espaciosRes.data);
    } catch (error) {
      console.error('Error al cargar datos iniciales:', error);
      alert('Error al cargar datos del formulario');
    }
  };

  const cargarActivo = async () => {
    try {
      setLoading(true);
      const response = await activoService.getById(id);
      const activo = response.data;

      setFormData({
        codigo: activo.codigo || '',
        nombre: activo.nombre || '',
        categoria: activo.categoria?.categoria_activo_id || '',
        fecha_compra: activo.fecha_compra || '',
        valor: activo.valor || '',
        estado: activo.estado || 'activo',
        ubicacion: activo.ubicacion || '',
        sede: activo.sede_nombre ? sedes.find(s => s.nombre === activo.sede_nombre)?.id || '' : '',
        espacio: activo.espacio_nombre ? espacios.find(e => e.nombre === activo.espacio_nombre)?.id || '' : '',
        descripcion: activo.descripcion || '',
        marca: activo.marca || '',
        modelo: activo.modelo || '',
        numero_serie: activo.numero_serie || '',
        imagen: null, // La imagen existente se mostrará pero no se cargará en el form
      });
    } catch (error) {
      console.error('Error al cargar activo:', error);
      alert('Error al cargar el activo');
      navigate('/gestion-equipos/activos');
    } finally {
      setLoading(false);
    }
  };

  const verificarCodigo = async (codigo) => {
    if (!codigo || codigo.length < 3) {
      setCodigoExistente(false);
      return;
    }

    try {
      const response = await activoService.getAll({ search: codigo.toUpperCase() });
      const existe = response.data.some(
        activo => activo.codigo === codigo.toUpperCase() && activo.activo_id !== parseInt(id)
      );
      setCodigoExistente(existe);
    } catch (error) {
      console.error('Error al verificar código:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, files } = e.target;

    if (type === 'file') {
      setFormData(prev => ({ ...prev, [name]: files[0] }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));

      // Verificar código en tiempo real
      if (name === 'codigo') {
        verificarCodigo(value);
      }
    }

    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.codigo.trim()) {
      newErrors.codigo = 'El código es obligatorio';
    } else if (codigoExistente) {
      newErrors.codigo = 'Este código ya existe, usa uno diferente';
    }

    if (!formData.nombre.trim()) newErrors.nombre = 'El nombre es obligatorio';
    if (!formData.categoria) newErrors.categoria = 'La categoría es obligatoria';
    if (!formData.fecha_compra) newErrors.fecha_compra = 'La fecha de compra es obligatoria';
    if (!formData.valor || parseFloat(formData.valor) <= 0) {
      newErrors.valor = 'El valor debe ser mayor a 0';
    }
    if (!formData.sede) newErrors.sede = 'La sede es obligatoria';

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
        codigo: formData.codigo.toUpperCase().trim(),
        nombre: formData.nombre.trim(),
        categoria: parseInt(formData.categoria),
        fecha_compra: formData.fecha_compra,
        valor: parseFloat(formData.valor),
        estado: formData.estado,
        ubicacion: formData.ubicacion.trim(),
        sede: parseInt(formData.sede),
        espacio: formData.espacio ? parseInt(formData.espacio) : null,
        descripcion: formData.descripcion.trim(),
        marca: formData.marca.trim(),
        modelo: formData.modelo.trim(),
        numero_serie: formData.numero_serie.trim(),
      };

      // Si hay imagen, agregarla
      if (formData.imagen) {
        dataToSend.imagen = formData.imagen;
      }

      if (isEdit) {
        await activoService.update(id, dataToSend);
        showSuccessMessage('Activo actualizado exitosamente');
      } else {
        await activoService.create(dataToSend);
        showSuccessMessage('Activo creado exitosamente');
      }

      setTimeout(() => {
        navigate('/gestion-equipos/activos');
      }, 1500);
    } catch (error) {
      console.error('Error al guardar:', error);

      if (error.response?.data) {
        const serverErrors = error.response.data;

        // Procesar errores del servidor
        const newErrors = {};
        let errorMessage = '';

        // Manejar diferentes formatos de error
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

          // Casos específicos
          if (serverErrors.codigo) {
            errorMessage = 'El código ya existe. Por favor usa uno diferente.';
          }
        } else if (typeof serverErrors === 'string') {
          errorMessage = serverErrors;
        }

        setErrors(newErrors);
        alert(errorMessage || 'Error al guardar. Revisa los campos marcados.');
      } else {
        alert('Error al guardar el activo. Verifica tu conexión.');
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
      {/* Header mejorado */}
      <div className="form-header">
        <Link to="/gestion-equipos/activos" className="btn-back-form">
          ← Volver al Listado
        </Link>
        <div className="form-header-info">
          <h1 className="form-title">
            {isEdit ? '✏️ Editar Activo' : '✨ Nuevo Activo'}
          </h1>
          <p className="form-subtitle">
            {isEdit ? 'Actualiza la información del activo' : 'Registra un nuevo equipo en el inventario'}
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="activo-form">
        {/* Sección: Información General */}
        <div className="form-section-header">
          <span className="section-icon">📋</span>
          <h2 className="section-title">Información General</h2>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🏷️</span>
              Código del Activo *
            </label>
            <input
              type="text"
              name="codigo"
              value={formData.codigo}
              onChange={handleChange}
              className={`field-input ${errors.codigo || codigoExistente ? 'input-error' : ''} ${!errors.codigo && formData.codigo && !codigoExistente ? 'input-success' : ''}`}
              placeholder="CARDIO-001"
              maxLength={50}
              required
            />
            {codigoExistente && !errors.codigo && (
              <span className="field-error">⚠️ Este código ya existe</span>
            )}
            {errors.codigo && (
              <span className="field-error">⚠️ {errors.codigo}</span>
            )}
            {!errors.codigo && !codigoExistente && formData.codigo && (
              <span className="field-success">✓ Código disponible</span>
            )}
            <span className="field-hint">Identificador único del equipo</span>
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📦</span>
              Nombre del Activo *
            </label>
            <input
              type="text"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className={`field-input ${errors.nombre ? 'input-error' : ''}`}
              placeholder="Caminadora TechnoGym"
              maxLength={100}
              required
            />
            {errors.nombre && (
              <span className="field-error">⚠️ {errors.nombre}</span>
            )}
          </div>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📁</span>
              Categoría *
            </label>
            <select
              name="categoria"
              value={formData.categoria}
              onChange={handleChange}
              className={`field-select ${errors.categoria ? 'input-error' : ''}`}
              required
            >
              <option value="">Seleccione una categoría</option>
              {categorias.map(cat => (
                <option key={cat.categoria_activo_id} value={cat.categoria_activo_id}>
                  {cat.nombre}
                </option>
              ))}
            </select>
            {errors.categoria && (
              <span className="field-error">⚠️ {errors.categoria}</span>
            )}
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🔄</span>
              Estado *
            </label>
            <select
              name="estado"
              value={formData.estado}
              onChange={handleChange}
              className="field-select"
              required
            >
              <option value="activo">✓ Activo</option>
              <option value="mantenimiento">🔧 En Mantenimiento</option>
              <option value="inactivo">⏸️ Inactivo</option>
              <option value="baja">🚫 Dado de Baja</option>
            </select>
          </div>
        </div>

        {/* Sección: Información de Compra */}
        <div className="form-section-header">
          <span className="section-icon">💰</span>
          <h2 className="section-title">Información de Compra</h2>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📅</span>
              Fecha de Compra *
            </label>
            <input
              type="date"
              name="fecha_compra"
              value={formData.fecha_compra}
              onChange={handleChange}
              className={`field-input ${errors.fecha_compra ? 'input-error' : ''}`}
              max={new Date().toISOString().split('T')[0]}
              required
            />
            {errors.fecha_compra && (
              <span className="field-error">⚠️ {errors.fecha_compra}</span>
            )}
            <span className="field-hint">Fecha en que se adquirió el equipo</span>
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">💵</span>
              Valor (MXN) *
            </label>
            <input
              type="number"
              name="valor"
              value={formData.valor}
              onChange={handleChange}
              className={`field-input ${errors.valor ? 'input-error' : ''}`}
              placeholder="0.00"
              step="0.01"
              min="0"
              required
            />
            {errors.valor && (
              <span className="field-error">⚠️ {errors.valor}</span>
            )}
            <span className="field-hint">Precio de compra del activo</span>
          </div>
        </div>

        {/* Sección: Ubicación */}
        <div className="form-section-header">
          <span className="section-icon">📍</span>
          <h2 className="section-title">Ubicación</h2>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🏢</span>
              Sede *
            </label>
            <select
              name="sede"
              value={formData.sede}
              onChange={handleChange}
              className={`field-select ${errors.sede ? 'input-error' : ''}`}
              required
            >
              <option value="">Seleccione una sede</option>
              {sedes.map(sede => (
                <option key={sede.id} value={sede.id}>
                  {sede.nombre}
                </option>
              ))}
            </select>
            {errors.sede && (
              <span className="field-error">⚠️ {errors.sede}</span>
            )}
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🚪</span>
              Espacio
            </label>
            <select
              name="espacio"
              value={formData.espacio}
              onChange={handleChange}
              className="field-select"
              disabled={!formData.sede}
            >
              <option value="">Seleccione un espacio (opcional)</option>
              {espaciosFiltrados.map(espacio => (
                <option key={espacio.id} value={espacio.id}>
                  {espacio.nombre}
                </option>
              ))}
            </select>
            <span className="field-hint">
              {!formData.sede ? 'Primero seleccione una sede' : 'Área específica dentro de la sede'}
            </span>
          </div>
        </div>

        <div className="form-row single">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📌</span>
              Ubicación Específica
            </label>
            <input
              type="text"
              name="ubicacion"
              value={formData.ubicacion}
              onChange={handleChange}
              className="field-input"
              placeholder="Ej: Área cardiovascular - Fila 1"
              maxLength={255}
            />
            <span className="field-hint">Descripción detallada de dónde se encuentra el equipo</span>
          </div>
        </div>

        {/* Sección: Detalles Técnicos */}
        <div className="form-section-header">
          <span className="section-icon">🔧</span>
          <h2 className="section-title">Detalles Técnicos</h2>
        </div>

        <div className="form-row">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🏷️</span>
              Marca
            </label>
            <input
              type="text"
              name="marca"
              value={formData.marca}
              onChange={handleChange}
              className="field-input"
              placeholder="Ej: TechnoGym"
              maxLength={100}
            />
            <span className="field-hint">Fabricante del equipo</span>
          </div>

          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📋</span>
              Modelo
            </label>
            <input
              type="text"
              name="modelo"
              value={formData.modelo}
              onChange={handleChange}
              className="field-input"
              placeholder="Ej: Run 700"
              maxLength={100}
            />
            <span className="field-hint">Modelo específico del equipo</span>
          </div>
        </div>

        <div className="form-row single">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">🔢</span>
              Número de Serie
            </label>
            <input
              type="text"
              name="numero_serie"
              value={formData.numero_serie}
              onChange={handleChange}
              className="field-input"
              placeholder="Ej: TG-RUN700-2023-001"
              maxLength={100}
            />
            <span className="field-hint">Número de serie único del fabricante</span>
          </div>
        </div>

        <div className="form-row single">
          <div className="form-field">
            <label className="field-label">
              <span className="label-icon">📝</span>
              Descripción
            </label>
            <textarea
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              className="field-textarea"
              placeholder="Descripción detallada del activo, características especiales, accesorios incluidos, etc."
              rows={4}
            />
            <span className="field-hint">Información adicional relevante del equipo</span>
          </div>
        </div>

        <div className="form-row single">
          <div className="form-field field-file">
            <label className="field-label">
              <span className="label-icon">🖼️</span>
              Imagen del Activo
            </label>
            <div className="file-input-wrapper">
              <input
                type="file"
                name="imagen"
                onChange={handleChange}
                accept="image/*"
              />
              <div className={`file-input-display ${formData.imagen ? 'has-file' : ''}`}>
                <span>
                  {formData.imagen ? formData.imagen.name : 'Haz clic para seleccionar una imagen'}
                </span>
                <span className="file-icon">
                  {formData.imagen ? '✓' : '📁'}
                </span>
              </div>
            </div>
            <span className="field-hint">Formatos permitidos: JPG, PNG, GIF (máx. 5MB)</span>
          </div>
        </div>

        {formData.imagen && (
          <div className="form-row single">
            <div className="image-preview-container">
              <span className="image-preview-label">Vista previa:</span>
              <img
                src={URL.createObjectURL(formData.imagen)}
                alt="Preview"
                className="image-preview"
              />
            </div>
          </div>
        )}

        {/* Botones de acción */}
        <div className="form-actions">
          <button
            type="button"
            onClick={() => navigate('/gestion-equipos/activos')}
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
                {isEdit ? '✓ Actualizar Activo' : '✨ Crear Activo'}
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ActivoForm;
