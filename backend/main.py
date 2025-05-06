import os
from typing import Any, Dict, List
import joblib  # O usa pickle si usaste pickle
import pandas as pd  # O numpy, dependiendo de los datos que espera tu modelo
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # Opcional para la ejecución local
import sqlite3, joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from collections import defaultdict, Counter


# --- Configuración de la aplicación ---
app = FastAPI(title="E-commerce", version="1.0.0")

# --- Configuración de CORS ---
# Permite que tu frontend (corriendo en un dominio/puerto diferente) 
# se comunique con esta API. Ajusta los orígenes para producción.
origins = [
    "http://localhost:3000",  # Puerto predeterminado de React
    "http://localhost:5174",  # Puerto predeterminado de Vite
    "http://localhost:5173",  # Puerto predeterminado de Vite
    
    # Agrega tu URL desplegada aquí más tarde
    # "https://tu-frontend-en-render.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# --- Carga del modelo ---

@app.on_event("startup")
def load_model_on_startup():
    """Carga el modelo cuando la aplicación se inicia."""
    global conn,productos,usuarios,rules,tfidf_vectorizer,tfidf_matrix,nn_model
   # Conexión a la base de datos
    conn = sqlite3.connect("db/market_place.db")

    # Cargar recursos
    productos = pd.read_sql_query("SELECT product_id, product_name FROM products", conn)
    usuarios = pd.read_sql_query("SELECT user_id, segment FROM users", conn)
    rules = joblib.load("models/MBA/MBA_reglas_apriori.joblib")
    tfidf_vectorizer = joblib.load("models/NLP/tfidf_vectorizer.joblib")
    tfidf_matrix = joblib.load("models/NLP/tfidf_matrix.joblib")
    nn_model = NearestNeighbors(n_neighbors=20, metric='cosine').fit(tfidf_matrix)

@app.on_event("shutdown")
async def shutdown():
    """Cerrar la conexión de la base de datos cuando la aplicación se apague."""
    global conn
    conn.close()
# --- Definición del modelo de entrada de datos (Pydantic) ---
# IMPORTANTE: Ajusta estos campos EXACTAMENTE a las características que tu modelo espera,
# con los mismos nombres y tipos de datos.

# --- Definición del modelo de salida de datos (Pydantic) ---

# --- Endpoint raíz (opcional) ---
@app.get("/")
def read_root():
    """Devuelve un mensaje de bienvenida."""
    return {"message": "Bienvenido a la API de E-commerce"}

# Conectar a la base de datos SQLite
conn = sqlite3.connect("db/market_place.db")


# --- Endpoint de predicción ---
class PredictionOutput(BaseModel):
    product_id: int
    product_name: str
    aisle_id: int  # ID del pasillo
    department_id: int  # ID del departamento
    peso_total: float
    detalles: Dict[str, Any]

class InputFeatures(BaseModel):
    id: str
    buyList: List[int]
    top_n:int

@app.post("/predict", response_model=List[PredictionOutput])
async def predict_purchase(features: InputFeatures):
    """
    Recibe datos del cliente y devuelve la probabilidad de compra.
    """
    user_id = features.id
    buyList = features.buyList
    top_n = features.top_n
    print(user_id, buyList)

    try:
        # Recomendaciones precalculadas de SVD
        def recomendaciones_svd(user_id, top_n=10):
            query = """
            SELECT product_id, score FROM svd_predictions
            WHERE user_id = ?
            ORDER BY score DESC
            LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(user_id, top_n))
            return df['product_id'].tolist()

        # MBA rápido
        def recomendaciones_mba(productos_en_carrito):
            recomendados = set()
            for producto in productos_en_carrito:
                sub_rules = rules[rules['antecedents'].apply(lambda x: producto in x)]
                recomendados.update(sub_rules['consequents'].explode().tolist())
            return list(recomendados)

        # NLP rápido con NearestNeighbors
        def recomendaciones_nlp(query, top_n=10):
            vector = tfidf_vectorizer.transform([query])
            indices = nn_model.kneighbors(vector, return_distance=False)[0][:top_n]
            return productos.iloc[indices]['product_id'].tolist()

        # Motor híbrido explicativo
        def products_recomender(user_id, productos_en_carrito=[], top_n = 9):
            rec_svd = recomendaciones_svd(user_id, top_n * 2)
            rec_mba = recomendaciones_mba(productos_en_carrito)

            pesos = {'svd': 0.5, 'mba': 0.3, 'nlp': 0.2}
            explicacion = defaultdict(lambda: {'peso_total': 0, 'detalles': {}})

            # SVD
            for pid in rec_svd:
                score = conn.execute("SELECT score FROM svd_predictions WHERE user_id=? AND product_id=?", (user_id, pid)).fetchone()
                if score:
                    explicacion[pid]['peso_total'] += pesos['svd']
                    explicacion[pid]['detalles']['svd'] = round(score[0], 3)

            # MBA
            for pid in rec_mba:
                explicacion[pid]['peso_total'] += pesos['mba']
                explicacion[pid]['detalles']['mba'] = "Regla encontrada"

            # Armar resultados
            final = sorted(explicacion.items(), key=lambda x: x[1]['peso_total'], reverse=True)[:top_n]
            resultados = []
            for pid, data in final:
                nombre = productos[productos['product_id'] == pid]['product_name'].values[0]
                
                # Aquí se asume que aisle_id y department_id se obtienen de la base de datos
                aisle_id = conn.execute("SELECT aisle_id FROM products WHERE product_id=?", (pid,)).fetchone()[0]
                department_id = conn.execute("SELECT department_id FROM products WHERE product_id=?", (pid,)).fetchone()[0]

                # Crear el resultado con los campos requeridos
                resultados.append({
                    'product_id': pid,
                    'product_name': nombre,
                    'aisle_id': aisle_id,
                    'department_id': department_id,
                    'peso_total': round(data['peso_total'], 3),
                    'detalles': data['detalles']
                })
            return resultados

        # Obtener resultados de las recomendaciones
        resultados = products_recomender(user_id, buyList,top_n)
        
        # Devolver las predicciones
        return resultados

    except KeyError as e:
        # Error común si faltan columnas o están nombradas incorrectamente en el DataFrame
        print(f"Error de clave en el procesamiento de los datos de entrada: {e}")
        raise HTTPException(status_code=422, detail=f"Campo de datos de entrada inválido o faltante: {e}")
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno durante el procesamiento de la predicción: {e}")

@app.get("/search")
async def search_products(search: str):
    """
    Recibe un texto de búsqueda como parámetro de consulta y devuelve los productos más relevantes.
    Devuelve los productos más vendidos (top sellers) basados en la cantidad vendida.
    """
    try:
        # Cargar datos de la tabla 'products'
        query = "SELECT product_id, product_name, aisle_id, department_id FROM products"
        products = pd.read_sql_query(query, conn)
        
        # Verifica si no se obtuvieron productos
        if products.empty:
            raise HTTPException(status_code=404, detail="No se encontraron productos en la base de datos.")
        
        # Cargar el vectorizador y la matriz TF-IDF guardados
        vectorizer = joblib.load('models/NLP/tfidf_vectorizer.joblib')
        tfidf_matrix = joblib.load('models/NLP/tfidf_matrix.joblib')

        # Función de búsqueda
        query_clean = search.lower()  # Normaliza la búsqueda
        query_vec = vectorizer.transform([query_clean])  # Transforma la consulta al mismo espacio vectorial
        similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()  # Calcula la similitud de coseno
        
        # Obtenemos los índices de los productos más similares
        top_indices = similarity.argsort()[::-1][:15]

        # Seleccionamos los productos más similares basados en los índices
        resultados = products.iloc[top_indices][['product_id', 'product_name', 'aisle_id', 'department_id']]
        
        # Verifica si hay resultados
        if resultados.empty:
            raise HTTPException(status_code=404, detail="No se encontraron productos relevantes para la búsqueda.")
        
        # Devuelve los resultados en formato de lista de diccionarios
        return resultados.to_dict(orient="records")
    
    except Exception as e:
        # Captura y devuelve cualquier error inesperado
        raise HTTPException(status_code=500, detail=str(e))

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login(request: LoginRequest):
    """
    Endpoint para iniciar sesión de usuario con el nombre de usuario y contraseña.
    """
    try:
        # Consultar si el usuario existe en la base de datos
        query = "SELECT user_id FROM users WHERE user_id = :username"
        
        # Leer los datos de la base de datos utilizando pandas
        user_data = pd.read_sql_query(query, conn, params={"username": request.username})
        
        # Verifica si no se obtuvo el usuario
        if user_data.empty:
            raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
        
        # Verificar si la contraseña proporcionada coincide con la almacenada
        
        # Si todo está bien, devuelve un mensaje de éxito
        return {"message": "Inicio de sesión exitoso", "username": request.username}

    except Exception as e:
        # Si ocurre algún error en el proceso
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }

# --- Punto de entrada opcional para ejecución local ---
# Render usará Gunicorn, no esto directamente.
# if __name__ == "__main__":
#    print("Iniciando servidor Uvicorn en http://127.0.0.1:8000")
#    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
