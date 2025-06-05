import os
import platform
import win32print
import win32api

def configurar_impresora(tamano_papel):
    """Configura los parámetros de la impresora por defecto"""
    try:
        # Obtener la impresora por defecto
        impresora = win32print.GetDefaultPrinter()
        
        # Obtener el handle de la impresora
        handle = win32print.OpenPrinter(impresora)
        
        # Obtener la configuración actual
        info = win32print.GetPrinter(handle, 2)
        
        # Configurar el tamaño del papel
        if tamano_papel == "Grande":
            info['pDevMode'].PaperSize = win32print.DMPAPER_USER
            info['pDevMode'].PaperWidth = 1500  # 150mm
            info['pDevMode'].PaperLength = 1800  # 180mm
        elif tamano_papel == "Chico":
            # Configurar tamaño personalizado (en décimas de milímetro)
            info['pDevMode'].PaperSize = win32print.DMPAPER_USER
            info['pDevMode'].PaperWidth = 1100  # 110mm
            info['pDevMode'].PaperLength = 1800  # 180mm
        
        # Configurar orientación a 270 grados
        info['pDevMode'].Orientation = win32print.DMORIENT_LANDSCAPE
        info['pDevMode'].DM_ORIENTATION = win32print.DMORIENT_LANDSCAPE
        
        # Aplicar la configuración
        win32print.SetPrinter(handle, 2, info, 0)
        win32print.ClosePrinter(handle)
        
        return True
    except Exception as e:
        print(f"Error al configurar la impresora: {str(e)}")
        return False

def imprimir_windows(archivo, tamano_papel):
    """Imprime en Windows usando el comando start"""
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe")
    try:
        # Configurar la impresora antes de imprimir
        configurar_impresora(tamano_papel)
        
        # Imprimir el archivo
        os.startfile(archivo, 'print')
        
    except Exception as e:
        raise Exception(f"Error al imprimir en Windows: {str(e)}")

def imprimir_etiquetas(archivo, cantidad, tamano_papel):
    """Imprime el archivo la cantidad de veces especificada"""
    if cantidad < 0:
        raise ValueError("La cantidad de copias no puede ser negativa")
    if cantidad == 0:
        return  # No hacer nada si la cantidad es 0
        
    try:
        sistema = platform.system()
        for _ in range(cantidad):
            imprimir_windows(archivo, tamano_papel)
    except Exception as e:
        raise Exception(f"Error al imprimir: {str(e)}")

