import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Layout from './components/Layout';
import EmployeeList from './components/EmployeeList';
import EmployeeFormWizard from './components/EmployeeFormWizard';
import EmployeeDetail from './components/EmployeeDetail';
import DashboardAdmin from './components/DashboardAdmin';
import DashboardEntrenador from './components/DashboardEntrenador';
import DashboardRecepcion from './components/DashboardRecepcion';
import DashboardSupervisor from './components/DashboardSupervisor';
import DashboardLimpieza from './components/DashboardLimpieza';
import ProtectedRoute from './components/ProtectedRoute';
import authService from './services/authService';
import './App.css';

function App() {
  // Función para redirigir al dashboard correcto según el rol
  const getDashboardRedirect = () => {
    if (authService.isAuthenticated()) {
      const dashboardRoute = authService.getDashboardRoute();
      return <Navigate to={dashboardRoute} replace />;
    }
    return <Navigate to="/login" replace />;
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />

          {/* Dashboards por rol */}
          <Route
            path="/dashboard/admin"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardAdmin />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard/entrenador"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardEntrenador />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard/recepcion"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardRecepcion />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard/supervisor"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardSupervisor />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard/limpieza"
            element={
              <ProtectedRoute>
                <Layout>
                  <DashboardLimpieza />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de empleados */}
          <Route
            path="/employees"
            element={
              <ProtectedRoute>
                <Layout>
                  <EmployeeList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/employees/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <EmployeeFormWizard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/employees/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <EmployeeFormWizard />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/employees/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <EmployeeDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Redirección raíz */}
          <Route path="/" element={getDashboardRedirect()} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
