import sqlite3, joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Conectar a la base de datos SQLite
conn = sqlite3.connect("db/market_place.db")

# Cargar datos de la tabla 'products'
query = "SELECT product_id, product_name, aisle_id, department_id FROM products"
products = pd.read_sql_query(query, conn)

# Cargar el vectorizador y la matriz TF-IDF guardados
vectorizer = joblib.load('models/tfidf_vectorizer.joblib')
tfidf_matrix = joblib.load('models/tfidf_matrix.joblib')

# Función de búsqueda
def buscar_productos(query, top_n=10):
    query_clean = query.lower()
    query_vec = vectorizer.transform([query_clean])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
    top_indices = similarity.argsort()[::-1][:top_n]
    return products.iloc[top_indices][['product_id', 'product_name', 'aisle_id', 'department_id']]

# Ejemplo de uso
resultados = buscar_productos("rice")
print(resultados)
