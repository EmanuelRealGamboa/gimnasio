import React from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Header.css';

function Header() {
  const navigate = useNavigate();
  const userData = authService.getUserData();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  if (!userData) {
    return null;
  }

  // Obtener el primer rol o usar "Usuario" como predeterminado
  const rol = userData.roles && userData.roles.length > 0
    ? userData.roles[0]
    : 'Usuario';

  // Construir el nombre completo
  const nombre = userData.user?.persona
    ? `${userData.user.persona.nombre} ${userData.user.persona.apellido_paterno} ${userData.user.persona.apellido_materno || ''}`.trim()
    : userData.user?.email || 'Usuario';

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="header-left">
          <h1>Sistema de Gestión de Gimnasio</h1>
        </div>
        <div className="header-right">
          <div className="user-info">
            <span className="greeting">
              Hola <strong>{rol}</strong>: <span className="user-name">{nombre}</span>
            </span>
          </div>
          <button onClick={handleLogout} className="logout-button">
            Cerrar Sesión
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;
