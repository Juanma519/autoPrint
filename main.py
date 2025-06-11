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
impresiones_cargadas = []  # Lista de tuplas (cod_articulo, nro_lote, cantidad, fecha_vencimiento, tipo_etiqueta)

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
    
    # Ordenar impresiones por tipo_etiqueta
    impresiones_ordenadas = sorted(impresiones_cargadas, key=lambda x: x[4])  # x[4] es tipo_etiqueta
    
    # Crear una lista para cada tipo de etiqueta
    row = 0
    tipo_etiqueta_actual = None
    frame_actual = None
    
    for impresion in impresiones_ordenadas:
        cod_articulo, nro_lote, cantidad, fecha_vencimiento, tipo_etiqueta = impresion
        
        # Si es un nuevo tipo de etiqueta, crear nuevo frame
        if tipo_etiqueta != tipo_etiqueta_actual:
            tipo_etiqueta_actual = tipo_etiqueta
            frame_actual = ttk.LabelFrame(scrollable_frame, text=f"Tipo de Etiqueta: {tipo_etiqueta}", padding="10")
            frame_actual.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10, padx=5)
            row += 1
        
        # Crear frame para cada impresión
        frame_impresion = ttk.Frame(frame_actual)
        frame_impresion.grid(row=len(frame_actual.winfo_children()), column=0, sticky=(tk.W, tk.E), pady=2)
        
        # Información de la impresión
        info_text = f"Artículo: {cod_articulo} | Lote: {nro_lote} | Cantidad: {cantidad} | Vencimiento: {fecha_vencimiento}"
        ttk.Label(frame_impresion, text=info_text).grid(row=0, column=0, sticky=tk.W)
        
        # Botón para imprimir
        btn_imprimir = ttk.Button(
            frame_impresion,
            text="Imprimir",
            command=lambda ca=cod_articulo, nl=nro_lote, c=cantidad, fv=fecha_vencimiento, te=tipo_etiqueta: 
                confirmar_impresion_individual(ca, nl, c, fv, te)
        )
        btn_imprimir.grid(row=0, column=1, padx=5)
    
    # Configurar grid
    ventana_impresiones.columnconfigure(0, weight=1)
    ventana_impresiones.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(0, weight=1)
    
    return ventana_impresiones

def confirmar_impresion_individual(cod_articulo, nro_lote, cantidad, fecha_vencimiento,tipo_etiqueta):
    """Muestra diálogo de confirmación antes de imprimir una etiqueta individual"""
    respuesta = messagebox.askyesno(
        "Confirmar Impresión",
        f"¿Desea imprimir la etiqueta del artículo {cod_articulo}, lote {nro_lote}?",
        f"Revise si el tamaño de la etiqueta es el correcto: {tipo_etiqueta}"
    )
    if respuesta:
        procesar_impresion_individual(cod_articulo, nro_lote, cantidad, fecha_vencimiento,tipo_etiqueta)

def procesar_impresion_individual(cod_articulo, nro_lote, cantidad, fecha_vencimiento,tipo_etiqueta:str):
    """Procesa una impresión individual"""
    global root
    try:
        crear_ventana_carga()
        actualizar_estado("Procesando impresión...")
        
        # Procesar etiqueta usando el nro_lote proporcionado
        archivo_etiqueta = procesar_etiqueta(
            cod_articulo, 
            nro_lote, 
            fecha_vencimiento
        )
        if "Grande" or "grande" in tipo_etiqueta:
            # Imprimir etiquetas
            imprimir_etiquetas(archivo_etiqueta, cantidad, "Grande")
        elif "Chico" or "chico" in tipo_etiqueta:
            # Imprimir etiquetas
            imprimir_etiquetas(archivo_etiqueta, cantidad, "Chico")
        else:
            raise Exception(f"Tipo de etiqueta no válido: {tipo_etiqueta}")
        
        # Eliminar la impresión de la lista
        impresiones_cargadas[:] = [imp for imp in impresiones_cargadas 
                                 if not (imp[0] == cod_articulo and imp[1] == nro_lote)]
        
        # Actualizar interfaz
        actualizar_estado("¡Éxito! La etiqueta fue impresa")
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
        
        cod_articulo, fecha_vencimiento, tipo_etiqueta = datos
        tipo_etiqueta = tipo_etiqueta.upper()
      
        
        # Agregar a la lista de impresiones cargadas
        impresiones_cargadas.append((cod_articulo, nro_lote, cantidad, fecha_vencimiento, tipo_etiqueta))
        
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