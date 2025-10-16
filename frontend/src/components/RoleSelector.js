import { useState } from 'react';
import './RoleSelector.css';

const ROLES = [
  {
    id: 'entrenador',
    nombre: 'Entrenador',
    nombreDB: 'entrenador',
    icon: '💪',
    descripcion: 'Gestión de entrenamientos y rutinas',
    color: '#10b981'
  },
  {
    id: 'cajero',
    nombre: 'Cajero',
    nombreDB: 'cajero',
    icon: '💰',
    descripcion: 'Gestión de pagos y transacciones',
    color: '#ec4899'
  },
  {
    id: 'limpieza',
    nombre: 'Personal de Limpieza',
    nombreDB: 'personal de limpieza',
    icon: '🧹',
    descripcion: 'Gestión de tareas de limpieza',
    color: '#06b6d4'
  },
  {
    id: 'supervisor',
    nombre: 'Supervisor de Espacio',
    nombreDB: 'supervisor de espacio',
    icon: '🏗️',
    descripcion: 'Supervisión de instalaciones y equipamiento',
    color: '#8b5cf6'
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
        {ROLES.map((role) => (
          <div
            key={role.id}
            className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
            onClick={() => onSelectRole(role.id)}
            style={{
              '--role-color': role.color
            }}
          >
            <div className="role-icon">{role.icon}</div>
            <h4 className="role-name">{role.nombre}</h4>
            <p className="role-description">{role.descripcion}</p>
            <div className="role-check">
              {selectedRole === role.id && <span>✓</span>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RoleSelector;
export { ROLES };
