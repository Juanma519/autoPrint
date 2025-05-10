import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la conexión desde variables de entorno
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

def conectar_db():
    """Establece conexión con la base de datos"""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")

def obtener_datos_lote(nro_lote):
    """Obtiene los datos del lote desde la base de datos"""
    conn = None
    cursor = None
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        
        # Ajusta esta consulta según tu esquema de base de datos
        query = """
            SELECT cod_articulo, fecha_vencimiento 
            FROM v_cz_articulolote 
            WHERE nro_lote = %s
        """
        cursor.execute(query, (nro_lote,))
        resultado = cursor.fetchone()
        
        if resultado:
            return resultado[0], resultado[1]
        return None

    except Exception as e:
        raise Exception(f"Error al consultar la base de datos: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 