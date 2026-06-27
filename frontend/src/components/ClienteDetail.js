import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowLeft,
  Pencil,
  BarChart3,
  User,
  Mail,
  Phone,
  Cake,
  VenusAndMars,
  MapPin,
  Dumbbell,
  RefreshCw,
  Calendar,
  Target,
  Siren,
  Users
} from 'lucide-react';
import clienteService from '../services/clienteService';
import './ClienteDetail.css';

function ClienteDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [cliente, setCliente] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCliente();
  }, [id]);

  const fetchCliente = async () => {
    try {
      setLoading(true);
      const response = await clienteService.getCliente(id);
      setCliente(response.data);
      setError('');
    } catch (err) {
      setError('Error al cargar el cliente');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getEstadoColor = (estado) => {
    const colors = {
      'activo': '#10b981',
      'inactivo': '#6b7280',
      'suspendido': '#ef4444'
    };
    return colors[estado] || '#6b7280';
  };

  const getNivelColor = (nivel) => {
    const colors = {
      'principiante': '#60a5fa',
      'intermedio': '#f59e0b',
      'avanzado': '#a78bfa'
    };
    return colors[nivel] || '#60a5fa';
  };

  const getInitials = (nombre, apellidoP, apellidoM) => {
    const n = nombre?.charAt(0) || '';
    const ap = apellidoP?.charAt(0) || '';
    const am = apellidoM?.charAt(0) || '';
    return (n + ap + am).toUpperCase();
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Cargando detalle del cliente...</p>
      </div>
    );
  }

  if (error || !cliente) {
    return (
      <div className="cliente-detail-container">
        <div className="error-card">
          <div className="error-icon"><AlertTriangle size={48} style={{ color: 'var(--warning)' }} /></div>
          <h3>{error || 'Cliente no encontrado'}</h3>
          <button className="btn-back-error" onClick={() => navigate('/clientes')}>
            <ArrowLeft size={18} />
            Volver a la lista
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="cliente-detail-container">
      {/* Header */}
      <div className="detail-header">
        <button className="btn-back" onClick={() => navigate('/clientes')}>
          <ArrowLeft size={18} />
          Volver
        </button>
        <button
          className="btn-edit"
          onClick={() => navigate(`/clientes/edit/${id}`)}
          style={{ color: '#ffffff' }}
        >
          <Pencil size={18} />
          Editar Cliente
        </button>
      </div>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="avatar-large">
          {getInitials(cliente.nombre, cliente.apellido_paterno, cliente.apellido_materno)}
        </div>
        <div className="hero-info">
          <h1 className="cliente-nombre-completo">
            {cliente.nombre} {cliente.apellido_paterno} {cliente.apellido_materno}
          </h1>
          <div className="badges-container">
            <span
              className="estado-badge-large"
              style={{ backgroundColor: getEstadoColor(cliente.estado) }}
            >
              {cliente.estado?.toUpperCase()}
            </span>
            <span
              className="nivel-badge-large"
              style={{ backgroundColor: getNivelColor(cliente.nivel_experiencia) }}
            >
              <BarChart3 size={16} /> {cliente.nivel_experiencia?.toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="detail-grid">

        {/* Información Personal */}
        <div className="info-card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)' }}>
              <User size={24} />
            </div>
            <h2>Información Personal</h2>
          </div>
          <div className="card-content">
            <div className="info-row">
              <span className="info-label"><Mail size={16} /> Email</span>
              <span className="info-value">{cliente.email || 'No especificado'}</span>
            </div>
            <div className="info-row">
              <span className="info-label"><Phone size={16} /> Teléfono</span>
              <span className="info-value">{cliente.telefono || 'No especificado'}</span>
            </div>
            <div className="info-row">
              <span className="info-label"><Cake size={16} /> Fecha de Nacimiento</span>
              <span className="info-value">
                {cliente.fecha_nacimiento
                  ? new Date(cliente.fecha_nacimiento).toLocaleDateString('es-MX', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })
                  : 'No especificado'}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label"><VenusAndMars size={16} /> Sexo</span>
              <span className="info-value">{cliente.sexo || 'No especificado'}</span>
            </div>
            <div className="info-row">
              <span className="info-label"><MapPin size={16} /> Dirección</span>
              <span className="info-value">{cliente.direccion || 'No especificado'}</span>
            </div>
          </div>
        </div>

        {/* Información del Cliente */}
        <div className="info-card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)' }}>
              <Dumbbell size={24} />
            </div>
            <h2>Información del Cliente</h2>
          </div>
          <div className="card-content">
            <div className="info-row">
              <span className="info-label"><BarChart3 size={16} /> Nivel de Experiencia</span>
              <span
                className="nivel-badge-inline"
                style={{ backgroundColor: getNivelColor(cliente.nivel_experiencia) }}
              >
                {cliente.nivel_experiencia?.toUpperCase()}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label"><RefreshCw size={16} /> Estado</span>
              <span
                className="estado-badge-inline"
                style={{ backgroundColor: getEstadoColor(cliente.estado) }}
              >
                {cliente.estado?.toUpperCase()}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label"><Calendar size={16} /> Fecha de Registro</span>
              <span className="info-value">
                {cliente.fecha_registro
                  ? new Date(cliente.fecha_registro).toLocaleDateString('es-MX', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })
                  : 'No especificado'}
              </span>
            </div>
          </div>
        </div>

        {/* Objetivo de Fitness */}
        <div className="info-card full-width">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)' }}>
              <Target size={24} />
            </div>
            <h2>Objetivo de Fitness</h2>
          </div>
          <div className="card-content">
            <p className="objetivo-text">
              {cliente.objetivo_fitness || 'No se ha especificado un objetivo de fitness'}
            </p>
          </div>
        </div>

        {/* Contacto de Emergencia */}
        {(cliente.nombre_contacto || cliente.telefono_contacto) && (
          <div className="info-card full-width">
            <div className="card-header">
              <div className="card-icon" style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' }}>
                <Siren size={24} />
              </div>
              <h2>Contacto de Emergencia</h2>
            </div>
            <div className="card-content">
              <div className="info-grid-3">
                <div className="info-row">
                  <span className="info-label"><User size={16} /> Nombre</span>
                  <span className="info-value">{cliente.nombre_contacto || 'No especificado'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label"><Phone size={16} /> Teléfono</span>
                  <span className="info-value">{cliente.telefono_contacto || 'No especificado'}</span>
                </div>
                <div className="info-row">
                  <span className="info-label"><Users size={16} /> Parentesco</span>
                  <span className="info-value">{cliente.parentesco || 'No especificado'}</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ClienteDetail;
