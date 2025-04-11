import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

interface Product {
  product_id: number;
  product_name: string;
  aisle_id: number;
  department_id: number;
}

function App() {
  const [search, setSearch] = useState('');
  const [result, setResult] = useState<Product[] | null>(null); // Explicitly typing result as an array of Product or null
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setResult(null);

    // const apiUrl = process.env.VITE_APP_API_URL || 'http://localhost:8000';
    const apiUrl = 'http://localhost:8000';

    try {
      // Realizar la solicitud GET con el parámetro de búsqueda
      const response = await axios.get(
        `${apiUrl}/search?search=${encodeURIComponent(search)}`
      );

      // Manejar la respuesta de la API
      setResult(response.data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Error al buscar los productos.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Búsqueda de Productos</h1>
      <form onSubmit={handleSubmit}>
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
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Buscando...' : 'Buscar'}
        </button>
      </form>

      {/* Mostrar resultados */}
      {error && <p className="error-message">{error}</p>}
      {result && (
        <div className="result">
          <h2>Resultados:</h2>
          <ul>
            {result.map((product) => (
              <li key={product.product_id}>{product.product_name}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
