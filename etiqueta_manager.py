import os
import shutil
from datetime import datetime
from pptx import Presentation

# Configurar rutas (ajustar según tu estructura de carpetas)
CARPETA_ETIQUETAS = "etiquetas"
CARPETA_TEMP = "temp"

def crear_carpetas():
    """Crea las carpetas necesarias si no existen"""
    for carpeta in [CARPETA_ETIQUETAS, CARPETA_TEMP]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

def buscar_etiqueta(cod_articulo):
    """Busca el archivo de etiqueta correspondiente al código de artículo"""
    for archivo in os.listdir(CARPETA_ETIQUETAS):
        if archivo.startswith(f"{cod_articulo}_") and archivo.endswith(".pptx"):
            return os.path.join(CARPETA_ETIQUETAS, archivo)
    return None

def modificar_etiqueta(archivo, nro_lote, fecha_vencimiento):
    """Modifica el contenido de la etiqueta"""
    try:
        prs = Presentation(archivo)
        
        # Formatear fecha de vencimiento
        fecha_formateada = fecha_vencimiento.strftime("%d/%m/%Y")

        # Buscar y reemplazar los textos en todas las diapositivas
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    # Reemplazar marcadores de posición
                    shape.text = shape.text.replace("*fecha vencimiento", fecha_formateada)
                    shape.text = shape.text.replace("*nro de lote", str(nro_lote))

        # Guardar los cambios
        prs.save(archivo)

    except Exception as e:
        raise Exception(f"Error al modificar la etiqueta: {str(e)}")

def procesar_etiqueta(cod_articulo, nro_lote, fecha_vencimiento):
    """Procesa la etiqueta para su impresión"""
    try:
        # Crear carpetas si no existen
        crear_carpetas()
        
        # Buscar el archivo de etiqueta original
        archivo_original = buscar_etiqueta(cod_articulo)
        if not archivo_original:
            raise Exception(f"No se encontró la etiqueta para el artículo {cod_articulo}")

        # Crear nombre para el archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo_temp = os.path.join(CARPETA_TEMP, f"etiqueta_{timestamp}.pptx")

        # Copiar el archivo original
        shutil.copy2(archivo_original, archivo_temp)

        # Modificar el archivo
        modificar_etiqueta(archivo_temp, nro_lote, fecha_vencimiento)

        return archivo_temp

    except Exception as e:
        raise Exception(f"Error al procesar la etiqueta: {str(e)}") 