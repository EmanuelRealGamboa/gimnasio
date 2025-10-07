import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import employeeService from '../services/employeeService';
import roleService from '../services/roleService';
import './EmployeeForm.css';

function EmployeeForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = !!id;

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
    puesto: '',
    departamento: '',
    fecha_contratacion: '',
    tipo_contrato: 'Indefinido',
    salario: '',
    estado: 'Activo',
    rfc: '',
    rol_id: '',
  });

  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRoles();
    if (isEditMode) {
      fetchEmployeeDetail();
    }
  }, [id]);

  const fetchRoles = async () => {
    try {
      const response = await roleService.getRoles();
      setRoles(response.data);
      // Si no hay rol seleccionado y hay roles disponibles, seleccionar el primero
      if (!formData.rol_id && response.data.length > 0) {
        setFormData(prev => ({ ...prev, rol_id: response.data[0].id }));
      }
    } catch (err) {
      console.error('Error al cargar roles:', err);
    }
  };

  const fetchEmployeeDetail = async () => {
    try {
      setLoading(true);
      const response = await employeeService.getEmployee(id);
      const data = response.data;

      setFormData({
        nombre: data.nombre || '',
        apellido_paterno: data.apellido_paterno || '',
        apellido_materno: data.apellido_materno || '',
        fecha_nacimiento: data.fecha_nacimiento || '',
        sexo: data.sexo || '',
        direccion: data.direccion || '',
        telefono: data.telefono || '',
        email: data.email || '',
        password: '', // No mostrar password en edición
        puesto: data.puesto || '',
        departamento: data.departamento || '',
        fecha_contratacion: data.fecha_contratacion || '',
        tipo_contrato: data.tipo_contrato || 'Indefinido',
        salario: data.salario || '',
        estado: data.estado || 'Activo',
        rfc: data.rfc || '',
        rol_id: data.rol_id || 1,
      });
    } catch (err) {
      setError('Error al cargar los datos del empleado');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isEditMode) {
        // En modo edición, no enviar password si está vacío
        const dataToSend = { ...formData };
        if (!dataToSend.password) {
          delete dataToSend.password;
        }
        await employeeService.updateEmployee(id, dataToSend);
        alert('Empleado actualizado exitosamente');
      } else {
        await employeeService.createEmployee(formData);
        alert('Empleado creado exitosamente');
      }
      navigate('/employees');
    } catch (err) {
      const errorMsg = err.response?.data;
      if (typeof errorMsg === 'object') {
        const errors = Object.entries(errorMsg)
          .map(([key, value]) => `${key}: ${value}`)
          .join('\n');
        setError(errors);
      } else {
        setError('Error al guardar el empleado');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEditMode && !formData.email) {
    return <div className="loading">Cargando datos del empleado...</div>;
  }

  return (
    <div className="employee-form-container">
      <div className="form-card">
        <h2>{isEditMode ? 'Editar Empleado' : 'Nuevo Empleado'}</h2>

        {error && (
          <div className="error-message">
            <pre>{error}</pre>
          </div>
        )}

        <form onSubmit={handleSubmit}>
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
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                Contraseña {isEditMode ? '(dejar vacío para no cambiar)' : '*'}
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required={!isEditMode}
              />
            </div>
          </div>

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
              <label htmlFor="rol_id">Rol *</label>
              <select
                id="rol_id"
                name="rol_id"
                value={formData.rol_id}
                onChange={handleChange}
                required
              >
                <option value="">Seleccionar rol</option>
                {roles.map((rol) => (
                  <option key={rol.id} value={rol.id}>
                    {rol.nombre}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/employees')}
            >
              Cancelar
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading
                ? 'Guardando...'
                : isEditMode
                ? 'Actualizar Empleado'
                : 'Crear Empleado'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EmployeeForm;
