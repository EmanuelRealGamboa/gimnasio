import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import dashboardService from '../services/dashboardService';
import instalacionesService from '../services/instalacionesService';
import './DashboardAdmin.css';

function DashboardAdmin() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [sedes, setSedes] = useState([]);
  const [sedeFilter, setSedeFilter] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [rangoPreset, setRangoPreset] = useState('mes_actual');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSedes();
    fetchStats();
  }, []);

  useEffect(() => {
    fetchStats();
  }, [sedeFilter, fechaInicio, fechaFin]);

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      setSedes(response.data.results || response.data);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  const fetchStats = async () => {
    try {
      setLoading(true);
      const filtros = {};
      if (sedeFilter) {
        filtros.sede = sedeFilter;
      }
      if (fechaInicio) {
        filtros.fecha_inicio = fechaInicio;
      }
      if (fechaFin) {
        filtros.fecha_fin = fechaFin;
      }
      const data = await dashboardService.getStats(filtros);
      setStats(data);
      setError(null);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
      setError('Error al cargar las estadísticas del dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleRangoPresetChange = (preset) => {
    setRangoPreset(preset);
    const hoy = new Date();
    let inicio, fin;

    switch (preset) {
      case 'hoy':
        inicio = fin = hoy.toISOString().split('T')[0];
        break;
      case 'ayer':
        const ayer = new Date(hoy);
        ayer.setDate(ayer.getDate() - 1);
        inicio = fin = ayer.toISOString().split('T')[0];
        break;
      case 'ultimos_7_dias':
        fin = hoy.toISOString().split('T')[0];
        const hace7 = new Date(hoy);
        hace7.setDate(hace7.getDate() - 7);
        inicio = hace7.toISOString().split('T')[0];
        break;
      case 'ultimos_30_dias':
        fin = hoy.toISOString().split('T')[0];
        const hace30 = new Date(hoy);
        hace30.setDate(hace30.getDate() - 30);
        inicio = hace30.toISOString().split('T')[0];
        break;
      case 'mes_actual':
        inicio = new Date(hoy.getFullYear(), hoy.getMonth(), 1).toISOString().split('T')[0];
        fin = hoy.toISOString().split('T')[0];
        break;
      case 'mes_anterior':
        const primerDiaMesAnterior = new Date(hoy.getFullYear(), hoy.getMonth() - 1, 1);
        const ultimoDiaMesAnterior = new Date(hoy.getFullYear(), hoy.getMonth(), 0);
        inicio = primerDiaMesAnterior.toISOString().split('T')[0];
        fin = ultimoDiaMesAnterior.toISOString().split('T')[0];
        break;
      case 'personalizado':
        // No cambiar las fechas, el usuario las seleccionará manualmente
        return;
      default:
        return;
    }

    setFechaInicio(inicio);
    setFechaFin(fin);
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  };

  const getTendenciaIcon = (tendencia) => {
    if (tendencia > 0) return '↑';
    if (tendencia < 0) return '↓';
    return '→';
  };

  const getTendenciaClass = (tendencia) => {
    if (tendencia > 0) return 'tendencia-positiva';
    if (tendencia < 0) return 'tendencia-negativa';
    return 'tendencia-neutral';
  };

  // Colores para las gráficas
  const COLORS = ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (loading) {
    return (
      <div className="dashboard-admin-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Cargando estadísticas...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-admin-container">
        <div className="error-message">
          <p>{error}</p>
          <button onClick={fetchStats} className="btn-retry">Reintentar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-admin-container">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>Panel de Administrador</h1>
          <p className="dashboard-subtitle">
            Vista general del negocio - {stats?.periodo?.fecha_inicio} al {stats?.periodo?.fecha_fin}
          </p>
        </div>
        <div className="header-actions">
          <select
            value={sedeFilter}
            onChange={(e) => setSedeFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">Todas las sedes</option>
            {sedes.map(sede => (
              <option key={sede.id} value={sede.id}>{sede.nombre}</option>
            ))}
          </select>
          <button onClick={fetchStats} className="btn-refresh">
            🔄 Actualizar
          </button>
        </div>
      </div>

      {/* Filtros de Fecha */}
      <div className="date-filters-section">
        <div className="date-presets">
          <button
            className={`preset-btn ${rangoPreset === 'hoy' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('hoy')}
          >
            Hoy
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'ayer' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('ayer')}
          >
            Ayer
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'ultimos_7_dias' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('ultimos_7_dias')}
          >
            Últimos 7 días
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'ultimos_30_dias' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('ultimos_30_dias')}
          >
            Últimos 30 días
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'mes_actual' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('mes_actual')}
          >
            Mes Actual
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'mes_anterior' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('mes_anterior')}
          >
            Mes Anterior
          </button>
          <button
            className={`preset-btn ${rangoPreset === 'personalizado' ? 'active' : ''}`}
            onClick={() => handleRangoPresetChange('personalizado')}
          >
            Personalizado
          </button>
        </div>
        {rangoPreset === 'personalizado' && (
          <div className="custom-date-inputs">
            <div className="date-input-group">
              <label>Fecha Inicio:</label>
              <input
                type="date"
                value={fechaInicio}
                onChange={(e) => setFechaInicio(e.target.value)}
                className="date-input"
              />
            </div>
            <div className="date-input-group">
              <label>Fecha Fin:</label>
              <input
                type="date"
                value={fechaFin}
                onChange={(e) => setFechaFin(e.target.value)}
                className="date-input"
              />
            </div>
          </div>
        )}
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
            👥
          </div>
          <div className="kpi-content">
            <div className="kpi-label">Clientes Activos</div>
            <div className="kpi-value">{stats?.kpis?.total_clientes_activos || 0}</div>
            <div className={`kpi-tendencia ${getTendenciaClass(stats?.kpis?.tendencia_clientes)}`}>
              {getTendenciaIcon(stats?.kpis?.tendencia_clientes)} {Math.abs(stats?.kpis?.tendencia_clientes || 0)}% vs mes anterior
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)' }}>
            🎫
          </div>
          <div className="kpi-content">
            <div className="kpi-label">Membresías Activas</div>
            <div className="kpi-value">{stats?.kpis?.membresias_activas || 0}</div>
            <div className="kpi-detail">
              {stats?.kpis?.membresias_vencidas || 0} vencidas • {stats?.kpis?.membresias_por_vencer || 0} por vencer
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
            💰
          </div>
          <div className="kpi-content">
            <div className="kpi-label">Ingresos del Mes</div>
            <div className="kpi-value">{formatCurrency(stats?.kpis?.ingresos_mes || 0)}</div>
            <div className={`kpi-tendencia ${getTendenciaClass(stats?.kpis?.tendencia_ingresos)}`}>
              {getTendenciaIcon(stats?.kpis?.tendencia_ingresos)} {Math.abs(stats?.kpis?.tendencia_ingresos || 0)}% vs mes anterior
            </div>
          </div>
        </div>

        <div className="kpi-card">
          <div className="kpi-icon" style={{ background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)' }}>
            🚪
          </div>
          <div className="kpi-content">
            <div className="kpi-label">Accesos Hoy</div>
            <div className="kpi-value">{stats?.kpis?.accesos_hoy || 0}</div>
            <div className="kpi-detail">
              ✅ {stats?.kpis?.accesos_autorizados || 0} autorizados • ❌ {stats?.kpis?.accesos_denegados || 0} denegados
            </div>
          </div>
        </div>
      </div>

      {/* Gráfica de Tendencia de Accesos */}
      <div className="chart-section">
        <h2 className="section-title">📊 Tendencia de Accesos (Últimos 30 días)</h2>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stats?.graficas?.accesos_30_dias || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="dia"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="total"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
                activeDot={{ r: 6 }}
                name="Accesos"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Gráficas de Ingresos y Membresías */}
      <div className="charts-grid">
        <div className="chart-section">
          <h2 className="section-title">💰 Ingresos por Concepto</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={stats?.graficas?.ingresos_por_concepto || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="concepto"
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                  formatter={(value) => formatCurrency(value)}
                />
                <Legend />
                <Bar
                  dataKey="monto"
                  fill="#22c55e"
                  radius={[8, 8, 0, 0]}
                  name="Monto"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-section">
          <h2 className="section-title">🎫 Distribución de Membresías</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={stats?.graficas?.distribucion_membresias || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ tipo, total }) => `${tipo}: ${total}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="total"
                >
                  {(stats?.graficas?.distribucion_membresias || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Top Productos Más Vendidos */}
      {stats?.graficas?.productos_mas_vendidos?.length > 0 && (
        <div className="chart-section">
          <h2 className="section-title">🔥 Top 10 Productos Más Vendidos</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={stats?.graficas?.productos_mas_vendidos || []}
                layout="vertical"
                margin={{ left: 100 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  type="number"
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis
                  type="category"
                  dataKey="nombre"
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                  width={90}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                  }}
                />
                <Legend />
                <Bar
                  dataKey="cantidad"
                  fill="#3b82f6"
                  radius={[0, 8, 8, 0]}
                  name="Cantidad Vendida"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Gráfica de Evolución de Ingresos Mensuales */}
      {stats?.graficas?.evolucion_ingresos?.length > 0 && (
        <div className="chart-section-full">
          <h2 className="section-title">📈 Evolución de Ingresos Mensuales</h2>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={stats.graficas.evolucion_ingresos}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="mes_corto"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
                tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}
                formatter={(value) => formatCurrency(value)}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="productos"
                stroke="#10b981"
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 4 }}
                activeDot={{ r: 6 }}
                name="Productos"
              />
              <Line
                type="monotone"
                dataKey="membresias"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 4 }}
                activeDot={{ r: 6 }}
                name="Membresías"
              />
              <Line
                type="monotone"
                dataKey="total"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ fill: '#3b82f6', r: 5 }}
                activeDot={{ r: 7 }}
                name="Total"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Comparativas entre Sedes */}
      {stats?.comparativas_sedes?.length > 0 && (
        <div className="comparativas-section">
          <h2 className="section-title">🏢 Comparativa de Rendimiento por Sede</h2>
          <div className="comparativas-grid">
            {stats.comparativas_sedes.map((sede, index) => (
              <div key={index} className="comparativa-card">
                <div className="comparativa-header">
                  <h3>{sede.sede}</h3>
                </div>
                <div className="comparativa-stats">
                  <div className="comparativa-stat">
                    <span className="stat-label">Ingresos</span>
                    <span className="stat-value ingresos">{formatCurrency(sede.ingresos)}</span>
                  </div>
                  <div className="comparativa-stat">
                    <span className="stat-label">Clientes</span>
                    <span className="stat-value">{sede.clientes}</span>
                  </div>
                  <div className="comparativa-stat">
                    <span className="stat-label">Membresías</span>
                    <span className="stat-value">{sede.membresias}</span>
                  </div>
                  <div className="comparativa-stat">
                    <span className="stat-label">Accesos Hoy</span>
                    <span className="stat-value">{sede.accesos}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tablas de Últimas Transacciones */}
      <div className="transactions-grid">
        {/* Últimas Ventas de Productos */}
        {stats?.ultimas_ventas?.length > 0 && (
          <div className="table-section">
            <h2 className="section-title">🛒 Últimas Ventas de Productos</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Total</th>
                    <th>Sede</th>
                    <th>Cajero</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.ultimas_ventas.map((venta) => (
                    <tr key={venta.id}>
                      <td>{venta.fecha}</td>
                      <td className="amount">{formatCurrency(venta.total)}</td>
                      <td>{venta.sede}</td>
                      <td className="text-secondary">{venta.cajero}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Últimas Suscripciones */}
        {stats?.ultimas_suscripciones?.length > 0 && (
          <div className="table-section">
            <h2 className="section-title">🎫 Últimas Suscripciones</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Cliente</th>
                    <th>Membresía</th>
                    <th>Total</th>
                    <th>Sede</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.ultimas_suscripciones.map((suscripcion) => (
                    <tr key={suscripcion.id}>
                      <td>{suscripcion.fecha}</td>
                      <td>{suscripcion.cliente}</td>
                      <td className="text-secondary">{suscripcion.membresia}</td>
                      <td className="amount">{formatCurrency(suscripcion.total)}</td>
                      <td>{suscripcion.sede}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Alertas y Acciones Rápidas */}
      <div className="bottom-grid">
        <div className="alerts-section">
          <h2 className="section-title">🚨 Alertas</h2>
          <div className="alerts-list">
            {stats?.alertas?.membresias_por_vencer > 0 && (
              <div className="alert-item alert-warning">
                <span className="alert-icon">⚠️</span>
                <div className="alert-content">
                  <strong>{stats.alertas.membresias_por_vencer}</strong> membresías por vencer en 7 días
                </div>
                <button
                  className="btn-alert-action"
                  onClick={() => navigate('/ventas/servicios')}
                >
                  Ver
                </button>
              </div>
            )}

            {stats?.alertas?.productos_stock_bajo > 0 && (
              <div className="alert-item alert-danger">
                <span className="alert-icon">📦</span>
                <div className="alert-content">
                  <strong>{stats.alertas.productos_stock_bajo}</strong> productos con stock bajo
                </div>
                <button
                  className="btn-alert-action"
                  onClick={() => navigate('/inventario')}
                >
                  Ver
                </button>
              </div>
            )}

            {stats?.alertas?.accesos_denegados_hoy > 0 && (
              <div className="alert-item alert-info">
                <span className="alert-icon">🚫</span>
                <div className="alert-content">
                  <strong>{stats.alertas.accesos_denegados_hoy}</strong> accesos denegados hoy
                </div>
                <button
                  className="btn-alert-action"
                  onClick={() => navigate('/accesos/monitor')}
                >
                  Ver
                </button>
              </div>
            )}

            {stats?.alertas?.membresias_por_vencer === 0 &&
             stats?.alertas?.productos_stock_bajo === 0 &&
             stats?.alertas?.accesos_denegados_hoy === 0 && (
              <div className="no-alerts">
                <span className="check-icon">✅</span>
                <p>No hay alertas pendientes</p>
              </div>
            )}
          </div>

          {/* Productos con Stock Bajo */}
          {stats?.productos_stock_bajo?.length > 0 && (
            <div className="stock-bajo-section">
              <h3>Productos con Stock Bajo</h3>
              <div className="stock-bajo-list">
                {stats.productos_stock_bajo.map((producto, index) => (
                  <div key={`${producto.id}-${index}`} className="stock-bajo-item">
                    <div className="producto-info">
                      <strong>{producto.nombre}</strong>
                      <span className="producto-categoria">
                        {producto.categoria} {producto.sede && `• ${producto.sede}`}
                      </span>
                    </div>
                    <div className="producto-stock">
                      <span className="stock-badge">{producto.stock} unidades</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="quick-actions-section">
          <h2 className="section-title">⚡ Acciones Rápidas</h2>
          <div className="action-buttons-grid">
            <button onClick={() => navigate('/clientes/new')} className="action-btn">
              <span className="action-icon">➕</span>
              Nuevo Cliente
            </button>
            <button onClick={() => navigate('/ventas/productos')} className="action-btn">
              <span className="action-icon">🛒</span>
              Venta Rápida
            </button>
            <button onClick={() => navigate('/accesos/monitor')} className="action-btn">
              <span className="action-icon">👁️</span>
              Monitor Accesos
            </button>
            <button onClick={() => navigate('/employees/new')} className="action-btn">
              <span className="action-icon">👤</span>
              Nuevo Empleado
            </button>
            <button onClick={() => navigate('/membresias')} className="action-btn">
              <span className="action-icon">🎫</span>
              Gestionar Membresías
            </button>
            <button onClick={() => navigate('/inventario')} className="action-btn">
              <span className="action-icon">📦</span>
              Inventario
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardAdmin;
