import { Crown, Dumbbell, DollarSign, Brush, HardHat, Check } from 'lucide-react';
import './RoleSelector.css';

const ROLES = [
  {
    id: 'administrador',
    nombre: 'Administrador',
    nombreDB: 'Administrador',
    icon: Crown,
    descripcion: 'Gestión completa del sistema y supervisión',
    color: '#2a2a2a'
  },
  {
    id: 'entrenador',
    nombre: 'Entrenador',
    nombreDB: 'Entrenador',
    icon: Dumbbell,
    descripcion: 'Gestión de entrenamientos y rutinas',
    color: '#22c55e'
  },
  {
    id: 'cajero',
    nombre: 'Cajero',
    nombreDB: 'Recepcionista',
    icon: DollarSign,
    descripcion: 'Gestión de pagos y transacciones',
    color: '#f59e0b'
  },
  {
    id: 'limpieza',
    nombre: 'Personal de Limpieza',
    nombreDB: 'Personal de Limpieza',
    icon: Brush,
    descripcion: 'Gestión de tareas de limpieza',
    color: '#666666'
  },
  {
    id: 'supervisor',
    nombre: 'Supervisor de Espacio',
    nombreDB: 'Supervisor de Instalaciones',
    icon: HardHat,
    descripcion: 'Supervisión de instalaciones y equipamiento',
    color: '#666666'
  }
];

function RoleSelector({ selectedRole, onSelectRole }) {
  return (
    <div className="role-selector-container">
      <h3 className="role-selector-title">Selecciona el Rol del Empleado</h3>
      <p className="role-selector-subtitle">
        Elige el rol que mejor describe las responsabilidades del empleado
      </p>

      <div className="roles-grid">
        {ROLES.map((role) => {
          const RoleIcon = role.icon;
          return (
            <div
              key={role.id}
              className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
              onClick={() => onSelectRole(role.id)}
              style={{
                '--role-color': role.color
              }}
            >
              <div className="role-icon"><RoleIcon size={48} /></div>
              <h4 className="role-name">{role.nombre}</h4>
              <p className="role-description">{role.descripcion}</p>
              <div className="role-check">
                {selectedRole === role.id && <Check size={16} />}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RoleSelector;
export { ROLES };
