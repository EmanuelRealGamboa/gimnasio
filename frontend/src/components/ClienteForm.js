import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import clienteService from '../services/clienteService';
import sedeService from '../services/sedeService';
import './ClienteForm.css';

function ClienteForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);

  const [formData, setFormData] = useState({
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    sexo: '',
    direccion: '',
    telefono: '',
    email: '',
    password: '',
    sede: '',
    objetivo_fitness: '',
    nivel_experiencia: 'principiante',
    estado: 'activo',
    nombre_contacto: '',
    telefono_contacto: '',
    parentesco: ''
  });

  const [sedes, setSedes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    fetchSedes();
    if (isEditMode) {
      fetchCliente();
    }
  }, [id]);

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchCliente = async () => {
    try {
      setLoading(true);
      const response = await clienteService.getCliente(id);
      const cliente = response.data;

      setFormData({
        nombre: cliente.nombre || '',
        apellido_paterno: cliente.apellido_paterno || '',
        apellido_materno: cliente.apellido_materno || '',
        fecha_nacimiento: cliente.fecha_nacimiento || '',
        sexo: cliente.sexo || '',
        direccion: cliente.direccion || '',
        telefono: cliente.telefono || '',
        email: cliente.email || '',
        password: '', // No cargar password en edición
        sede: cliente.sede || '',
        objetivo_fitness: cliente.objetivo_fitness || '',
        nivel_experiencia: cliente.nivel_experiencia || 'principiante',
        estado: cliente.estado || 'activo',
        nombre_contacto: cliente.nombre_contacto || '',
        telefono_contacto: cliente.telefono_contacto || '',
        parentesco: cliente.parentesco || ''
      });
    } catch (err) {
      setError('Error al cargar el cliente');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.nombre.trim()) {
      newErrors.nombre = 'El nombre es requerido';
    }
    if (!formData.apellido_paterno.trim()) {
      newErrors.apellido_paterno = 'El apellido paterno es requerido';
    }
    if (!formData.apellido_materno.trim()) {
      newErrors.apellido_materno = 'El apellido materno es requerido';
    }
    if (!formData.telefono.trim()) {
      newErrors.telefono = 'El teléfono es requerido';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'El email no es válido';
    }

    // Password es obligatorio solo en modo creación
    if (!isEditMode && !formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password && formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    // Sede es requerida
    if (!formData.sede) {
      newErrors.sede = 'La sede es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError('');

      if (isEditMode) {
        await clienteService.updateCliente(id, formData);
        showSuccessMessage('Cliente actualizado exitosamente');
      } else {
        await clienteService.createCliente(formData);
        showSuccessMessage('Cliente creado exitosamente');
      }

      setTimeout(() => {
        navigate('/clientes');
      }, 1500);
    } catch (err) {
      const errorMessage = err.response?.data?.email?.[0] ||
                          err.response?.data?.message ||
                          'Error al guardar el cliente. Por favor, verifica los datos.';
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

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

  if (loading && isEditMode) {
    return <div className="loading">Cargando cliente...</div>;
  }

  return (
    <div className="cliente-form-container">
      <div className="form-header">
        <h2>{isEditMode ? 'Editar Cliente' : 'Nuevo Cliente'}</h2>
        <button
          className="btn-back"
          onClick={() => navigate('/clientes')}
        >
          ← Volver
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <form onSubmit={handleSubmit} className="cliente-form">
        {/* Información Personal */}
        <div className="form-section">
          <h3>Información Personal</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nombre">
                Nombre <span className="required">*</span>
              </label>
              <input
                type="text"
                id="nombre"
                name="nombre"
                value={formData.nombre}
                onChange={handleChange}
                className={errors.nombre ? 'error' : ''}
                placeholder="Nombre"
              />
              {errors.nombre && <span className="error-text">{errors.nombre}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="apellido_paterno">
                Apellido Paterno <span className="required">*</span>
              </label>
              <input
                type="text"
                id="apellido_paterno"
                name="apellido_paterno"
                value={formData.apellido_paterno}
                onChange={handleChange}
                className={errors.apellido_paterno ? 'error' : ''}
                placeholder="Apellido Paterno"
              />
              {errors.apellido_paterno && <span className="error-text">{errors.apellido_paterno}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="apellido_materno">
                Apellido Materno <span className="required">*</span>
              </label>
              <input
                type="text"
                id="apellido_materno"
                name="apellido_materno"
                value={formData.apellido_materno}
                onChange={handleChange}
                className={errors.apellido_materno ? 'error' : ''}
                placeholder="Apellido Materno"
              />
              {errors.apellido_materno && <span className="error-text">{errors.apellido_materno}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="fecha_nacimiento">Fecha de Nacimiento</label>
              <input
                type="date"
                id="fecha_nacimiento"
                name="fecha_nacimiento"
                value={formData.fecha_nacimiento}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="sexo">Sexo</label>
              <select
                id="sexo"
                name="sexo"
                value={formData.sexo}
                onChange={handleChange}
              >
                <option value="">Seleccionar</option>
                <option value="Masculino">Masculino</option>
                <option value="Femenino">Femenino</option>
                <option value="Otro">Otro</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="telefono">
                Teléfono <span className="required">*</span>
              </label>
              <input
                type="tel"
                id="telefono"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                className={errors.telefono ? 'error' : ''}
                placeholder="1234567890"
                maxLength="10"
              />
              {errors.telefono && <span className="error-text">{errors.telefono}</span>}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="direccion">Dirección</label>
            <textarea
              id="direccion"
              name="direccion"
              value={formData.direccion}
              onChange={handleChange}
              placeholder="Dirección completa"
              rows="3"
            />
          </div>
        </div>

        {/* Información de Cuenta */}
        <div className="form-section">
          <h3>Información de Cuenta</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="email">
                Email <span className="required">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={errors.email ? 'error' : ''}
                placeholder="ejemplo@correo.com"
              />
              {errors.email && <span className="error-text">{errors.email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="password">
                Contraseña {!isEditMode && <span className="required">*</span>}
                {isEditMode && <span className="hint"> (dejar vacío para no cambiar)</span>}
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={errors.password ? 'error' : ''}
                placeholder={isEditMode ? "Dejar vacío para no cambiar" : "Mínimo 6 caracteres"}
                minLength="6"
              />
              {errors.password && <span className="error-text">{errors.password}</span>}
            </div>
          </div>
        </div>

        {/* Información del Cliente */}
        <div className="form-section">
          <h3>Información del Cliente</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nivel_experiencia">Nivel de Experiencia</label>
              <select
                id="nivel_experiencia"
                name="nivel_experiencia"
                value={formData.nivel_experiencia}
                onChange={handleChange}
              >
                <option value="principiante">Principiante</option>
                <option value="intermedio">Intermedio</option>
                <option value="avanzado">Avanzado</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="estado">Estado</label>
              <select
                id="estado"
                name="estado"
                value={formData.estado}
                onChange={handleChange}
              >
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
                <option value="suspendido">Suspendido</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="sede">
                Sede <span className="required">*</span>
              </label>
              <select
                id="sede"
                name="sede"
                value={formData.sede}
                onChange={handleChange}
                className={errors.sede ? 'error' : ''}
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
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="objetivo_fitness">Objetivo de Fitness</label>
            <textarea
              id="objetivo_fitness"
              name="objetivo_fitness"
              value={formData.objetivo_fitness}
              onChange={handleChange}
              placeholder="Ej: Pérdida de peso, ganancia muscular, mejorar resistencia..."
              rows="3"
            />
          </div>
        </div>

        {/* Contacto de Emergencia */}
        <div className="form-section">
          <h3>Contacto de Emergencia</h3>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nombre_contacto">Nombre del Contacto</label>
              <input
                type="text"
                id="nombre_contacto"
                name="nombre_contacto"
                value={formData.nombre_contacto}
                onChange={handleChange}
                placeholder="Nombre completo"
              />
            </div>

            <div className="form-group">
              <label htmlFor="telefono_contacto">Teléfono del Contacto</label>
              <input
                type="tel"
                id="telefono_contacto"
                name="telefono_contacto"
                value={formData.telefono_contacto}
                onChange={handleChange}
                placeholder="1234567890"
                maxLength="10"
              />
            </div>

            <div className="form-group">
              <label htmlFor="parentesco">Parentesco</label>
              <input
                type="text"
                id="parentesco"
                name="parentesco"
                value={formData.parentesco}
                onChange={handleChange}
                placeholder="Ej: Padre, Madre, Hermano, Esposo/a"
              />
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="form-actions">
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => navigate('/clientes')}
            disabled={loading}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Guardando...' : isEditMode ? 'Actualizar Cliente' : 'Crear Cliente'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ClienteForm;
