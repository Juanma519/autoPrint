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
ventana_impresiones = None

# Estructura para almacenar las impresiones cargadas
impresiones_cargadas = {}  # {cod_articulo: [(nro_lote, cantidad, fecha_vencimiento), ...]}

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

def crear_ventana_impresiones():
    """Crea la ventana que muestra las impresiones cargadas"""
    global ventana_impresiones
    ventana_impresiones = tk.Toplevel()
    ventana_impresiones.title("Impresiones Cargadas")
    ventana_impresiones.geometry("800x600")
    
    # Frame principal con scroll
    main_frame = ttk.Frame(ventana_impresiones, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # Canvas y scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Posicionar elementos
    canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    # Crear una tabla para cada tipo de artículo
    row = 0
    for cod_articulo, impresiones in impresiones_cargadas.items():
        # Frame para cada tipo de artículo
        frame_articulo = ttk.LabelFrame(scrollable_frame, text=f"Artículo: {cod_articulo}", padding="10")
        frame_articulo.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Crear tabla
        columns = ("Lote", "Cantidad", "Fecha Vencimiento")
        tree = ttk.Treeview(frame_articulo, columns=columns, show="headings", height=min(len(impresiones), 5))
        
        # Configurar columnas
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Agregar datos
        for impresion in impresiones:
            tree.insert("", "end", values=impresion)
        
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Botón para imprimir
        btn_imprimir = ttk.Button(
            frame_articulo, 
            text="Imprimir Todas",
            command=lambda ca=cod_articulo: confirmar_impresion(ca)
        )
        btn_imprimir.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        row += 1
    
    # Configurar grid
    ventana_impresiones.columnconfigure(0, weight=1)
    ventana_impresiones.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    return ventana_impresiones

def confirmar_impresion(cod_articulo):
    """Muestra diálogo de confirmación antes de imprimir"""
    respuesta = messagebox.askyesno(
        "Confirmar Impresión",
        f"¿Asegúrese que está la etiqueta del tipo {cod_articulo}?"
    )
    if respuesta:
        procesar_impresiones_articulo(cod_articulo)

def procesar_impresiones_articulo(cod_articulo):
    """Procesa todas las impresiones de un artículo específico"""
    global root
    try:
        crear_ventana_carga()
        actualizar_estado("Procesando impresiones...")
        
        for nro_lote, cantidad, fecha_vencimiento in impresiones_cargadas[cod_articulo]:
            # Procesar etiqueta
            archivo_etiqueta = procesar_etiqueta(
                cod_articulo, 
                nro_lote, 
                fecha_vencimiento
            )
            
            # Imprimir etiquetas
            imprimir_etiquetas(archivo_etiqueta, cantidad)
        
        # Limpiar impresiones procesadas
        impresiones_cargadas[cod_articulo] = []
        
        # Actualizar interfaz
        actualizar_estado("¡Éxito! Todas las etiquetas fueron impresas")
        root.after(2000, cerrar_ventana_carga)
        
        # Actualizar ventana de impresiones
        if ventana_impresiones:
            ventana_impresiones.destroy()
            crear_ventana_impresiones()
            
    except Exception as e:
        error_msg = str(e)
        messagebox.showerror("Error", error_msg)
        cerrar_ventana_carga()

def crear_interfaz():
    """Crea y configura la interfaz gráfica"""
    global root
    root = tk.Tk()
    root.title("Sistema de Impresión de Etiquetas")
    root.geometry("400x300")
    
    # Configurar estilo
    style = ttk.Style()
    style.configure("TLabel", padding=5)
    style.configure("TButton", padding=5)
    style.configure("TEntry", padding=5)
    
    # Frame principal
    main_frame = ttk.Frame(root, padding="20")
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
    
    # Botones
    btn_frame = ttk.Frame(main_frame)
    btn_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=20)
    
    btn_cargar = ttk.Button(btn_frame, text="Cargar Impresión", command=cargar_impresion)
    btn_cargar.grid(row=0, column=0, padx=5)
    
    btn_ver = ttk.Button(btn_frame, text="Ver Impresiones Cargadas", command=crear_ventana_impresiones)
    btn_ver.grid(row=0, column=1, padx=5)
    
    # Configurar grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)
    
    return root

def cargar_impresion():
    """Carga una impresión a la lista de impresiones pendientes"""
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
        datos = obtener_datos_lote(nro_lote)
        if not datos:
            actualizar_estado("Error: No se encontró el lote en la base de datos", True)
            root.after(2000, cerrar_ventana_carga)
            return
        
        cod_articulo, fecha_vencimiento = datos
        
        # Agregar a la lista de impresiones cargadas
        if cod_articulo not in impresiones_cargadas:
            impresiones_cargadas[cod_articulo] = []
        
        impresiones_cargadas[cod_articulo].append((nro_lote, cantidad, fecha_vencimiento))
        
        # Limpiar campos
        lote_input.delete(0, tk.END)
        cantidad_input.delete(0, tk.END)
        
        # Mostrar éxito
        actualizar_estado("¡Éxito! Impresión cargada correctamente")
        root.after(2000, cerrar_ventana_carga)
        
    except Exception as e:
        error_msg = str(e)
        messagebox.showerror("Error", error_msg)
        cerrar_ventana_carga()

def main():
    root = crear_interfaz()
    root.mainloop()

if __name__ == "__main__":
    main() 