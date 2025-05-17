import os
import subprocess
import platform

def imprimir_windows(archivo):
    """Imprime en Windows usando el comando start"""
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe")
    try:
        subprocess.run(['start', '/min', '', archivo], shell=True)
        """# Opción 1: Usar el comando 'print' de Windows (funciona para archivos de texto)
        subprocess.run(['print', archivo], shell=True)
        
        # Opción 2: Usar 'os.startfile' con el argumento 'print' (más directo para imprimir archivos asociados)
        # Solo funciona en Windows y con aplicaciones que soportan la acción 'print'
        os.startfile(archivo, 'print')
        
        
        # Opción 3: Usar PowerPoint directamente para imprimir archivos .pptx (requiere que PowerPoint esté instalado)
        import win32com.client
        ppt = win32com.client.Dispatch('PowerPoint.Application')
        presentation = ppt.Presentations.Open(archivo, WithWindow=False)
        presentation.PrintOut()
        presentation.Close()
        ppt.Quit()
      """
    except Exception as e:
        raise Exception(f"Error al imprimir en Windows: {str(e)}")

def imprimir_linux(archivo):
    """Imprime en Linux usando lp"""
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo {archivo} no existe")
    try:
        subprocess.run(['lp', archivo])
    except Exception as e:
        raise Exception(f"Error al imprimir en Linux: {str(e)}")

def imprimir_etiquetas(archivo, cantidad):
    """Imprime el archivo la cantidad de veces especificada"""
    if cantidad < 0:
        raise ValueError("La cantidad de copias no puede ser negativa")
    if cantidad == 0:
        return  # No hacer nada si la cantidad es 0
        
    try:
        sistema = platform.system()
        for _ in range(cantidad):
            if sistema == "Windows":
                imprimir_windows(archivo)
            else:
                imprimir_linux(archivo)
    except Exception as e:
        raise Exception(f"Error al imprimir: {str(e)}")

