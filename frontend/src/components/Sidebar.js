import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import './Sidebar.css';

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [expandedMenu, setExpandedMenu] = useState(null);
  const userData = authService.getUserData();


  // Determinar si el usuario es administrador
  const isAdmin = userData?.dashboard === 'Administrador' || userData?.permisos?.includes('gestionar_empleados');

  // Determinar si el usuario es cajero (solo puede ver ventas y accesos)
  const isCajero = (
    userData?.dashboard === 'Recepción' ||
    (userData?.permisos?.includes('gestionar_ventas') || userData?.permisos?.includes('gestionar_acceso')) &&
    !isAdmin
  );

  let menuItems = [
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
      id: 'horarios',
      label: 'Horarios',
      icon: '📅',
      submenu: [
        {
          id: 'tipos-actividad',
          label: 'Tipos de Actividad',
          path: '/horarios/tipos-actividad',
        },
        {
          id: 'horarios-list',
          label: 'Gestión de Horarios',
          path: '/horarios',
        },
        {
          id: 'generar-sesiones',
          label: 'Generar Sesiones',
          path: '/horarios/sesiones',
        },
        {
          id: 'reservas-clases',
          label: 'Reservas de Clases',
          path: '/reservas-clases',
        },
      ],
      adminOnly: true,
    },
    {
      id: 'inventario',
      label: 'Inventario',
      icon: '📦',
      path: '/inventario',
      adminOnly: true,
    },
    {
      id: 'ventas',
      label: 'Ventas',
      icon: '💰',
      submenu: [
        {
          id: 'ventas-servicios',
          label: 'Servicios',
          path: '/ventas/servicios',
        },
        {
          id: 'ventas-productos',
          label: 'Productos',
          path: '/ventas/productos',
        },
        {
          id: 'ventas-historial',
          label: 'Historial',
          path: '/ventas/historial',
        },
        {
          id: 'ventas-suscripciones',
          label: 'Suscripciones',
          path: '/ventas/suscripciones',
        },
      ],
      adminOnly: false,
    },
    {
      id: 'accesos',
      label: 'Accesos',
      icon: '🔐',
      submenu: [
        {
          label: 'Control de Accesos',
          path: '/accesos',
        },
        {
          label: 'Monitor en Tiempo Real',
          path: '/accesos/monitor',
        },
      ],
      adminOnly: false,
    },
    {
      id: 'limpieza',
      label: 'Limpieza',
      icon: '🧹',
      path: '/limpieza',
      adminOnly: true,
    },
  ];

  // Filtrar menú según el rol
  if (isAdmin) {
    menuItems = menuItems.filter(item => true); // Admin ve todo
  } else if (isCajero) {
    // Cajero solo ve ventas y accesos
    menuItems = menuItems.filter(item => ['ventas', 'accesos', 'dashboard'].includes(item.id));
  } else {
    // Otros roles: solo dashboard
    menuItems = menuItems.filter(item => item.id === 'dashboard');
  }

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const toggleSubmenu = (itemId) => {
    setExpandedMenu(expandedMenu === itemId ? null : itemId);
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
          <div key={item.id}>
            {item.submenu ? (
              <>
                <button
                  className={`nav-item ${item.submenu.some(sub => isActive(sub.path)) ? 'active' : ''}`}
                  onClick={() => toggleSubmenu(item.id)}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {!isCollapsed && (
                    <>
                      <span className="nav-label">{item.label}</span>
                      <span className="submenu-arrow">{expandedMenu === item.id ? '▼' : '▶'}</span>
                    </>
                  )}
                </button>
                {!isCollapsed && expandedMenu === item.id && (
                  <div className="submenu">
                    {item.submenu.map((subItem) => (
                      <button
                        key={subItem.id}
                        className={`submenu-item ${isActive(subItem.path) ? 'active' : ''}`}
                        onClick={() => navigate(subItem.path)}
                      >
                        <span className="submenu-label">{subItem.label}</span>
                      </button>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <button
                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                <span className="nav-icon">{item.icon}</span>
                {!isCollapsed && <span className="nav-label">{item.label}</span>}
              </button>
            )}
          </div>
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
