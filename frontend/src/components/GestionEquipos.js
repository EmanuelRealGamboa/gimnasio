import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { activoService, mantenimientoService } from '../services/gestionEquiposService';
import './GestionEquipos.css';

const GestionEquipos = () => {
  const [estadisticasActivos, setEstadisticasActivos] = useState(null);
  const [estadisticasMantenimientos, setEstadisticasMantenimientos] = useState(null);
  const [alertas, setAlertas] = useState([]);
  const [vencidos, setVencidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      const [statsActivos, statsMantenimientos, alertasData, vencidosData] = await Promise.all([
        activoService.getEstadisticas(),
        mantenimientoService.getEstadisticas(),
        mantenimientoService.getAlertas(),
        mantenimientoService.getVencidos(),
      ]);

      setEstadisticasActivos(statsActivos.data);
      setEstadisticasMantenimientos(statsMantenimientos.data);
      setAlertas(alertasData.data);
      setVencidos(vencidosData.data);
    } catch (error) {
      console.error('Error al cargar datos:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const totalNotifications = vencidos.length + alertas.length;

  if (loading) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <div className="gestion-equipos-container">
      <div className="header">
        <div className="header-content">
          <div>
            <h1>Gestión de Equipos y Mantenimiento</h1>
            <p className="subtitle">Control y auditoría operativa del gimnasio</p>
          </div>

          {/* Icono de notificaciones */}
          <div className="notification-icon-container">
            <button
              className="notification-button"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              <span className="bell-icon">🔔</span>
              {totalNotifications > 0 && (
                <span className="notification-badge">{totalNotifications}</span>
              )}
            </button>

            {/* Dropdown de notificaciones */}
            {showNotifications && (
              <div className="notifications-dropdown">
                <div className="notifications-header">
                  <h3>Notificaciones</h3>
                  <span className="notifications-count">{totalNotifications}</span>
                </div>

                <div className="notifications-list">
                  {vencidos.length > 0 && (
                    <div className="notification-section">
                      <h4 className="notification-title danger">⚠️ Vencidos ({vencidos.length})</h4>
                      {vencidos.slice(0, 3).map(mant => (
                        <Link
                          key={mant.mantenimiento_id}
                          to={`/gestion-equipos/mantenimientos`}
                          className="notification-item danger"
                          onClick={() => setShowNotifications(false)}
                        >
                          <div className="notification-content">
                            <strong>{mant.activo_codigo}</strong>
                            <span className="notification-date">
                              Vencido hace {Math.abs(mant.dias_para_mantenimiento)} días
                            </span>
                          </div>
                        </Link>
                      ))}
                      {vencidos.length > 3 && (
                        <Link
                          to="/gestion-equipos/mantenimientos"
                          className="notification-view-all"
                          onClick={() => setShowNotifications(false)}
                        >
                          Ver todos los {vencidos.length} vencidos →
                        </Link>
                      )}
                    </div>
                  )}

                  {alertas.length > 0 && (
                    <div className="notification-section">
                      <h4 className="notification-title warning">🔔 Próximos ({alertas.length})</h4>
                      {alertas.slice(0, 3).map(mant => (
                        <Link
                          key={mant.mantenimiento_id}
                          to={`/gestion-equipos/mantenimientos`}
                          className="notification-item warning"
                          onClick={() => setShowNotifications(false)}
                        >
                          <div className="notification-content">
                            <strong>{mant.activo_codigo}</strong>
                            <span className="notification-date">
                              En {mant.dias_para_mantenimiento} días
                            </span>
                          </div>
                        </Link>
                      ))}
                      {alertas.length > 3 && (
                        <Link
                          to="/gestion-equipos/mantenimientos"
                          className="notification-view-all"
                          onClick={() => setShowNotifications(false)}
                        >
                          Ver todas las {alertas.length} alertas →
                        </Link>
                      )}
                    </div>
                  )}

                  {totalNotifications === 0 && (
                    <div className="no-notifications">
                      <p>No hay notificaciones pendientes</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Menú de acceso rápido - Solo funcionales */}
      <div className="quick-access">
        <h2>Acceso Rápido</h2>
        <div className="quick-access-grid">
          <Link to="/gestion-equipos/activos" className="quick-access-card activos">
            <div className="card-icon">🏋️</div>
            <div className="card-content">
              <h3>Activos</h3>
              <p>Inventario de equipos</p>
              {estadisticasActivos && (
                <span className="card-badge">{estadisticasActivos.total_activos}</span>
              )}
            </div>
          </Link>

          <Link to="/gestion-equipos/mantenimientos" className="quick-access-card mantenimientos">
            <div className="card-icon">🔧</div>
            <div className="card-content">
              <h3>Mantenimientos</h3>
              <p>Programar y gestionar</p>
              {estadisticasMantenimientos && (
                <span className="card-badge">{estadisticasMantenimientos.por_estado?.pendiente || 0} pendientes</span>
              )}
            </div>
          </Link>

          <Link to="/gestion-equipos/proveedores" className="quick-access-card proveedores">
            <div className="card-icon">🏢</div>
            <div className="card-content">
              <h3>Proveedores</h3>
              <p>Gestión de servicios</p>
            </div>
          </Link>
        </div>
      </div>

      {/* Estadísticas de Activos */}
      {estadisticasActivos && (
        <div className="stats-section">
          <h2>Estadísticas de Activos</h2>

          <div className="stats-grid">
            <div className="stat-card primary">
              <div className="stat-icon">📦</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasActivos.total_activos}</div>
                <div className="stat-label">Total de Activos</div>
                <div className="stat-detail">{formatCurrency(estadisticasActivos.valor_total)}</div>
              </div>
            </div>

            <div className="stat-card success">
              <div className="stat-icon">✓</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasActivos.por_estado?.activo || 0}</div>
                <div className="stat-label">Activos Operando</div>
                <div className="stat-detail">En funcionamiento</div>
              </div>
            </div>

            <div className="stat-card warning">
              <div className="stat-icon">🔧</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasActivos.por_estado?.mantenimiento || 0}</div>
                <div className="stat-label">En Mantenimiento</div>
                <div className="stat-detail">Fuera de servicio</div>
              </div>
            </div>

            <div className="stat-card danger">
              <div className="stat-icon">⚠️</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasActivos.alertas_mantenimiento || 0}</div>
                <div className="stat-label">Alertas</div>
                <div className="stat-detail">Próximos 15 días</div>
              </div>
            </div>
          </div>

          {/* Gráfica de estado de activos */}
          <div className="chart-section">
            <h3>Distribución por Estado</h3>
            <div className="chart-container">
              <div className="bar-chart">
                {Object.entries(estadisticasActivos.por_estado || {}).map(([estado, cantidad]) => {
                  const percentage = (cantidad / estadisticasActivos.total_activos) * 100;
                  const colors = {
                    activo: '#10b981',
                    mantenimiento: '#f59e0b',
                    baja: '#6b7280',
                    inactivo: '#ef4444'
                  };
                  return (
                    <div key={estado} className="bar-item">
                      <div className="bar-label">{estado.charAt(0).toUpperCase() + estado.slice(1)}</div>
                      <div className="bar-wrapper">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${percentage}%`,
                            backgroundColor: colors[estado] || '#6366f1'
                          }}
                        >
                          <span className="bar-value">{cantidad}</span>
                        </div>
                      </div>
                      <div className="bar-percentage">{percentage.toFixed(1)}%</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Distribución por categoría */}
          {estadisticasActivos.por_categoria && Object.keys(estadisticasActivos.por_categoria).length > 0 && (
            <div className="chart-section">
              <h3>Distribución por Categoría</h3>
              <div className="category-grid">
                {Object.entries(estadisticasActivos.por_categoria).map(([categoria, cantidad], index) => {
                  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];
                  return (
                    <div key={categoria} className="category-item">
                      <div className="category-color" style={{ backgroundColor: colors[index % colors.length] }}></div>
                      <div className="category-info">
                        <div className="category-name">{categoria}</div>
                        <div className="category-value">{cantidad} equipos</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Estadísticas de Mantenimientos */}
      {estadisticasMantenimientos && (
        <div className="stats-section">
          <h2>Estadísticas de Mantenimientos</h2>

          <div className="stats-grid">
            <div className="stat-card primary">
              <div className="stat-icon">📋</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasMantenimientos.total_mantenimientos}</div>
                <div className="stat-label">Total</div>
                <div className="stat-detail">Histórico completo</div>
              </div>
            </div>

            <div className="stat-card warning">
              <div className="stat-icon">⏳</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasMantenimientos.por_estado?.pendiente || 0}</div>
                <div className="stat-label">Pendientes</div>
                <div className="stat-detail">Por realizar</div>
              </div>
            </div>

            <div className="stat-card info">
              <div className="stat-icon">⚙️</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasMantenimientos.por_estado?.en_proceso || 0}</div>
                <div className="stat-label">En Proceso</div>
                <div className="stat-detail">En ejecución</div>
              </div>
            </div>

            <div className="stat-card success">
              <div className="stat-icon">✓</div>
              <div className="stat-info">
                <div className="stat-value">{estadisticasMantenimientos.por_estado?.completado || 0}</div>
                <div className="stat-label">Completados</div>
                <div className="stat-detail">Finalizados</div>
              </div>
            </div>
          </div>

          {/* Gráfica de costos */}
          <div className="chart-section">
            <h3>Análisis de Costos</h3>
            <div className="cost-analysis">
              <div className="cost-card total">
                <div className="cost-icon">💰</div>
                <div className="cost-info">
                  <div className="cost-label">Total Invertido</div>
                  <div className="cost-value">{formatCurrency(estadisticasMantenimientos.costo_total || 0)}</div>
                </div>
              </div>
              <div className="cost-card average">
                <div className="cost-icon">📊</div>
                <div className="cost-info">
                  <div className="cost-label">Costo Promedio</div>
                  <div className="cost-value">{formatCurrency(estadisticasMantenimientos.costo_promedio || 0)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Distribución por tipo con gráfica */}
          {estadisticasMantenimientos.por_tipo && (
            <div className="chart-section">
              <h3>Distribución por Tipo</h3>
              <div className="type-chart">
                {Object.entries(estadisticasMantenimientos.por_tipo).map(([tipo, cantidad]) => {
                  const total = Object.values(estadisticasMantenimientos.por_tipo).reduce((a, b) => a + b, 0);
                  const percentage = (cantidad / total) * 100;
                  const colors = {
                    preventivo: '#3b82f6',
                    correctivo: '#f59e0b'
                  };
                  return (
                    <div key={tipo} className="type-item">
                      <div className="type-header">
                        <span className="type-label">{tipo.charAt(0).toUpperCase() + tipo.slice(1)}</span>
                        <span className="type-value">{cantidad}</span>
                      </div>
                      <div className="type-bar-wrapper">
                        <div
                          className="type-bar"
                          style={{
                            width: `${percentage}%`,
                            backgroundColor: colors[tipo] || '#6366f1'
                          }}
                        ></div>
                      </div>
                      <span className="type-percentage">{percentage.toFixed(1)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
};

export default GestionEquipos;
