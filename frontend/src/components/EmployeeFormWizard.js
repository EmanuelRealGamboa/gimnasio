import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import employeeService from '../services/employeeService';
import roleService from '../services/roleService';
import sedeService from '../services/sedeService';
import espacioService from '../services/espacioService';
import RoleSelector, { ROLES } from './RoleSelector';
import WizardSteps from './WizardSteps';
import './EmployeeForm.css';

const WIZARD_STEPS = [
  { label: 'Rol', description: 'Selecciona el rol' },
  { label: 'Datos Personales', description: 'Información personal' },
  { label: 'Datos de Usuario', description: 'Credenciales' },
  { label: 'Datos Laborales', description: 'Información laboral' },
  { label: 'Datos Específicos', description: 'Info del rol' },
  { label: 'Documentos', description: 'Archivos' }
];

function EmployeeFormWizard() {
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);
  const [selectedRoleKey, setSelectedRoleKey] = useState('');

  const [formData, setFormData] = useState({
    // Datos personales
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    fecha_nacimiento: '',
    sexo: '',
    direccion: '',
    telefono: '',

    // Datos de usuario
    email: '',
    password: '',

    // Datos laborales base
    puesto: '',
    departamento: '',
    fecha_contratacion: '',
    tipo_contrato: 'Indefinido',
    salario: '',
    estado: 'Activo',
    rfc: '',
    curp: '',
    nss: '',
    rol_id: '',

    // Datos específicos por rol
    especialidad: '',          // Entrenador
    certificaciones: '',       // Entrenador
    turno: '',                 // Común para varios
    sede_id: '',              // Común para varios
    espacios: []              // ManyToMany
  });

  const [roles, setRoles] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [espacios, setEspacios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Estado para archivos
  const [files, setFiles] = useState({
    identificacion: null,
    comprobante: null,
    certificados: []
  });

  useEffect(() => {
    fetchRoles();
    fetchSedes();
    fetchEspacios();
  }, []);

  // Actualizar rol_id cuando se cargan los roles y ya hay un rol seleccionado
  useEffect(() => {
    if (roles.length > 0 && selectedRoleKey && !formData.rol_id) {
      const roleData = ROLES.find(r => r.id === selectedRoleKey);
      if (roleData) {
        const roleDB = roles.find(r => r.nombre === roleData.nombreDB);
        if (roleDB) {
          setFormData(prev => ({
            ...prev,
            rol_id: roleDB.id
          }));
        }
      }
    }
  }, [roles, selectedRoleKey]);

  // Filtrar espacios cuando cambia la sede seleccionada
  useEffect(() => {
    if (formData.sede_id) {
      console.log('🔍 Filtrando espacios para la sede:', formData.sede_id);
      fetchEspacios(formData.sede_id);
      // Limpiar espacios seleccionados al cambiar de sede
      setFormData(prev => ({
        ...prev,
        espacios: []
      }));
    } else {
      // Si no hay sede seleccionada, cargar todos los espacios
      fetchEspacios();
    }
  }, [formData.sede_id]);

  const fetchRoles = async () => {
    try {
      const response = await roleService.getRoles();
      console.log('📋 Roles cargados desde el backend:', response.data);
      setRoles(response.data);
    } catch (err) {
      console.error('Error al cargar roles:', err);
    }
  };

  const fetchSedes = async () => {
    try {
      const response = await sedeService.getSedes();
      console.log('🏢 Sedes cargadas desde el backend:', response.data);
      setSedes(response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
      setSedes([]);
    }
  };

  const fetchEspacios = async (sedeId = null) => {
    try {
      const response = await espacioService.getEspacios(sedeId);
      console.log('🏋️ Espacios cargados desde el backend:', response.data);
      setEspacios(response.data);
    } catch (err) {
      console.error('Error al cargar espacios:', err);
      setEspacios([]);
    }
  };

  // Función removida - El wizard solo se usa para crear empleados

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleRoleSelect = (roleKey) => {
    setSelectedRoleKey(roleKey);
    const roleData = ROLES.find(r => r.id === roleKey);

    console.log('🎯 Rol seleccionado:', roleKey);
    console.log('📌 Datos del rol:', roleData);
    console.log('🗂️ Roles disponibles en BD:', roles);

    // Buscar el rol en la base de datos por nombreDB
    let rolId = '';
    if (roles.length > 0 && roleData) {
      console.log('🔍 Buscando rol con nombre:', roleData.nombreDB);
      const roleDB = roles.find(r => r.nombre === roleData.nombreDB);
      console.log('✅ Rol encontrado en BD:', roleDB);
      if (roleDB) {
        rolId = roleDB.id;
      }
    }

    console.log('🆔 rol_id asignado:', rolId);

    setFormData(prev => ({
      ...prev,
      rol_id: rolId,
      puesto: roleData?.nombre || '',
      departamento: roleKey === 'entrenador' ? 'Entrenamiento' :
                   roleKey === 'cajero' ? 'Caja' :
                   roleKey === 'supervisor' ? 'Instalaciones' :
                   roleKey === 'limpieza' ? 'Limpieza' :
                   'General'
    }));
  };

  const nextStep = () => {
    if (validateCurrentStep()) {
      setCurrentStep(prev => Math.min(prev + 1, WIZARD_STEPS.length));
    }
  };

  const prevStep = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const validateCurrentStep = () => {
    switch (currentStep) {
      case 1:
        if (!selectedRoleKey) {
          setError('Debes seleccionar un rol');
          return false;
        }
        if (!formData.rol_id) {
          setError('Error al cargar el rol. Por favor, intenta de nuevo.');
          return false;
        }
        console.log('Rol seleccionado:', selectedRoleKey, 'rol_id:', formData.rol_id);
        break;
      case 2:
        if (!formData.nombre || !formData.apellido_paterno || !formData.apellido_materno || !formData.telefono) {
          setError('Completa todos los campos obligatorios');
          return false;
        }
        break;
      case 3:
        if (!formData.email || !formData.password) {
          setError('Completa todos los campos obligatorios');
          return false;
        }
        // Validar que el email termine con @gmail.com
        if (!formData.email.endsWith('@gmail.com')) {
          setError('El email debe terminar con @gmail.com');
          return false;
        }
        break;
      case 4:
        if (!formData.puesto || !formData.fecha_contratacion || !formData.salario || !formData.rfc) {
          setError('Completa todos los campos obligatorios');
          return false;
        }
        break;
    }
    setError('');
    return true;
  };

  const handleFinalSubmit = async () => {
    setError('');
    setLoading(true);

    try {
      // Crear FormData para enviar archivos y datos
      const formDataToSend = new FormData();

      // Agregar todos los campos del formulario
      Object.keys(formData).forEach(key => {
        if (formData[key] !== null && formData[key] !== undefined && formData[key] !== '') {
          if (Array.isArray(formData[key])) {
            formDataToSend.append(key, JSON.stringify(formData[key]));
          } else {
            formDataToSend.append(key, formData[key]);
          }
        }
      });

      // Agregar archivos si existen
      if (files.identificacion) {
        formDataToSend.append('identificacion', files.identificacion);
      }
      if (files.comprobante) {
        formDataToSend.append('comprobante', files.comprobante);
      }
      if (files.certificados && files.certificados.length > 0) {
        files.certificados.forEach((cert, index) => {
          formDataToSend.append(`certificado_${index}`, cert);
        });
      }

      console.log('📤 Enviando datos con archivos...');

      // Wizard solo para crear empleados nuevos
      await employeeService.createEmployee(formDataToSend);
      showSuccessMessage('Empleado creado exitosamente');

      // Esperar 2 segundos antes de redirigir para que el usuario vea el mensaje
      setTimeout(() => {
        navigate('/employees');
      }, 2000);
    } catch (err) {
      console.error('Error completo:', err);
      console.error('Datos enviados:', formData);
      const errorMsg = err.response?.data;
      if (typeof errorMsg === 'object') {
        const errors = Object.entries(errorMsg)
          .map(([key, value]) => {
            if (Array.isArray(value)) {
              return `${key}: ${value.join(', ')}`;
            }
            return `${key}: ${value}`;
          })
          .join('\n');
        setError(errors);
      } else {
        setError('Error al guardar el empleado: ' + (errorMsg || err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const showSuccessMessage = (message) => {
    // Crear el elemento del modal de éxito
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

    // Remover después de 2 segundos
    setTimeout(() => {
      successModal.remove();
    }, 2000);
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <RoleSelector
            selectedRole={selectedRoleKey}
            onSelectRole={handleRoleSelect}
          />
        );

      case 2:
        return (
          <div className="step-content">
            <h3>Datos Personales</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="nombre">Nombre *</label>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="apellido_paterno">Apellido Paterno *</label>
                <input
                  type="text"
                  id="apellido_paterno"
                  name="apellido_paterno"
                  value={formData.apellido_paterno}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="apellido_materno">Apellido Materno *</label>
                <input
                  type="text"
                  id="apellido_materno"
                  name="apellido_materno"
                  value={formData.apellido_materno}
                  onChange={handleChange}
                  required
                />
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
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="telefono">Teléfono *</label>
                <input
                  type="tel"
                  id="telefono"
                  name="telefono"
                  value={formData.telefono}
                  onChange={handleChange}
                  required
                  maxLength="10"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="direccion">Dirección</label>
              <input
                type="text"
                id="direccion"
                name="direccion"
                value={formData.direccion}
                onChange={handleChange}
              />
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-content">
            <h3>Datos de Usuario</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="email">Email *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="ejemplo@gmail.com"
                />
                <small style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.25rem', display: 'block' }}>
                  * El email debe terminar con @gmail.com
                </small>
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  Contraseña *
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    style={{ paddingRight: '40px' }}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    style={{
                      position: 'absolute',
                      right: '10px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      fontSize: '1.2rem',
                      padding: '5px',
                      color: '#6b7280'
                    }}
                    title={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="step-content">
            <h3>Datos Laborales</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="puesto">Puesto *</label>
                <input
                  type="text"
                  id="puesto"
                  name="puesto"
                  value={formData.puesto}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="departamento">Departamento *</label>
                <input
                  type="text"
                  id="departamento"
                  name="departamento"
                  value={formData.departamento}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="fecha_contratacion">Fecha de Contratación *</label>
                <input
                  type="date"
                  id="fecha_contratacion"
                  name="fecha_contratacion"
                  value={formData.fecha_contratacion}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="tipo_contrato">Tipo de Contrato *</label>
                <select
                  id="tipo_contrato"
                  name="tipo_contrato"
                  value={formData.tipo_contrato}
                  onChange={handleChange}
                  required
                >
                  <option value="Indefinido">Indefinido</option>
                  <option value="Temporal">Temporal</option>
                  <option value="Por Proyecto">Por Proyecto</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="salario">Salario *</label>
                <input
                  type="number"
                  id="salario"
                  name="salario"
                  value={formData.salario}
                  onChange={handleChange}
                  required
                  step="0.01"
                  min="0"
                />
              </div>

              <div className="form-group">
                <label htmlFor="estado">Estado *</label>
                <select
                  id="estado"
                  name="estado"
                  value={formData.estado}
                  onChange={handleChange}
                  required
                >
                  <option value="Activo">Activo</option>
                  <option value="Inactivo">Inactivo</option>
                  <option value="Suspendido">Suspendido</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="rfc">RFC *</label>
                <input
                  type="text"
                  id="rfc"
                  name="rfc"
                  value={formData.rfc}
                  onChange={handleChange}
                  required
                  maxLength="13"
                />
              </div>

              <div className="form-group">
                <label htmlFor="curp">CURP</label>
                <input
                  type="text"
                  id="curp"
                  name="curp"
                  value={formData.curp}
                  onChange={handleChange}
                  maxLength="18"
                />
              </div>

              <div className="form-group">
                <label htmlFor="nss">NSS</label>
                <input
                  type="text"
                  id="nss"
                  name="nss"
                  value={formData.nss}
                  onChange={handleChange}
                  maxLength="11"
                />
              </div>
            </div>
          </div>
        );

      case 5:
        return renderRoleSpecificFields();

      case 6:
        return (
          <div className="step-content">
            <h3>Documentos</h3>
            <p className="text-secondary" style={{ marginBottom: '20px' }}>
              Adjunta los documentos requeridos del empleado
            </p>

            <div className="form-group">
              <label htmlFor="identificacion">INE / Identificación Oficial</label>
              <input
                type="file"
                id="identificacion"
                accept="image/*,.pdf"
                onChange={(e) => {
                  setFiles(prev => ({
                    ...prev,
                    identificacion: e.target.files[0]
                  }));
                }}
              />
              {files.identificacion && (
                <small style={{ color: '#10b981', display: 'block', marginTop: '5px' }}>
                  ✓ {files.identificacion.name}
                </small>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="comprobante">Comprobante de Domicilio</label>
              <input
                type="file"
                id="comprobante"
                accept="image/*,.pdf"
                onChange={(e) => {
                  setFiles(prev => ({
                    ...prev,
                    comprobante: e.target.files[0]
                  }));
                }}
              />
              {files.comprobante && (
                <small style={{ color: '#10b981', display: 'block', marginTop: '5px' }}>
                  ✓ {files.comprobante.name}
                </small>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="certificados">Certificados (opcional)</label>
              <input
                type="file"
                id="certificados"
                accept="image/*,.pdf"
                multiple
                onChange={(e) => {
                  setFiles(prev => ({
                    ...prev,
                    certificados: Array.from(e.target.files)
                  }));
                }}
              />
              {files.certificados.length > 0 && (
                <small style={{ color: '#10b981', display: 'block', marginTop: '5px' }}>
                  ✓ {files.certificados.length} archivo(s) seleccionado(s)
                </small>
              )}
            </div>

            <div style={{
              marginTop: '30px',
              padding: '15px',
              background: 'rgba(59, 130, 246, 0.1)',
              borderRadius: '8px',
              border: '1px solid rgba(59, 130, 246, 0.3)'
            }}>
              <p style={{ margin: 0, fontSize: '0.9rem', color: '#93c5fd' }}>
                ℹ️ Revisa que toda la información sea correcta antes de continuar.
                Al hacer clic en "Crear Empleado" se registrará el empleado en el sistema.
              </p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const renderRoleSpecificFields = () => {
    if (selectedRoleKey === 'administrador') {
      return (
        <div className="step-content">
          <h3>Datos Específicos - Administrador</h3>
          <p className="text-secondary">
            El rol de administrador no requiere campos adicionales.
          </p>
        </div>
      );
    }

    if (selectedRoleKey === 'entrenador') {
      return (
        <div className="step-content">
          <h3>Datos Específicos - Entrenador</h3>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="especialidad">Especialidad *</label>
              <input
                type="text"
                id="especialidad"
                name="especialidad"
                value={formData.especialidad}
                onChange={handleChange}
                placeholder="Ej: CrossFit, Yoga, Musculación"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="certificaciones">Certificaciones</label>
              <input
                type="text"
                id="certificaciones"
                name="certificaciones"
                value={formData.certificaciones}
                onChange={handleChange}
                placeholder="Ej: ACE, NASM, etc."
              />
            </div>

            <div className="form-group">
              <label htmlFor="turno">Turno *</label>
              <select
                id="turno"
                name="turno"
                value={formData.turno}
                onChange={handleChange}
                required
              >
                <option value="">Seleccionar</option>
                <option value="Matutino">Matutino (6am - 2pm)</option>
                <option value="Vespertino">Vespertino (2pm - 10pm)</option>
                <option value="Nocturno">Nocturno (10pm - 6am)</option>
                <option value="Mixto">Mixto</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="sede_id">Sede *</label>
              <select
                id="sede_id"
                name="sede_id"
                value={formData.sede_id}
                onChange={handleChange}
                required
              >
                <option value="">Seleccionar sede</option>
                {sedes.map(sede => (
                  <option key={sede.id} value={sede.id}>{sede.nombre}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Espacios Asignados</label>
            <div className="checkbox-group">
              {espacios.length > 0 ? (
                espacios.map(espacio => (
                  <label key={espacio.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      value={espacio.id}
                      checked={formData.espacios.includes(espacio.id)}
                      onChange={(e) => {
                        const espacioId = parseInt(e.target.value);
                        setFormData(prev => ({
                          ...prev,
                          espacios: e.target.checked
                            ? [...prev.espacios, espacioId]
                            : prev.espacios.filter(id => id !== espacioId)
                        }));
                      }}
                    />
                    {espacio.nombre}
                  </label>
                ))
              ) : (
                <p style={{ color: '#94a3b8', fontSize: '0.9rem', padding: '0.5rem' }}>
                  {formData.sede_id
                    ? 'No hay espacios disponibles para esta sede'
                    : 'Selecciona una sede primero'}
                </p>
              )}
            </div>
          </div>
        </div>
      );
    }

    // Campos comunes para Recepcionista, Supervisor y Limpieza
    return (
      <div className="step-content">
        <h3>Datos Específicos - {ROLES.find(r => r.id === selectedRoleKey)?.nombre}</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="turno">Turno *</label>
            <select
              id="turno"
              name="turno"
              value={formData.turno}
              onChange={handleChange}
              required
            >
              <option value="">Seleccionar</option>
              <option value="Matutino">Matutino (6am - 2pm)</option>
              <option value="Vespertino">Vespertino (2pm - 10pm)</option>
              <option value="Nocturno">Nocturno (10pm - 6am)</option>
              <option value="Mixto">Mixto</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="sede_id">Sede *</label>
            <select
              id="sede_id"
              name="sede_id"
              value={formData.sede_id}
              onChange={handleChange}
              required
            >
              <option value="">Seleccionar sede</option>
              {sedes.map(sede => (
                <option key={sede.id} value={sede.id}>{sede.nombre}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Espacios Asignados</label>
          <div className="checkbox-group">
            {espacios.length > 0 ? (
              espacios.map(espacio => (
                <label key={espacio.id} className="checkbox-label">
                  <input
                    type="checkbox"
                    value={espacio.id}
                    checked={formData.espacios.includes(espacio.id)}
                    onChange={(e) => {
                      const espacioId = parseInt(e.target.value);
                      setFormData(prev => ({
                        ...prev,
                        espacios: e.target.checked
                          ? [...prev.espacios, espacioId]
                          : prev.espacios.filter(id => id !== espacioId)
                      }));
                    }}
                  />
                  {espacio.nombre}
                </label>
              ))
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.9rem', padding: '0.5rem' }}>
                {formData.sede_id
                  ? 'No hay espacios disponibles para esta sede'
                  : 'Selecciona una sede primero'}
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="employee-form-container">
      <div className="form-card wizard-card">
        <h2>Nuevo Empleado</h2>

        <WizardSteps currentStep={currentStep} steps={WIZARD_STEPS} />

        {error && (
          <div className="error-message">
            <pre>{error}</pre>
          </div>
        )}

        <div>
          {renderStepContent()}

          <div className="form-actions wizard-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => {
                if (currentStep === 1) {
                  navigate('/employees');
                } else {
                  prevStep();
                }
              }}
            >
              {currentStep === 1 ? 'Cancelar' : '← Anterior'}
            </button>

            {currentStep < WIZARD_STEPS.length ? (
              <button
                type="button"
                className="btn btn-primary"
                onClick={nextStep}
              >
                Siguiente →
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleFinalSubmit}
                disabled={loading}
              >
                {loading ? 'Guardando...' : 'Crear Empleado'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default EmployeeFormWizard;
