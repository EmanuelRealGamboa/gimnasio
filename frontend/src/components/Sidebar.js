import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import './Sidebar.css';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const userData = authService.getUserData();

  // Determinar si el usuario es administrador
  const isAdmin = userData?.dashboard === 'Administrador' || userData?.permisos?.includes('gestionar_empleados');

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Principal',
      icon: '🏠',
      path: authService.getDashboardRoute(),
    },
    {
      id: 'personal',
      label: 'Personal',
      icon: '👥',
      path: '/employees',
      adminOnly: true,
    },
    {
      id: 'clientes',
      label: 'Clientes',
      icon: '🤸',
      path: '/clientes',
      adminOnly: true,
    },
    {
      id: 'membresias',
      label: 'Membresías',
      icon: '💳',
      path: '/membresias',
      adminOnly: true,
    },
    {
      id: 'instalaciones',
      label: 'Instalaciones',
      icon: '🏢',
      path: '/instalaciones',
      adminOnly: true,
    },
    {
      id: 'gestion-equipos',
      label: 'Equipos y Mantenimiento',
      icon: '🔧',
      path: '/gestion-equipos',
      adminOnly: true,
    },
    {
      id: 'accesos',
      label: 'Accesos',
      icon: '🔐',
      path: '/accesos',
    },
  ].filter(item => !item.adminOnly || isAdmin);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <div className="sidebar-logo">
          {!isCollapsed && <span className="logo-text">GIMNASIO</span>}
          {isCollapsed && <span className="logo-icon">G</span>}
        </div>
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? "Expandir menú" : "Contraer menú"}
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            {!isCollapsed && <span className="nav-label">{item.label}</span>}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        {!isCollapsed && userData && (
          <div className="user-info-sidebar">
            <div className="user-avatar">
              {userData.user?.persona?.nombre?.charAt(0) || userData.user?.email?.charAt(0) || 'U'}
            </div>
            <div className="user-details">
              <div className="user-name">
                {userData.user?.persona ?
                  `${userData.user.persona.nombre} ${userData.user.persona.apellido_paterno}`.substring(0, 20) :
                  userData.user?.email
                }
              </div>
              <div className="user-role">
                {userData.roles?.[0] || 'Usuario'}
              </div>
            </div>
          </div>
        )}
        <button className="logout-btn-sidebar" onClick={handleLogout}>
          <span className="nav-icon">🚪</span>
          {!isCollapsed && <span>Salir</span>}
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
