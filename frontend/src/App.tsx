import { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';

interface Product {
  id: number;
  name: string;
}

const products: Product[] = [
  { id: 1, name: 'Chocolate blanco' },
  { id: 2, name: 'Café molido' },
  { id: 3, name: 'Galletas de avena' },
  { id: 4, name: 'Leche vegetal' },
];

function App() {
  const [selectedProductId, setSelectedProductId] = useState<number>(
    products[0].id
  );
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [recommended, setRecommended] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const selectedProduct = products.find((p) => p.id === selectedProductId);

  useEffect(() => {
    const fetchImage = async () => {
      if (!selectedProduct) return;
      setLoading(true);

      try {
        const response = await axios.get('https://api.pexels.com/v1/search', {
          params: {
            query: selectedProduct.name,
            per_page: 1,
          },
          headers: {
            Authorization:
              'lZeUuH90LJs8HDtrlVm31nyOtwB5U50N80bDcVAuiyl0lgHUDAZ5eMs7', // 👈 pon tu API key aquí
          },
        });

        const photos = response.data.photos;
        if (photos.length > 0) {
          setImageUrl(photos[0].src.large);
        } else {
          setImageUrl(null);
        }
      } catch (err) {
        console.error('Error fetching image:', err);
        setImageUrl(null);
      } finally {
        setLoading(false);
      }
    };

    const generateRecommendations = () => {
      // lógica simple de ejemplo
      if (!selectedProduct) return;
      const recs = products
        .filter((p) => p.id !== selectedProduct.id)
        .slice(0, 2)
        .map((p) => p.name);
      setRecommended(recs);
    };

    fetchImage();
    generateRecommendations();
  }, [selectedProductId]);

  return (
    <div className="App">
      <h1>🛒 Marketplace Inteligente</h1>

      <label htmlFor="product">Selecciona un producto:</label>
      <select
        id="product"
        value={selectedProductId}
        onChange={(e) => setSelectedProductId(Number(e.target.value))}>
        {products.map((product) => (
          <option key={product.id} value={product.id}>
            {product.name}
          </option>
        ))}
      </select>

      {loading && <p>Cargando imagen...</p>}

      {imageUrl && (
        <div>
          <h2>{selectedProduct?.name}</h2>
          <img
            src={imageUrl}
            alt={selectedProduct?.name}
            style={{ maxWidth: '400px' }}
          />
        </div>
      )}

      {recommended.length > 0 && (
        <div>
          <h3>Recomendado para tu cesta:</h3>
          <ul>
            {recommended.map((rec) => (
              <li key={rec}>{rec}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
