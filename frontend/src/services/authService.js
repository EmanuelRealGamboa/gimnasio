import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

class AuthService {
  async login(email, password) {
    const response = await axios.post(`${API_URL}/token/`, {
      email,
      password,
    });

    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
    }

    return response.data;
  }

  async getUserDashboard() {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No hay token de autenticación');
    }

    // Primero intentar obtener el dashboard default para ver los permisos
    let response;
    try {
      response = await axios.get(`${API_URL}/dashboard/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch (error) {
      // Si falla el default, el usuario no tiene acceso
      throw error;
    }

    const defaultData = response.data;
    const permisos = defaultData.permisos || [];

    // Determinar el dashboard correcto según los permisos (prioridad)
    let dashboardEndpoint = '/dashboard/';
    if (permisos.includes('gestionar_empleados')) {
      dashboardEndpoint = '/dashboard/admin/';
    } else if (permisos.includes('gestionar_instalaciones')) {
      dashboardEndpoint = '/dashboard/supervisor/';
    } else if (permisos.includes('gestionar_entrenamientos')) {
      dashboardEndpoint = '/dashboard/entrenador/';
    } else if (permisos.includes('gestionar_acceso')) {
      dashboardEndpoint = '/dashboard/recepcion/';
    } else if (permisos.includes('gestionar_limpieza')) {
      dashboardEndpoint = '/dashboard/limpieza/';
    }

    // Si no es el dashboard por defecto, obtener el dashboard específico
    if (dashboardEndpoint !== '/dashboard/') {
      response = await axios.get(`${API_URL}${dashboardEndpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    }

    // Guardar información del usuario en localStorage
    if (response.data) {
      localStorage.setItem('user_data', JSON.stringify(response.data));
    }

    return response.data;
  }

  getUserData() {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }

  getDashboardRoute() {
    const userData = this.getUserData();

    console.log('User Data:', userData); // Debug

    if (!userData || !userData.dashboard) {
      console.log('No dashboard data, redirecting to login');
      return '/login';
    }

    // Mapear el nombre del dashboard a la ruta
    const dashboardMap = {
      'Administrador': '/dashboard/admin',
      'Entrenador': '/dashboard/entrenador',
      'Recepción': '/dashboard/recepcion',
      'Supervisor': '/dashboard/supervisor',
      'Personal de Limpieza': '/dashboard/limpieza',
      'Usuario': '/login', // Si no tiene permisos, enviar a login
    };

    const route = dashboardMap[userData.dashboard] || '/login';
    console.log('Redirecting to:', route); // Debug

    return route;
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_data');
  }

  getCurrentUser() {
    return localStorage.getItem('access_token');
  }

  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  }
}

export default new AuthService();
