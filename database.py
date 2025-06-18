import pyodbc
from datetime import datetime
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración de la conexión desde variables de entorno
DB_CONFIG = {
    'DRIVER': '{SQL Server}',
    'SERVER': os.getenv('DB_HOST'),
    'DATABASE': os.getenv('DB_NAME'),
    'UID': os.getenv('DB_USER'),
    'PWD': os.getenv('DB_PASSWORD'),
    'PORT': os.getenv('DB_PORT'),
}

def conectar_db():
    """Establece conexión con la base de datos SQL Server"""
    try:
        return pyodbc.connect(**DB_CONFIG)
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
            SELECT cod_articulo, fec_venc, nom_articulo
            FROM v_cz_articulolote 
            WHERE nro_lote = ?
        """
        cursor.execute(query, (str(nro_lote),))
        resultado = cursor.fetchone()
        if resultado:
            return resultado[0], formatear_fecha(resultado[1]), resultado[2]
        return None

    except Exception as e:
        raise Exception(f"Error al consultar la base de datos: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close() 

def formatear_fecha(fecha):
    """Convierte el formato de fecha de 'YYYY-MM-DD HH:MM:SS.mmm' a 'DD-MM-YYYY'."""    
    if isinstance(fecha, datetime):
        return fecha.strftime('%d-%m-%Y')
    # Si es string, asume que viene como 'YYYY-MM-DD' o 'YYYY-MM-DD HH:MM:SS.mmm'
    fecha_str = fecha.split()[0]  # Tomar solo la parte de la fecha
    try:
        fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
        return fecha_dt.strftime('%d-%m-%Y')
    except ValueError:
        # Si el formato no es el esperado, devolver el string original
        return fecha_str