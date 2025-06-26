import os
import platform
import win32print
import win32api
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener nombre de la impresora desde .env
NOMBRE_IMPRESORA = os.getenv('NOMBRE_IMPRESORA')

def configurar_impresora(tamano_papel):
    
    """
    Ajusta ancho, largo y orientación en la impresora definida en .env
    y verifica que el driver acepte el cambio.
    """
    handle = win32print.OpenPrinter(NOMBRE_IMPRESORA)
    try:
        info = win32print.GetPrinter(handle, 2)
        dm = info['pDevMode']          # alias breve

        # --- 1. Elegir valores según tamaño ---
        if tamano_papel == "Grande":
            width, length = 1500, 1800   # 150 mm × 180 mm
        elif tamano_papel == "Chico":
            width, length = 1100, 1800   # 110 mm × 180 mm
        else:
            raise ValueError("Tamaño no reconocido")

        # --- 2. Cargar en el DEVMODE ---
        dm.PaperSize   = 256            # DM_PAPER_USER → tamaño personalizado
        dm.PaperWidth  = width          # décimas de mm
        dm.PaperLength = length
        dm.Orientation = win32print.DMORIENT_LANDSCAPE

        # --- 3. Activar los flags para que el driver los respete ---
        dm.Fields |= (win32print.DM_PAPERSIZE |
                      win32print.DM_PAPERLENGTH |
                      win32print.DM_PAPERWIDTH |
                      win32print.DM_ORIENTATION)

        # --- 4. Validar & aplicar con DocumentProperties ---
        win32print.DocumentProperties(
            None,            # hwnd
            handle,
            NOMBRE_IMPRESORA,
            dm,              # salida
            dm,              # entrada (misma struct)
            win32print.DM_IN_BUFFER | win32print.DM_OUT_BUFFER
        )

        # --- 5. Guardar como Preferencias de impresora ---
        info['pDevMode'] = dm
        win32print.SetPrinter(handle, 2, info, 0)

    finally:
        win32print.ClosePrinter(handle)


def leer_config_impresora():
    """Devuelve ancho, largo y orientación grabados en la impresora."""
    handle = win32print.OpenPrinter(NOMBRE_IMPRESORA)
    try:
        dm = win32print.GetPrinter(handle, 2)['pDevMode']
        return dm.PaperWidth, dm.PaperLength, dm.Orientation
    finally:
        win32print.ClosePrinter(handle)


def imprimir_windows(archivo, tamano_papel):
    """Imprime en Windows usando la impresora especificada en .env"""
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe")
    try:
        # Guardar la impresora predeterminada actual
        #impresora_anterior = win32print.GetDefaultPrinter()
      
        # Configurar la impresora antes de imprimir
        configurar_impresora(tamano_papel)
        
        # Establecer la impresora especificada como predeterminada
        #win32print.SetDefaultPrinter(NOMBRE_IMPRESORA)
        win32api.ShellExecute(
            0,
            "printto",                 # cambiamos 'print' → 'printto'
            archivo,                   # ruta del archivo
            f'"{NOMBRE_IMPRESORA}"',   # arg → impresora destino, con comillas
            ".",
            0
        )
        # Imprimir el archivo usando os.startfile
        #os.startfile(archivo, 'print')
    
        """finally:
            # Restaurar la impresora predeterminada original
            win32print.SetDefaultPrinter(impresora_anterior)
        """
    except Exception as e:
        raise Exception(f"Error al imprimir en Windows: {str(e)}")

def imprimir_etiquetas(archivo, cantidad, tamano_papel):
    """Imprime el archivo la cantidad de veces especificada"""
    if cantidad < 0:
        raise ValueError("La cantidad de copias no puede ser negativa")
    if cantidad == 0:
        return  # No hacer nada si la cantidad es 0
        
    try:
        for _ in range(cantidad):
            imprimir_windows(archivo, tamano_papel)
    except Exception as e:
        raise Exception(f"Error al imprimir: {str(e)}")

