import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Layout from './components/Layout';
import EmployeeList from './components/EmployeeList';
import EmployeeFormWizard from './components/EmployeeFormWizard';
import EmployeeDetail from './components/EmployeeDetail';
import ClienteList from './components/ClienteList';
import ClienteForm from './components/ClienteForm';
import ClienteDetail from './components/ClienteDetail';
import MembresiaList from './components/MembresiaList';
import MembresiaForm from './components/MembresiaForm';
import Instalaciones from './components/Instalaciones';
import GestionEquipos from './components/GestionEquipos';
import ActivoList from './components/ActivoList';
import ActivoForm from './components/ActivoForm';
import ActivoDetail from './components/ActivoDetail';
import MantenimientoList from './components/MantenimientoList';
import MantenimientoForm from './components/MantenimientoForm';
import MantenimientoDetail from './components/MantenimientoDetail';
import ProveedorList from './components/ProveedorList';
import ProveedorForm from './components/ProveedorForm';
import SedeList from './components/SedeList';
import SedeForm from './components/SedeForm';
import EspacioList from './components/EspacioList';
import EspacioForm from './components/EspacioForm';
import DashboardAdmin from './components/DashboardAdmin';
import DashboardEntrenador from './components/DashboardEntrenador';
import DashboardRecepcion from './components/DashboardRecepcion';
import DashboardSupervisor from './components/DashboardSupervisor';
import DashboardLimpieza from './components/DashboardLimpieza';
import CategoriaProductoList from './components/CategoriaProductoList';
import CategoriaProductoForm from './components/CategoriaProductoForm';
import ProductoList from './components/ProductoList';
import ProductoForm from './components/ProductoForm';
import InventarioList from './components/InventarioList';
import ClientesMembresiaList from './components/ClientesMembresiaList';
import ClienteMembresiaDetail from './components/ClienteMembresiaDetail';
import VentaProductos from './components/VentaProductos';
import VentasHistorial from './components/VentasHistorial';
import SuscripcionesHistorial from './components/SuscripcionesHistorial';
import ControlAccesos from './components/ControlAccesos';
import HorariosList from './components/HorariosList';
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
            path="/employees/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <EmployeeDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de instalaciones (panel unificado) */}
          <Route
            path="/instalaciones"
            element={
              <ProtectedRoute>
                <Layout>
                  <Instalaciones />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de sedes */}
          <Route
            path="/sedes"
            element={
              <ProtectedRoute>
                <Layout>
                  <SedeList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/sedes/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <SedeForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/sedes/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <SedeForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de espacios */}
          <Route
            path="/espacios"
            element={
              <ProtectedRoute>
                <Layout>
                  <EspacioList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/espacios/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <EspacioForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/espacios/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <EspacioForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de clientes */}
          <Route
            path="/clientes"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClienteList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClienteForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClienteForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/clientes/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClienteDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de membresías */}
          <Route
            path="/membresias"
            element={
              <ProtectedRoute>
                <Layout>
                  <MembresiaList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/membresias/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <MembresiaForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/membresias/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <MembresiaForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de horarios y reservas */}
          <Route
            path="/horarios"
            element={
              <ProtectedRoute>
                <Layout>
                  <HorariosList />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de equipos y mantenimiento */}
          <Route
            path="/gestion-equipos"
            element={
              <ProtectedRoute>
                <Layout>
                  <GestionEquipos />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/activos"
            element={
              <ProtectedRoute>
                <Layout>
                  <ActivoList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/activos/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <ActivoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/activos/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ActivoDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/activos/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ActivoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/mantenimientos"
            element={
              <ProtectedRoute>
                <Layout>
                  <MantenimientoList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/mantenimientos/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <MantenimientoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/mantenimientos/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <MantenimientoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/mantenimientos/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <MantenimientoDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de proveedores */}
          <Route
            path="/gestion-equipos/proveedores"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProveedorList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/proveedores/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProveedorForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/gestion-equipos/proveedores/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProveedorForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Rutas de gestión de inventario */}
          {/* Categorías de Productos */}
          <Route
            path="/inventario/categorias"
            element={
              <ProtectedRoute>
                <Layout>
                  <CategoriaProductoList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventario/categorias/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <CategoriaProductoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventario/categorias/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <CategoriaProductoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Productos */}
          <Route
            path="/inventario/productos"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProductoList />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventario/productos/new"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProductoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/inventario/productos/edit/:id"
            element={
              <ProtectedRoute>
                <Layout>
                  <ProductoForm />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Inventario */}
          <Route
            path="/inventario"
            element={
              <ProtectedRoute>
                <Layout>
                  <InventarioList />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Ventas - Servicios (Membresías) */}
          <Route
            path="/ventas/servicios"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClientesMembresiaList />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/ventas/servicios/cliente/:clienteId"
            element={
              <ProtectedRoute>
                <Layout>
                  <ClienteMembresiaDetail />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Ventas - Productos (Punto de Venta) */}
          <Route
            path="/ventas/productos"
            element={
              <ProtectedRoute>
                <Layout>
                  <VentaProductos />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Ventas - Historial */}
          <Route
            path="/ventas/historial"
            element={
              <ProtectedRoute>
                <Layout>
                  <VentasHistorial />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Ventas - Suscripciones Historial */}
          <Route
            path="/ventas/suscripciones"
            element={
              <ProtectedRoute>
                <Layout>
                  <SuscripcionesHistorial />
                </Layout>
              </ProtectedRoute>
            }
          />

          {/* Accesos - Control */}
          <Route
            path="/accesos"
            element={
              <ProtectedRoute>
                <Layout>
                  <ControlAccesos />
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
