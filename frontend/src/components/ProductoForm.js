import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import inventarioService from '../services/inventarioService';
import sedeService from '../services/sedeService';
import './Inventario.css';

function ProductoForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre: '',
    categoria: '',
    precio_unitario: '',
    descripcion: '',
    activo: true,
    sede: '' // Campo para asignar inventario a sede (solo creación)
  });

  const [categorias, setCategorias] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationType, setNotificationType] = useState('success');

  useEffect(() => {
    fetchCategorias();
    fetchSedes();
    if (isEditMode) {
      fetchProducto();
    }
  }, [id]);

  const fetchCategorias = async () => {
    try {
      const response = await inventarioService.getCategorias();
      setCategorias(response.data);
    } catch (err) {
      console.error('Error al cargar categorías:', err);
    }
  };

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchProducto = async () => {
    try {
      setLoading(true);
      const response = await inventarioService.getProducto(id);
      const producto = response.data;

      setFormData({
        nombre: producto.nombre || '',
        categoria: producto.categoria || '',
        precio_unitario: producto.precio_unitario || '',
        descripcion: producto.descripcion || '',
        activo: producto.activo !== undefined ? producto.activo : true,
        sede: '' // En edición, la sede no se muestra porque ya está asignada
      });
    } catch (err) {
      console.error('Error al cargar producto:', err);
      showNotif('Error al cargar el producto', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
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

  const validate = () => {
    const newErrors = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }

    if (!formData.categoria) {
      newErrors.categoria = 'La categoría es requerida';
    }

    if (!formData.precio_unitario || formData.precio_unitario <= 0) {
      newErrors.precio_unitario = 'El precio debe ser mayor a 0';
    }

    // Solo validar sede en modo creación
    if (!isEditMode && !formData.sede) {
      newErrors.sede = 'La sede es requerida para crear el inventario inicial';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validate()) {
      showNotif('Por favor, completa todos los campos requeridos', 'error');
      return;
    }

    try {
      setLoading(true);

      // Preparar datos para enviar al backend
      const dataToSend = {
        nombre: formData.nombre,
        categoria: parseInt(formData.categoria),
        precio_unitario: parseFloat(formData.precio_unitario),
        descripcion: formData.descripcion || '',
        activo: formData.activo
      };

      // Solo agregar sede en modo creación (para crear inventario inicial)
      if (!isEditMode) {
        dataToSend.sede = parseInt(formData.sede);
      }

      if (isEditMode) {
        await inventarioService.updateProducto(id, dataToSend);
        showNotif('✓ Producto actualizado exitosamente', 'success');
      } else {
        await inventarioService.createProducto(dataToSend);
        showNotif('✓ Producto creado exitosamente', 'success');
      }

      setTimeout(() => {
        navigate('/inventario/productos');
      }, 1500);
    } catch (err) {
      console.error('Error al guardar producto:', err);
      const errorMsg = err.response?.data?.detail || `Error al ${isEditMode ? 'actualizar' : 'crear'} el producto`;
      showNotif(errorMsg, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showNotif = (message, type = 'success') => {
    setNotificationMessage(message);
    setNotificationType(type);
    setShowNotification(true);
    setTimeout(() => setShowNotification(false), 3000);
  };

  return (
    <div className="inventario-container">
      {/* Notification */}
      {showNotification && (
        <div className={`notification ${notificationType} show`}>
          {notificationMessage}
        </div>
      )}

      {/* Header */}
      <div className="inventario-header">
        <div>
          <h1>{isEditMode ? '✏️ Editar Producto' : '➕ Nuevo Producto'}</h1>
          <p className="inventario-subtitle">
            {isEditMode ? 'Modifica los datos del producto' : 'Completa los datos para crear un nuevo producto'}
          </p>
        </div>
        <button
          className="btn-secondary"
          onClick={() => navigate('/inventario/productos')}
        >
          ← Volver
        </button>
      </div>

      {/* Form */}
      <div className="form-card">
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3 className="form-section-title">Información del Producto</h3>

            <div className="form-grid">
              <div className="form-group full-width">
                <label htmlFor="nombre">
                  Nombre del Producto <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  className={errors.nombre ? 'error' : ''}
                  placeholder="Ej: Proteína Whey 2kg"
                  disabled={loading}
                />
                {errors.nombre && (
                  <span className="error-message">{errors.nombre}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="categoria">
                  Categoría <span className="required">*</span>
                </label>
                <select
                  id="categoria"
                  name="categoria"
                  value={formData.categoria}
                  onChange={handleChange}
                  className={errors.categoria ? 'error' : ''}
                  disabled={loading}
                >
                  <option value="">Selecciona una categoría</option>
                  {categorias.map(cat => (
                    <option key={cat.categoria_producto_id} value={cat.categoria_producto_id}>
                      {cat.nombre}
                    </option>
                  ))}
                </select>
                {errors.categoria && (
                  <span className="error-message">{errors.categoria}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="precio_unitario">
                  Precio Unitario <span className="required">*</span>
                </label>
                <input
                  type="number"
                  id="precio_unitario"
                  name="precio_unitario"
                  value={formData.precio_unitario}
                  onChange={handleChange}
                  className={errors.precio_unitario ? 'error' : ''}
                  placeholder="0.00"
                  step="0.01"
                  min="0"
                  disabled={loading}
                />
                {errors.precio_unitario && (
                  <span className="error-message">{errors.precio_unitario}</span>
                )}
              </div>

              <div className="form-group full-width">
                <label htmlFor="descripcion">
                  Descripción
                </label>
                <textarea
                  id="descripcion"
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleChange}
                  placeholder="Descripción opcional del producto"
                  rows="3"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="activo">
                  Estado
                </label>
                <select
                  id="activo"
                  name="activo"
                  value={formData.activo}
                  onChange={(e) => setFormData(prev => ({ ...prev, activo: e.target.value === 'true' }))}
                  disabled={loading}
                >
                  <option value="true">Activo</option>
                  <option value="false">Inactivo</option>
                </select>
                <small className="form-help">
                  Solo los productos activos están disponibles para venta
                </small>
              </div>

              {!isEditMode && (
                <div className="form-group">
                  <label htmlFor="sede">
                    Sede para Inventario <span className="required">*</span>
                  </label>
                  <select
                    id="sede"
                    name="sede"
                    value={formData.sede}
                    onChange={handleChange}
                    className={errors.sede ? 'error' : ''}
                    disabled={loading}
                  >
                    <option value="">Selecciona una sede</option>
                    {sedes.map(sede => (
                      <option key={sede.id} value={sede.id}>
                        {sede.nombre}
                      </option>
                    ))}
                  </select>
                  {errors.sede && (
                    <span className="error-message">{errors.sede}</span>
                  )}
                  <small className="form-help">
                    El producto se registrará en el inventario de esta sede con stock inicial de 0. Puedes modificar el stock desde "Inventario por Sede"
                  </small>
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => navigate('/inventario/productos')}
              disabled={loading}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner-small"></span>
                  {isEditMode ? 'Actualizando...' : 'Guardando...'}
                </>
              ) : (
                <>
                  {isEditMode ? '💾 Actualizar' : '➕ Crear'} Producto
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ProductoForm;
