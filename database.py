import psycopg2
from datetime import datetime

# Configuración de la conexión (deberás completar estos datos)
DB_CONFIG = {
    'dbname': '',
    'user': '',
    'password': '',
    'host': '',
    'port': ''
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
            FROM lotes 
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