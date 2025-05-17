import sys
import os
import tkinter as tk
from tkinter import messagebox, ttk
from database import obtener_datos_lote
from etiqueta_manager import procesar_etiqueta
from printer_manager import imprimir_etiquetas

# Variables globales para los widgets
lote_input = None
cantidad_input = None
ventana_carga = None
label_estado = None
root = None

def crear_ventana_carga():
    """Crea una ventana de carga"""
    global ventana_carga, label_estado
    ventana_carga = tk.Toplevel()
    ventana_carga.title("Procesando")
    ventana_carga.geometry("300x150")
    
    # Centrar la ventana
    ventana_carga.transient()  # Hace que la ventana sea modal
    ventana_carga.grab_set()   # Bloquea la ventana principal
    
    # Frame principal
    frame = ttk.Frame(ventana_carga, padding="20")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Label de estado
    label_estado = ttk.Label(frame, text="Procesando...", font=("Arial", 12))
    label_estado.grid(row=0, column=0, pady=20)
    
    # Barra de progreso
    progress = ttk.Progressbar(frame, mode='indeterminate')
    progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
    progress.start()
    
    # Configurar grid
    ventana_carga.columnconfigure(0, weight=1)
    ventana_carga.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    
    return ventana_carga

def actualizar_estado(mensaje, es_error=False):
    """Actualiza el mensaje de estado en la ventana de carga"""
    if label_estado:
        label_estado.config(text=mensaje)
        if es_error:
            label_estado.config(foreground="red")
        else:
            label_estado.config(foreground="green")

def cerrar_ventana_carga():
    """Cierra la ventana de carga"""
    global ventana_carga
    if ventana_carga:
        ventana_carga.destroy()
        ventana_carga = None

def crear_interfaz():
    """Crea y configura la interfaz gráfica"""
    global root
    root = tk.Tk()
    root.title("Sistema de Impresión de Etiquetas")
    root.geometry("400x250")
    
    # Configurar estilo
    style = ttk.Style()
    style.configure("TLabel", padding=5)
    style.configure("TButton", padding=5)
    style.configure("TEntry", padding=5)
    
    # Frame principal
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Campos de entrada
    ttk.Label(main_frame, text="Número de Lote:").grid(row=0, column=0, sticky=tk.W, pady=5)
    global lote_input
    lote_input = ttk.Entry(main_frame, width=30)
    lote_input.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
    
    ttk.Label(main_frame, text="Cantidad a Imprimir:").grid(row=2, column=0, sticky=tk.W, pady=5)
    global cantidad_input
    cantidad_input = ttk.Entry(main_frame, width=30)
    cantidad_input.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
    
    # Botón de impresión
    print_button = ttk.Button(main_frame, text="Imprimir Etiquetas", command=procesar_impresion)
    print_button.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=20)
    
    # Configurar grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    
    return root

def procesar_impresion():
    """Procesa la impresión de etiquetas"""
    global root
    try:
        nro_lote = lote_input.get()
        cantidad = cantidad_input.get()
        
        if not nro_lote or not cantidad:
            messagebox.showwarning("Error", "Por favor ingrese valores válidos")
            return
            
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Error", "La cantidad debe ser un número entero positivo")
            return
        
        # Crear ventana de carga
        crear_ventana_carga()

        
        # Obtener datos de la base de datos
        actualizar_estado("Consultando base de datos...")
        print("casi")
        datos = obtener_datos_lote(nro_lote)
        if not datos:
            actualizar_estado("Error: No se encontró el lote en la base de datos", True)
            root.after(2000, cerrar_ventana_carga)  # Cerrar después de 2 segundos
            return
        print(datos)
        
        cod_articulo, fecha_vencimiento = datos
        
        # Procesar etiqueta
        actualizar_estado("Procesando etiqueta...")
        archivo_etiqueta = procesar_etiqueta(
            cod_articulo, 
            nro_lote, 
            fecha_vencimiento
        )
        
        # Imprimir etiquetas
        actualizar_estado("Imprimiendo etiquetas...")
        imprimir_etiquetas(archivo_etiqueta, cantidad)
        
        # Mostrar éxito
        actualizar_estado("¡Éxito! Etiquetas impresas correctamente")
        root.after(3000,cerrar_ventana_carga)  # Cerrar después de 2 segundos
        
    except Exception as e:
        error_msg = str(e)
        messagebox.showerror("Error", error_msg)
        cerrar_ventana_carga()  # Cerrar la ventana de carga después de mostrar el error

def main():
    root = crear_interfaz()
    root.mainloop()

if __name__ == "__main__":
    main() 