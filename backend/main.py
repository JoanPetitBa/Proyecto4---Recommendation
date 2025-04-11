import os
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
# --- Configuración de la aplicación ---
app = FastAPI(title="E-commerce", version="1.0.0")

# --- Configuración de CORS ---
# Permite que tu frontend (corriendo en un dominio/puerto diferente) 
# se comunique con esta API. Ajusta los orígenes para producción.
origins = [
    "http://localhost:3000",  # Puerto predeterminado de React
    "http://localhost:5174",  # Puerto predeterminado de Vite
    
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
MODEL_PATH = 'modelo_ecommerce.pkl'
model = None

@app.on_event("startup")
def load_model_on_startup():
    """Carga el modelo cuando la aplicación se inicia."""
    global model
    global conn
    conn = sqlite3.connect("db/market_place.db", check_same_thread=False)
    if not os.path.exists(MODEL_PATH):
        print(f"Advertencia: El archivo del modelo no se encuentra en {MODEL_PATH}")
        return  # No hace nada si no se encuentra el modelo
    try:
        model = joblib.load(MODEL_PATH)
        print("Modelo cargado exitosamente.")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        # La API sigue corriendo sin el modelo si hay un error

@app.on_event("shutdown")
async def shutdown():
    """Cerrar la conexión de la base de datos cuando la aplicación se apague."""
    global conn
    conn.close()
# --- Definición del modelo de entrada de datos (Pydantic) ---
# IMPORTANTE: Ajusta estos campos EXACTAMENTE a las características que tu modelo espera,
# con los mismos nombres y tipos de datos.
class InputFeatures(BaseModel):
    edad: int
    categoria_producto: str
    historial_compras: bool  # Ejemplo: True o False
    monto_gastado: float
    # ... agrega TODAS las características que tu modelo necesita

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "edad": 35,
                    "categoria_producto": "Electrónica",
                    "historial_compras": True,
                    "monto_gastado": 150.75,
                    # ... valores de ejemplo para todas las características
                }
            ]
        }
    }

# --- Definición del modelo de salida de datos (Pydantic) ---
class PredictionOutput(BaseModel):
    probabilidad_compra: float = Field(..., example=0.85)

# --- Endpoint raíz (opcional) ---
@app.get("/")
def read_root():
    """Devuelve un mensaje de bienvenida."""
    return {"message": "Bienvenido a la API de E-commerce"}

# Conectar a la base de datos SQLite
conn = sqlite3.connect("db/market_place.db")


@app.get("/search")
async def search_products(search: str):
    """
    Recibe un texto de búsqueda como parámetro de consulta y devuelve los productos más relevantes.
    """
    try:
        # Cargar datos de la tabla 'products'
        query = "SELECT product_id, product_name, aisle_id, department_id FROM products"
        products = pd.read_sql_query(query, conn)

        # Cargar el vectorizador y la matriz TF-IDF guardados
        vectorizer = joblib.load('models/tfidf_vectorizer.joblib')
        tfidf_matrix = joblib.load('models/tfidf_matrix.joblib')

        # Función de búsqueda
        query_clean = search.lower()
        query_vec = vectorizer.transform([query_clean])
        similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
        top_indices = similarity.argsort()[::-1][:10]

        resultados = products.iloc[top_indices][['product_id', 'product_name', 'aisle_id', 'department_id']]

        # Verifica si hay resultados
        if resultados.empty:
            raise HTTPException(status_code=404, detail="No se encontraron productos.")

        return resultados.to_dict(orient="records")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en la búsqueda: {e}")
# --- Endpoint de predicción ---
@app.post("/predict", response_model=PredictionOutput)
async def predict_purchase(features: InputFeatures):
    """
    Recibe datos del cliente y devuelve la probabilidad de compra.
    """
    global model
    if model is None:
        # Esto no debería ocurrir si el evento de inicio se ejecutó correctamente,
        # pero es una buena práctica.
        raise HTTPException(status_code=503, detail="Modelo no cargado o error durante la carga.")

    try:
        # 1. Convierte los datos de entrada al formato que el modelo espera.
        #    Esto es CRUCIAL y depende totalmente de cómo entrenaste tu modelo.
        data_dict = features.dict()  # Utiliza .dict() para Pydantic v1
        data_df = pd.DataFrame([data_dict])

        # 2. Realiza la predicción.
        #    Si tu modelo devuelve probabilidades directamente (por ejemplo, `predict_proba`):
        probabilities = model.predict_proba(data_df)  # o data_array
        # Suponiendo que la clase 1 corresponde a "compra"
        compra_probability = probabilities[0][1]

        # 3. Devuelve el resultado.
        return PredictionOutput(probabilidad_compra=compra_probability)

    except KeyError as e:
         # Error común si faltan columnas o están nombradas incorrectamente en el DataFrame
         print(f"Error de clave en el procesamiento de los datos de entrada: {e}")
         raise HTTPException(status_code=422, detail=f"Campo de datos de entrada inválido o faltante: {e}")
    except Exception as e:
        print(f"Error durante la predicción: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno durante el procesamiento de la predicción: {e}")

# --- Punto de entrada opcional para ejecución local ---
# Render usará Gunicorn, no esto directamente.
# if __name__ == "__main__":
#    print("Iniciando servidor Uvicorn en http://127.0.0.1:8000")
#    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
