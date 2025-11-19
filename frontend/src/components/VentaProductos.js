import { useState, useEffect } from 'react';
import ventasProductosService from '../services/ventasProductosService';
import clienteService from '../services/clienteService';
import instalacionesService from '../services/instalacionesService';
import './VentaProductos.css';

const VentaProductos = () => {
  // Estados principales
  const [productos, setProductos] = useState([]);
  const [carrito, setCarrito] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Estados para el formulario de venta
  const [clientes, setClientes] = useState([]);
  const [sedes, setSedes] = useState([]);
  const [clienteSeleccionado, setClienteSeleccionado] = useState('');
  const [sedeSeleccionada, setSedeSeleccionada] = useState('');
  const [metodoPago, setMetodoPago] = useState('efectivo');
  const [descuentoGlobal, setDescuentoGlobal] = useState('');
  const [notas, setNotas] = useState('');
  const [montoRecibido, setMontoRecibido] = useState('');

  // Cargar datos iniciales
  useEffect(() => {
    fetchClientes();
    fetchSedes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Recargar productos cuando cambie la sede seleccionada
  useEffect(() => {
    if (sedeSeleccionada) {
      fetchProductosDisponibles();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sedeSeleccionada]);

  // Buscar productos cuando cambie la búsqueda
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      fetchProductosDisponibles();
    }, 300);

    return () => clearTimeout(delayDebounceFn);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [busqueda]);

  const fetchProductosDisponibles = async () => {
    try {
      setLoading(true);
      const params = {};
      if (busqueda) params.search = busqueda;

      // CAMBIO CRÍTICO: Agregar sede al request
      if (sedeSeleccionada) {
        params.sede = sedeSeleccionada;
      } else {
        // Si no hay sede seleccionada, limpiar productos y salir
        setProductos([]);
        setLoading(false);
        return;
      }

      const response = await ventasProductosService.getProductosDisponibles(params);

      // Asegurarse de que response.data es un array y filtrar elementos inválidos
      let productosData = [];
      if (Array.isArray(response.data)) {
        productosData = response.data;
      } else if (response.data && Array.isArray(response.data.results)) {
        productosData = response.data.results;
      }

      // Filtrar productos inválidos (null, undefined, o sin producto_id)
      const productosValidos = productosData.filter(p => p && p.producto_id);
      setProductos(productosValidos);
      setError(null);
    } catch (err) {
      console.error('Error al cargar productos:', err);
      setProductos([]);
      setError(err.response?.data?.error || err.response?.data?.detail || 'Error al cargar productos');
    } finally {
      setLoading(false);
    }
  };

  const fetchClientes = async () => {
    try {
      const response = await clienteService.getClientes();
      const clientesData = response.data.results || response.data;
      console.log('Clientes cargados:', clientesData);
      setClientes(clientesData);
    } catch (err) {
      console.error('Error al cargar clientes:', err);
    }
  };

  const fetchSedes = async () => {
    try {
      const response = await instalacionesService.getSedes();
      const sedesData = response.data.results || response.data;
      console.log('Sedes cargadas:', sedesData);
      setSedes(sedesData);
    } catch (err) {
      console.error('Error al cargar sedes:', err);
    }
  };

  // Funciones del carrito
  const agregarAlCarrito = (producto) => {
    console.log('Agregando producto al carrito:', producto);

    // Validar que el producto existe y tiene las propiedades necesarias
    if (!producto || !producto.producto_id) {
      console.error('Producto inválido:', producto);
      setError('Error: producto inválido');
      return;
    }

    const itemExistente = carrito.find(item => item.producto_id === producto.producto_id);

    if (itemExistente) {
      if (itemExistente.cantidad >= (producto.stock || 0)) {
        setError(`No hay suficiente stock de ${producto.nombre || 'este producto'}`);
        return;
      }
      const nuevoCarrito = carrito.map(item =>
        item.producto_id === producto.producto_id
          ? { ...item, cantidad: item.cantidad + 1 }
          : item
      );
      console.log('Actualizando cantidad en carrito:', nuevoCarrito);
      setCarrito(nuevoCarrito);
    } else {
      const nuevoItem = {
        producto_id: producto.producto_id,
        codigo: producto.codigo || '',
        nombre: producto.nombre || 'Sin nombre',
        precio_unitario: parseFloat(producto.precio_unitario) || 0,
        cantidad: 1,
        descuento: 0,
        stock: producto.stock || 0
      };
      console.log('Agregando nuevo item al carrito:', nuevoItem);
      const nuevoCarrito = [...carrito, nuevoItem];
      console.log('Carrito actualizado:', nuevoCarrito);
      setCarrito(nuevoCarrito);
    }
    setError(null);
  };

  const actualizarCantidad = (producto_id, nuevaCantidad) => {
    const item = carrito.find(i => i.producto_id === producto_id);
    if (!item) {
      setError('Producto no encontrado en el carrito');
      return;
    }
    if (nuevaCantidad > (item.stock || 0)) {
      setError(`Stock máximo disponible: ${item.stock || 0}`);
      return;
    }
    if (nuevaCantidad <= 0) {
      eliminarDelCarrito(producto_id);
      return;
    }
    setCarrito(carrito.map(item =>
      item.producto_id === producto_id
        ? { ...item, cantidad: nuevaCantidad }
        : item
    ));
    setError(null);
  };

  const actualizarDescuento = (producto_id, descuento) => {
    const descuentoNum = parseFloat(descuento) || 0;
    if (descuentoNum < 0) return;

    setCarrito(carrito.map(item =>
      item.producto_id === producto_id
        ? { ...item, descuento: descuentoNum }
        : item
    ));
  };

  const eliminarDelCarrito = (producto_id) => {
    setCarrito(carrito.filter(item => item.producto_id !== producto_id));
  };

  const vaciarCarrito = () => {
    setCarrito([]);
    setClienteSeleccionado('');
    setDescuentoGlobal('');
    setNotas('');
    setMontoRecibido('');
    setError(null);
    setSuccess(null);
  };

  // Cálculos
  const calcularSubtotal = () => {
    return carrito.reduce((total, item) => {
      const subtotalItem = item.precio_unitario * item.cantidad;
      return total + (subtotalItem - item.descuento);
    }, 0);
  };

  const calcularTotal = () => {
    const subtotal = calcularSubtotal();
    const descuento = parseFloat(descuentoGlobal) || 0;
    const subtotalConDescuento = subtotal - descuento;
    return subtotalConDescuento;
  };

  const calcularCambio = () => {
    const total = calcularTotal();
    const recibido = parseFloat(montoRecibido) || 0;
    return recibido - total;
  };

  // Procesar venta
  const procesarVenta = async () => {
    // Validaciones
    if (carrito.length === 0) {
      setError('El carrito está vacío');
      return;
    }

    if (!sedeSeleccionada) {
      setError('Debe seleccionar una sede');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const ventaData = {
        cliente_id: clienteSeleccionado || null,
        sede_id: parseInt(sedeSeleccionada),
        metodo_pago: metodoPago,
        productos: carrito.map(item => ({
          producto_id: item.producto_id,
          cantidad: item.cantidad,
          descuento: item.descuento
        })),
        descuento_global: parseFloat(descuentoGlobal) || 0,
        notas: notas
      };

      console.log('Enviando venta:', ventaData);
      const response = await ventasProductosService.crearVenta(ventaData);
      console.log('Venta procesada exitosamente:', response.data);
      setSuccess(`¡Venta creada exitosamente! Ticket #${response.data.venta.venta_id}`);

      // Vaciar carrito y actualizar productos
      vaciarCarrito();
      console.log('Actualizando lista de productos después de la venta...');
      await fetchProductosDisponibles(); // Actualizar stock disponible

      // Limpiar mensaje de éxito después de 5 segundos
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      console.error('Error al procesar venta:', err);
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.detalles) {
        setError(JSON.stringify(err.response.data.detalles));
      } else {
        setError('Error al procesar la venta');
      }
    } finally {
      setLoading(false);
    }
  };

  console.log('Render principal - carrito.length:', carrito.length, 'carrito:', carrito);

  return (
    <div className="venta-productos-container">
      {/* Header con Selector de Sede Prominente */}
      <div className="pos-header">
        <div className="header-left">
          <h1>
            <span className="header-icon">🛒</span>
            Punto de Venta
          </h1>
        </div>

        <div className="sede-selector-header">
          <label className="sede-label">
            <span className="sede-icon">🏢</span>
            Seleccionar Sede:
          </label>
          <select
            value={sedeSeleccionada}
            onChange={(e) => {
              setSedeSeleccionada(e.target.value);
              setCarrito([]); // Limpiar carrito al cambiar de sede
            }}
            className={`sede-select ${!sedeSeleccionada ? 'sede-required' : 'sede-selected'}`}
          >
            <option value="">⚠️ Seleccione una sede...</option>
            {sedes && sedes.length > 0 && sedes.map((sede, index) => {
              if (!sede) return null;
              const sedeId = sede.sede_id || sede.id || sede.pk;
              const sedeNombre = sede.nombre || sede.name || `Sede ${index + 1}`;
              if (!sedeId) return null;
              return (
                <option key={sedeId} value={sedeId}>
                  {sedeNombre}
                </option>
              );
            })}
          </select>

          {sedeSeleccionada && (
            <div className="sede-badge-active">
              <span className="badge-icon">✓</span>
              {sedes.find(s => (s.sede_id || s.id) === parseInt(sedeSeleccionada))?.nombre || 'Sede Activa'}
            </div>
          )}
        </div>
      </div>

      {/* Alerta si no hay sede seleccionada */}
      {!sedeSeleccionada && (
        <div className="alert alert-warning">
          <span className="alert-icon-warning">⚠️</span>
          <div className="alert-content">
            <strong>Seleccione una sede para comenzar</strong>
            <p>Debe seleccionar la sede donde se realizará la venta para ver los productos disponibles.</p>
          </div>
        </div>
      )}

      {/* Mensajes */}
      {error && (
        <div className="alert alert-error">
          <span className="alert-icon" onClick={() => setError(null)}>✕</span>
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <span className="alert-icon" onClick={() => setSuccess(null)}>✕</span>
          {success}
        </div>
      )}

      {/* Layout principal: 2 columnas */}
      <div className="pos-layout">
        {/* Columna izquierda: Productos */}
        <div className="productos-section">
          <div className="search-bar">
            <div className="search-input-wrapper">
              <span className="search-icon">🔍</span>
              <input
                type="text"
                placeholder="Buscar producto por nombre o código..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
                className="search-input"
              />
            </div>
          </div>

          {loading && <div className="loading-spinner">Cargando productos...</div>}

          <div className="productos-grid">
            {productos && productos.length > 0 && productos.map(producto => {
              if (!producto) return null;
              return (
                <div key={producto.producto_id} className="producto-card">
                  <div className="producto-info">
                    <h3>{producto.nombre || 'Sin nombre'}</h3>
                    <p className="producto-codigo">Código: {producto.codigo || 'N/A'}</p>
                    <p className="producto-categoria">{producto.categoria || 'Sin categoría'}</p>
                    <div className="producto-footer">
                      <span className="producto-precio">${producto.precio_unitario || '0.00'}</span>
                      <span className={`producto-stock ${producto.stock === 0 ? 'sin-stock' : producto.stock < 5 ? 'stock-bajo' : 'stock-normal'}`}>
                        Stock: {producto.stock || 0}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => agregarAlCarrito(producto)}
                    className="btn-agregar"
                    disabled={!producto.stock || producto.stock === 0}
                  >
                    <span>+</span>
                    Agregar
                  </button>
                </div>
              );
            })}
          </div>

          {productos.length === 0 && !loading && (
            <div className="empty-state">
              <p>No se encontraron productos disponibles</p>
            </div>
          )}
        </div>

        {/* Columna derecha: Carrito y Pago */}
        <div className="carrito-section">
          <div className="carrito-header">
            <h2>Carrito de Compra</h2>
            {carrito.length > 0 && (
              <button onClick={vaciarCarrito} className="btn-vaciar">
                <span>🗑️</span>
                Vaciar
              </button>
            )}
          </div>

          {/* Items del carrito */}
          <div className="carrito-items">
            {carrito.length === 0 ? (
              <div className="carrito-vacio">
                <span style={{fontSize: '48px'}}>🛒</span>
                <p>El carrito está vacío</p>
              </div>
            ) : (
              <>
                {console.log('Renderizando carrito con items:', carrito)}
                {carrito.map(item => {
                  if (!item || !item.producto_id) return null;
                  return (
                    <div key={item.producto_id} className="carrito-item">
                      <div className="item-header">
                        <div>
                          <h4>{item.nombre}</h4>
                          <p className="item-codigo">{item.codigo}</p>
                        </div>
                        <button
                          onClick={() => eliminarDelCarrito(item.producto_id)}
                          className="btn-eliminar-item"
                        >
                          <span>✕</span>
                        </button>
                      </div>

                      <div className="item-controls">
                        <div className="cantidad-control">
                          <button onClick={() => actualizarCantidad(item.producto_id, item.cantidad - 1)}>
                            <span>−</span>
                          </button>
                          <input
                            type="number"
                            value={item.cantidad}
                            onChange={(e) => actualizarCantidad(item.producto_id, parseInt(e.target.value))}
                            min="1"
                            max={item.stock}
                          />
                          <button onClick={() => actualizarCantidad(item.producto_id, item.cantidad + 1)}>
                            <span>+</span>
                          </button>
                        </div>

                        <div className="item-precios">
                          <span className="item-precio-unitario">${item.precio_unitario.toFixed(2)}</span>
                          <span className="item-subtotal">${(item.precio_unitario * item.cantidad).toFixed(2)}</span>
                        </div>
                      </div>

                      <div className="item-descuento">
                        <label>Descuento:</label>
                        <input
                          type="number"
                          value={item.descuento}
                          onChange={(e) => actualizarDescuento(item.producto_id, e.target.value)}
                          min="0"
                          step="0.01"
                          placeholder="0.00"
                        />
                      </div>
                    </div>
                  );
                })}
              </>
            )}
          </div>

          {/* Formulario de pago */}
          {carrito.length > 0 && (
            <div className="pago-form">
              {console.log('Renderizando form - Clientes:', clientes.length, 'Sedes:', sedes.length)}
              <div className="form-group">
                <label>Cliente (opcional)</label>
                <select
                  value={clienteSeleccionado}
                  onChange={(e) => setClienteSeleccionado(e.target.value)}
                >
                  <option value="">Cliente Anónimo</option>
                  {clientes && clientes.length > 0 && clientes.map(cliente => {
                    if (!cliente || !cliente.cliente_id) return null;
                    const nombre = cliente.persona?.nombre || cliente.nombre || 'Sin nombre';
                    const apellido = cliente.persona?.apellido_paterno || cliente.apellido_paterno || '';
                    return (
                      <option key={cliente.cliente_id} value={cliente.cliente_id}>
                        {nombre} {apellido}
                      </option>
                    );
                  })}
                </select>
              </div>

              <div className="form-group">
                <label>Método de Pago</label>
                <div className="metodos-pago">
                  <button
                    type="button"
                    className={`metodo-btn ${metodoPago === 'efectivo' ? 'active' : ''}`}
                    onClick={() => setMetodoPago('efectivo')}
                  >
                    <span style={{fontSize: '20px'}}>💵</span>
                    Efectivo
                  </button>
                  <button
                    type="button"
                    className={`metodo-btn ${metodoPago === 'tarjeta' ? 'active' : ''}`}
                    onClick={() => setMetodoPago('tarjeta')}
                  >
                    <span style={{fontSize: '20px'}}>💳</span>
                    Tarjeta
                  </button>
                  <button
                    type="button"
                    className={`metodo-btn ${metodoPago === 'transferencia' ? 'active' : ''}`}
                    onClick={() => setMetodoPago('transferencia')}
                  >
                    <span style={{fontSize: '20px'}}>📱</span>
                    Transferencia
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Descuento Global</label>
                <input
                  type="number"
                  value={descuentoGlobal}
                  onChange={(e) => setDescuentoGlobal(e.target.value)}
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                />
              </div>

              <div className="form-group">
                <label>Notas</label>
                <textarea
                  value={notas}
                  onChange={(e) => setNotas(e.target.value)}
                  placeholder="Notas adicionales..."
                  rows="2"
                />
              </div>

              {/* Resumen de totales */}
              <div className="totales-resumen">
                <div className="total-line">
                  <span>Subtotal:</span>
                  <span>${calcularSubtotal().toFixed(2)}</span>
                </div>
                {(parseFloat(descuentoGlobal) || 0) > 0 && (
                  <div className="total-line descuento">
                    <span>Descuento Global:</span>
                    <span>-${(parseFloat(descuentoGlobal) || 0).toFixed(2)}</span>
                  </div>
                )}
                <div className="total-line total-final">
                  <span>TOTAL A PAGAR:</span>
                  <span>${calcularTotal().toFixed(2)}</span>
                </div>
              </div>

              {/* Sección de efectivo - Monto recibido y cambio */}
              {metodoPago === 'efectivo' && (
                <div className="pago-efectivo-section">
                  <div className="form-group">
                    <label>Monto Recibido *</label>
                    <input
                      type="number"
                      value={montoRecibido}
                      onChange={(e) => setMontoRecibido(e.target.value)}
                      placeholder="0.00"
                      step="0.01"
                      min="0"
                      className="input-monto"
                    />
                  </div>
                  <div className="cambio-display">
                    <div className="cambio-label">Cambio:</div>
                    <div className={`cambio-monto ${calcularCambio() < 0 ? 'negativo' : ''}`}>
                      ${calcularCambio().toFixed(2)}
                    </div>
                  </div>
                  {calcularCambio() < 0 && (
                    <div className="alerta-pago">
                      ⚠️ El monto recibido es insuficiente
                    </div>
                  )}
                </div>
              )}

              <button
                onClick={procesarVenta}
                className="btn-procesar-venta"
                disabled={loading || !sedeSeleccionada || (metodoPago === 'efectivo' && calcularCambio() < 0)}
              >
                {loading ? 'Procesando...' : 'Procesar Venta'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VentaProductos;
