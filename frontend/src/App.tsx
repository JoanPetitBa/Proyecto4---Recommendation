import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ProductCard from './components/ProductCard.tsx';
import './App.css';
import { Product } from './types/product.ts';
import RightMenu from './components/RightMenu';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [userLoged, setUserLoged] = useState('');

  const [search, setSearch] = useState('');
  const [result, setResult] = useState<Product[]>([]);
  const [topSellers, setTopSellers] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [buyList, setBuyList] = useState<Product[]>([]);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  console.log(buyList);
  const apiUrl = 'http://localhost:8000';

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');

    try {
      const response = await axios.post(`${apiUrl}/login`, {
        username,
        password,
      });
      if (response.status === 200) {
        setIsLoggedIn(true);
        setUserLoged(username);
        setUsername('');
        setPassword('');
      } else {
        setLoginError('Credenciales incorrectas.');
      }
    } catch (err) {
      setLoginError('Error al iniciar sesión.');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const performSearch = async (query: string) => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get(
        `${apiUrl}/search?search=${encodeURIComponent(query)}`
      );
      setResult(response.data);
    } catch (err) {
      setError('Error al buscar los productos.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTopSellers = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await axios.get(`${apiUrl}/topSellers`);
      setTopSellers(response.data);
    } catch (err) {
      setError('Error al obtener los productos más vendidos.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (search.trim() !== '') {
        performSearch(search);
      } else {
        setResult([]);
      }
    }, 500);
    return () => clearTimeout(delayDebounce);
  }, [search]);

  useEffect(() => {
    fetchTopSellers();
  }, [, userLoged]);

  // Si no está logueado, mostrar formulario de login
  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <h1>Iniciar Sesión</h1>
        <form onSubmit={handleLogin}>
          <div>
            <label htmlFor="username">ID Usuario:</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="password">Contraseña:</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Ingresar</button>
        </form>
        {loginError && <p className="error-message">{loginError}</p>}
      </div>
    );
  }

  return (
    <>
      {!isMenuOpen && (
        <>
          <div className="user-info">
            <div className="user-details">
              <span className="user-label">Usuario: </span>
              <strong className="user-name">{userLoged}</strong>
            </div>
            <button
              className="logout-button"
              onClick={() => {
                setIsLoggedIn(false);
                setSearch('');
                setResult([]);
                setTopSellers([]);
                setBuyList([]);
              }}>
              Cerrar sesión
            </button>
          </div>

          <div className="cart-button-container">
            <button onClick={() => setIsMenuOpen(true)}>
              🛒 Ver Carrito
              {buyList.length > 0 && (
                <span className="cart-badge">{buyList.length}</span>
              )}
            </button>
          </div>
        </>
      )}

      <h1>Búsqueda de Productos</h1>

      <form onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="search">Buscar Producto:</label>
          <input
            id="search"
            type="text"
            name="search"
            value={search}
            onChange={handleChange}
            required
          />
        </div>
      </form>

      {isLoading && <p>Buscando...</p>}
      {error && <p className="error-message">{error}</p>}

      {result.length > 0 ? (
        <div className="result-grid">
          {result.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              buttonText="Añadir Producto"
              onButtonPress={(product) =>
                setBuyList((prevList) => [...prevList, product])
              }
            />
          ))}
        </div>
      ) : (
        !isLoading && (
          <div className="result-grid">
            {topSellers.map((product) => (
              <ProductCard
                key={product.product_id}
                product={product}
                buttonText="Añadir Producto"
                onButtonPress={(product) =>
                  setBuyList((prevList) => [...prevList, product])
                }
              />
            ))}
          </div>
        )
      )}

      <RightMenu
        products={buyList}
        onRemove={(product) =>
          setBuyList((prevList) =>
            prevList.filter((p) => p.product_id !== product.product_id)
          )
        }
        onClear={() => setBuyList([])}
        onBuy={() => {
          alert('Compra realizada con éxito 🚀');
          setBuyList([]);
        }}
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
      />
    </>
  );
}

export default App;
