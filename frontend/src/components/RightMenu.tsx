import React from 'react';
import './RightMenu.css'; // Para estilos específicos, si quieres
import { Product } from '../types/product';

interface RightMenuProps {
  products: Product[];
  onRemove: (product: Product) => void;
  onClear: () => void;
  onBuy: () => void;
  isOpen: boolean;
  onClose: () => void;
}

const RightMenu: React.FC<RightMenuProps> = ({
  products,
  onRemove,
  onClear,
  onBuy,
  isOpen,
  onClose,
}) => {
  const getInitial = (name: string) => name.charAt(0).toUpperCase();

  return (
    <div className={`right-menu ${isOpen ? 'open' : ''}`}>
      <div className="right-menu-header">
        <p className="close-btn" onClick={onClose}>
          ←
        </p>
        <h2>Tu Carrito</h2>
      </div>
      {products.length === 0 ? (
        <p>El carrito está vacío.</p>
      ) : (
        <div className="cart-items-container">
          <ul className="cart-items">
            {products.map((product) => (
              <li key={product.product_id} className="cart-item">
                <div className="product-image">
                  <span className="product-initial">
                    {getInitial(product.product_name)}
                  </span>
                </div>
                <div className="product-info">
                  <span className="product-name">{product.product_name}</span>
                  <button
                    className="remove-btn"
                    onClick={() => onRemove(product)}>
                    Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
      {products.length > 0 && (
        <div className="menu-actions">
          <button onClick={onBuy}>Comprar</button>
          <button onClick={onClear}>Vaciar Cesta</button>
        </div>
      )}
    </div>
  );
};

export default RightMenu;
