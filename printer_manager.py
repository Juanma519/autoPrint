import os
import subprocess
import platform

def imprimir_windows(archivo):
    """Imprime en Windows usando el comando start"""
    try:
        # Usar el comando start de Windows para imprimir
        subprocess.run(['start', '/min', '', archivo], shell=True)
    except Exception as e:
        raise Exception(f"Error al imprimir en Windows: {str(e)}")

def imprimir_linux(archivo):
    """Imprime en Linux usando lp"""
    try:
        subprocess.run(['lp', archivo])
    except Exception as e:
        raise Exception(f"Error al imprimir en Linux: {str(e)}")

def imprimir_etiquetas(archivo, cantidad):
    """Imprime el archivo la cantidad de veces especificada"""
    try:
        sistema = platform.system()
        for _ in range(cantidad):
            if sistema == "Windows":
                imprimir_windows(archivo)
            else:
                imprimir_linux(archivo)
    except Exception as e:
        raise Exception(f"Error al imprimir: {str(e)}")

class PrinterManager:
    def __init__(self):
        self.sistema = platform.system()

    def imprimir_etiquetas(self, archivo, cantidad):
        """
        Imprime el archivo la cantidad de veces especificada
        """
        try:
            for _ in range(cantidad):
                if self.sistema == "Windows":
                    self._imprimir_windows(archivo)
                else:
                    self._imprimir_linux(archivo)
        except Exception as e:
            raise Exception(f"Error al imprimir: {str(e)}")

    def _imprimir_windows(self, archivo):
        """
        Imprime en Windows usando el comando start
        """
        try:
            # Usar el comando start de Windows para imprimir
            subprocess.run(['start', '/min', '', archivo], shell=True)
        except Exception as e:
            raise Exception(f"Error al imprimir en Windows: {str(e)}")

    def _imprimir_linux(self, archivo):
        """
        Imprime en Linux usando lp
        """
        try:
            subprocess.run(['lp', archivo])
        except Exception as e:
            raise Exception(f"Error al imprimir en Linux: {str(e)}") 