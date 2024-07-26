import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
from datetime import datetime

# Variable global para almacenar el nombre del archivo descargado
downloaded_file = None

def download_video():
    global downloaded_file
    youtube_url = url_entry.get()
    output_path = output_path_entry.get()
    
    if not youtube_url or not output_path:
        messagebox.showerror("Error", "Por favor, introduce la URL del video de YouTube y selecciona una carpeta de destino.")
        return
    
    # Configuración de yt-dlp para descargar el mejor formato disponible sin combinación
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [on_progress],
        'noplaylist': True  # No descargar listas de reproducción
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Cambiar la fecha de modificación del archivo descargado a la fecha actual
        if downloaded_file:
            file_path = os.path.join(output_path, downloaded_file)
            current_time = datetime.now().timestamp()
            os.utime(file_path, (current_time, current_time))
        
        messagebox.showinfo("Éxito", "Video descargado con éxito.")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {e}")

def on_progress(d):
    global downloaded_file
    if d['status'] == 'finished':
        downloaded_file = d['filename']

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, folder_selected)

# Obtener la carpeta de descargas por defecto
default_download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

# Crear la ventana principal
root = tk.Tk()
root.title("YouTube Video Downloader")

# Crear y colocar los widgets
tk.Label(root, text="URL del video de YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Carpeta de destino:").grid(row=1, column=0, padx=10, pady=10)
output_path_entry = tk.Entry(root, width=50)
output_path_entry.insert(0, default_download_path)
output_path_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Buscar...", command=browse_folder)
browse_button.grid(row=1, column=2, padx=10, pady=10)

download_button = tk.Button(root, text="Descargar Video", command=download_video)
download_button.grid(row=2, column=0, columnspan=3, pady=20)

# Ejecutar el bucle principal de la aplicación
root.mainloop()