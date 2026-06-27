import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dumbbell, Check, AlertTriangle, Mail, Lock, ArrowRight } from 'lucide-react';
import authService from '../services/authService';
import './Login.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Primero hacer login
      await authService.login(email, password);
      console.log('Login exitoso');

      // Luego obtener el dashboard del usuario
      const dashboardData = await authService.getUserDashboard();
      console.log('Dashboard data recibida:', dashboardData);

      // Redirigir al dashboard correspondiente según el rol
      const dashboardRoute = authService.getDashboardRoute();
      console.log('Redirigiendo a:', dashboardRoute);

      navigate(dashboardRoute);
    } catch (err) {
      console.error('Error completo:', err);
      console.error('Error response:', err.response);

      // Si el error es 403 (sin permisos), mostrar mensaje específico
      if (err.response?.status === 403) {
        setError('No tienes permisos asignados. Contacta al administrador.');
      } else {
        setError(
          err.response?.data?.detail ||
          err.response?.data?.error ||
          'Error al iniciar sesión. Verifica tus credenciales.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-content">
        {/* Panel izquierdo - Marca */}
        <div className="login-brand">
          <div className="brand-content">
            <div className="brand-icon">
              <span className="icon-gym"><Dumbbell size={64} /></span>
            </div>
            <h1 className="brand-title">GIMNASIO</h1>
            <p className="brand-subtitle">Sistema de Gestión Integral</p>
            <div className="brand-features">
              <div className="feature-item">
                <span className="feature-icon"><Check size={16} /></span>
                <span>Gestión de Clientes</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon"><Check size={16} /></span>
                <span>Control de Accesos</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon"><Check size={16} /></span>
                <span>Inventario y Ventas</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon"><Check size={16} /></span>
                <span>Gestión de Personal</span>
              </div>
            </div>
          </div>
        </div>

        {/* Panel derecho - Formulario */}
        <div className="login-form-panel">
          <div className="login-form-container">
            <div className="login-header">
              <h2>Bienvenido</h2>
              <p>Ingresa tus credenciales para continuar</p>
            </div>

            {error && (
              <div className="error-message">
                <span className="error-icon"><AlertTriangle size={20} style={{ color: 'var(--warning)' }} /></span>
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="login-form">
              <div className="form-group">
                <label htmlFor="email">
                  <span className="label-icon"><Mail size={16} /></span>
                  Correo Electrónico
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="correo@ejemplo.com"
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  <span className="label-icon"><Lock size={16} /></span>
                  Contraseña
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="form-input"
                />
              </div>

              <button type="submit" className="btn-login" disabled={loading}>
                {loading ? (
                  <>
                    <span className="spinner"></span>
                    <span>Iniciando sesión...</span>
                  </>
                ) : (
                  <>
                    <span>Ingresar</span>
                    <span className="btn-arrow"><ArrowRight size={18} /></span>
                  </>
                )}
              </button>
            </form>

            <div className="login-footer">
              <p>© 2025 Gimnasio. Todos los derechos reservados.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
