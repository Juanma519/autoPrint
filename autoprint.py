import psycopg2
from docx import Document
import os
import tkinter as tk
from tkinter import messagebox

def obtener_datos_producto(nro_lote, conexion):
    cursor = conexion.cursor()
    query = """
        SELECT cod_articulo,fec_venc FROM cpt_lote
        WHERE nro_lote='2304575'
    """
    cursor.execute(query, (nro_lote,))
    resultado = cursor.fetchone()
    cursor.close()
    if resultado:
        return {
            
            'cod_articulo': resultado[0],
            'fecha_vencimiento': resultado[1]
        }
    return None

def buscar_plantilla(producto, directorio):
    for archivo in os.listdir(directorio):
        if producto.lower().replace(" ", "_") in archivo.lower() and archivo.endswith('.docx'):
            return os.path.join(directorio, archivo)
    return None

def reemplazar_datos_en_word(path_word, nro_lote, fecha_vencimiento, salida):
    doc = Document(path_word)
    for p in doc.paragraphs:
        p.text = p.text.replace("NRO_LOTE", nro_lote)
        p.text = p.text.replace("FECHA_VTO", fecha_vencimiento)
    doc.save(salida)

def generar_etiquetas_gui():
    nro_lote = entry_lote.get()
    try:
        cantidad = int(entry_cantidad.get())
    except ValueError:
        messagebox.showerror("Error", "La cantidad debe ser un número.")
        return

    try:
        conexion = psycopg2.connect(
            host="localhost",
            database="mi_base",
            user="usuario",
            password="clave"
        )
    except Exception as e:
        messagebox.showerror("Error de conexión", str(e))
        return

    datos = obtener_datos_producto(nro_lote, conexion)
    if not datos:
        messagebox.showerror("Error", "Lote no encontrado.")
        return

    plantilla = buscar_plantilla(datos['producto'], "C:/plantillas_etiquetas")
    if not plantilla:
        messagebox.showerror("Error", "No se encontró la plantilla.")
        return

    for i in range(cantidad):
        salida = f"etiqueta_{nro_lote}_{i+1}.docx"
        reemplazar_datos_en_word(plantilla, nro_lote, datos['fecha_vencimiento'], salida)

    conexion.close()
    messagebox.showinfo("Éxito", f"Se generaron {cantidad} etiquetas.")


root = tk.Tk()
root.title("Generador de Etiquetas")

tk.Label(root, text="Número de Lote:").grid(row=0, column=0, pady=5, sticky="e")
entry_lote = tk.Entry(root)
entry_lote.grid(row=0, column=1, padx=5)

tk.Label(root, text="Cantidad:").grid(row=1, column=0, pady=5, sticky="e")
entry_cantidad = tk.Entry(root)
entry_cantidad.grid(row=1, column=1, padx=5)

tk.Button(root, text="Generar Etiquetas", command=generar_etiquetas_gui).grid(row=2, columnspan=2, pady=10)

root.mainloop()
