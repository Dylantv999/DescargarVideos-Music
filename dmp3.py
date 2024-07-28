import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import os
from datetime import datetime
import threading

# Variables globales
downloaded_file = None
download_complete_event = threading.Event()
current_progress = 0

def update_progress_bar(value):
    progress_bar['value'] = value
    root.update_idletasks()

def reset_progress_bar():
    progress_bar['value'] = 0
    root.update_idletasks()

def download_video():
    global downloaded_file

    youtube_url = url_entry.get()
    output_path = output_path_entry.get()

    if not youtube_url or not output_path:
        messagebox.showerror("Error", "Por favor, introduce la URL del video de YouTube y selecciona una carpeta de destino.")
        return

    def download_task():
        global downloaded_file
        
        ydl_opts = {
            'format': 'best',  # Descargar el mejor formato de video
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [on_progress],
            'noplaylist': True  # No descargar listas de reproducción
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Esperar a que se complete la descarga
            download_complete_event.wait()

            if downloaded_file:
                # Cambiar la fecha de modificación del archivo descargado a la fecha actual
                file_path = os.path.join(output_path, downloaded_file)
                current_time = datetime.now().timestamp()
                os.utime(file_path, (current_time, current_time))
                
            messagebox.showinfo("Éxito", "Video descargado con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")

        reset_progress_bar()

    # Ejecutar la tarea de descarga en un hilo separado
    threading.Thread(target=download_task).start()

def download_audio():
    global downloaded_file, current_progress

    youtube_url = url_entry.get()
    output_path = output_path_entry.get()

    if not youtube_url or not output_path:
        messagebox.showerror("Error", "Por favor, introduce la URL del video de YouTube y selecciona una carpeta de destino.")
        return

    def download_task():
        global downloaded_file
        
        ydl_opts = {
            'format': 'bestaudio/best',  # Descargar el mejor formato de audio
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [on_progress],
            'noplaylist': True  # No descargar listas de reproducción
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
            
            # Esperar a que se complete la descarga
            download_complete_event.wait()

            if downloaded_file:
                # Cambiar la fecha de modificación del archivo descargado a la fecha actual
                file_path = os.path.join(output_path, downloaded_file)
                current_time = datetime.now().timestamp()
                os.utime(file_path, (current_time, current_time))

                # Ocultar el archivo descargado
                os.system(f'attrib +h "{file_path}"')

                # Convertir a mp3 usando ffmpeg
                mp3_file_path = file_path.rsplit('.', 1)[0] + '.mp3'
                os.system(f'ffmpeg -i "{file_path}" -vn -ar 44100 -ac 2 -b:a 192k "{mp3_file_path}"')

                # Eliminar el archivo webm original
                os.remove(file_path)
                
                # Hacer visible el archivo mp3 final
                os.system(f'attrib -h "{mp3_file_path}"')
                
            messagebox.showinfo("Éxito", "Audio descargado y convertido a MP3 con éxito.")
        except Exception as e:
            messagebox.showerror("Error", f"Se produjo un error: {e}")

        reset_progress_bar()

    # Ejecutar la tarea de descarga en un hilo separado
    threading.Thread(target=download_task).start()

def on_progress(d):
    global downloaded_file, current_progress
    if d['status'] == 'downloading':
        current_progress = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
        update_progress_bar(current_progress)
    elif d['status'] == 'finished':
        downloaded_file = d['filename']
        download_complete_event.set()  # Indicar que la descarga ha terminado
        update_progress_bar(100)

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        output_path_entry.delete(0, tk.END)
        output_path_entry.insert(0, folder_selected)

# Obtener la carpeta de descargas por defecto
default_download_path = os.path.join(os.path.expanduser('~'), 'Downloads')

# Crear la ventana principal
root = tk.Tk()
root.title("YouTube Downloader")

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

# Botones para descargar video y audio
download_video_button = tk.Button(root, text="Descargar Video", command=download_video)
download_video_button.grid(row=2, column=0, columnspan=3, pady=20)

download_audio_button = tk.Button(root, text="Descargar Audio", command=download_audio)
download_audio_button.grid(row=3, column=0, columnspan=3, pady=20)

# Barra de progreso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, pady=20)

# Ejecutar el bucle principal de la aplicación
root.mainloop()
