import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
      <div className="login-card">
        <div className="login-logo">
          <div className="logo-box">G</div>
        </div>

        <h3>Inicia Sesión</h3>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Correo</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="correo@ejemplo.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? 'Iniciando sesión...' : 'Ingresar'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
