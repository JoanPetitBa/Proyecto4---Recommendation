import React from 'react';
import './ProductCard.css';
import { Product } from '../types/product';

interface Props {
  product: Product;
  onButtonPress: (product: Product) => void;
  buttonText: string;
}

const ProductCard: React.FC<Props> = ({
  product,
  onButtonPress,
  buttonText,
}) => {
  return (
    <div className="product-card">
      <div className="product-info">
        <h3 className="product-name">{product.product_name}</h3>
        <button onClick={() => onButtonPress(product)} className="action-btn">
          {buttonText}
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
