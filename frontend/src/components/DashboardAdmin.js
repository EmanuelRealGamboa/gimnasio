import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';
import './Dashboard.css';

function DashboardAdmin() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const data = await authService.getUserDashboard();
        setDashboardData(data);
      } catch (error) {
        console.error('Error al cargar dashboard:', error);
        if (error.response?.status === 401 || error.response?.status === 403) {
          authService.logout();
          navigate('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [navigate]);

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
        <div className="dashboard-header">
          <h2>{dashboardData?.mensaje}</h2>
          <p className="dashboard-subtitle">Panel de {dashboardData?.dashboard}</p>
        </div>

        <div className="dashboard-cards">
          {dashboardData?.accesos && Object.entries(dashboardData.accesos).map(([key, value]) => (
            value && (
              <div key={key} className="dashboard-card">
                <h3>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
                <p>Acceso habilitado</p>
              </div>
            )
          ))}
        </div>

        <div className="dashboard-section">
          <h3>Acciones Rápidas</h3>
          <div className="action-buttons">
            <button onClick={() => navigate('/employees')} className="action-btn">
              Gestionar Empleados
            </button>
            <button onClick={() => navigate('/employees/new')} className="action-btn">
              Crear Nuevo Empleado
            </button>
          </div>
        </div>

        <div className="dashboard-section">
          <h3>Mis Permisos</h3>
          <div className="permissions-list">
            {dashboardData?.permisos && dashboardData.permisos.map((permiso, index) => (
              <span key={index} className="permission-badge">
                {permiso.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
  );
}

export default DashboardAdmin;
