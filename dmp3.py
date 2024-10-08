import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QProgressBar, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp
import ffmpeg

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    stopped = pyqtSignal()

    def __init__(self, url, output_path, quality, is_video=True, is_playlist=False, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.is_video = is_video
        self.is_playlist = is_playlist
        self._is_canceled = False

    def run(self):
        if not self.is_video:
            quality_map = {'Baja': '64', 'Media': '128', 'Alta': '192'}
            selected_quality = quality_map.get(self.quality, '192')

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.output_path}/%(playlist_title)s/%(title)s.%(ext)s' if self.is_playlist else f'{self.output_path}/%(title)s.%(ext)s',
                'progress_hooks': [self.yt_progress_hook],
                'noplaylist': not self.is_playlist,
                'ignoreerrors': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': selected_quality,
                }],
                'postprocessor_args': ['-ar', '44100'],
                'prefer_ffmpeg': True
            }
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f'{self.output_path}/%(playlist_title)s/%(title)s.%(ext)s' if self.is_playlist else f'{self.output_path}/%(title)s.%(ext)s',
                'progress_hooks': [self.yt_progress_hook],
                'noplaylist': not self.is_playlist,
                'ignoreerrors': True
            }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            if not self._is_canceled:
                self.finished.emit(str(e))

    def yt_progress_hook(self, d):
        if self._is_canceled:
            raise yt_dlp.utils.DownloadError("Canceled")
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = int(downloaded_bytes / total_bytes * 100)
                self.progress.emit(progress)
        elif d['status'] == 'finished':
            self.finished.emit(d['filename'])

    def cancel(self):
        self._is_canceled = True
        self.stopped.emit()

class AudioCompressorThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_folder, output_folder, parent=None):
        super().__init__(parent)
        self.input_folder = input_folder
        self.output_folder = output_folder
        self._is_canceled = False

    def run(self):
        # Listar todos los archivos en la carpeta de entrada
        for filename in os.listdir(self.input_folder):
            if filename.endswith(('.mp3', '.wav', '.webm', '.m4a')):  # Puedes agregar otros formatos si es necesario
                input_file = os.path.join(self.input_folder, filename)
                output_file = os.path.join(self.output_folder, f"{os.path.splitext(filename)[0]}.mp3")  # Cambiar a .mp3

                # Comprimir a MP3
                try:
                    ffmpeg.input(input_file).output(output_file, audio_bitrate='96k').run()  # Usar MP3 como formato
                    self.progress.emit(100)  # Emitir progreso final
                except Exception as e:
                    print(f'Error al comprimir {filename}: {str(e)}')
        
        self.finished.emit("Compresión de audio finalizada.")

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 700, 400)

        layout = QVBoxLayout()

        # URL del video
        url_layout = QHBoxLayout()
        self.url_label = QLabel('URL del video o playlist de YouTube:')
        self.url_entry = QLineEdit()
        url_layout.addWidget(self.url_label)
        url_layout.addWidget(self.url_entry)
        layout.addLayout(url_layout)

        # Carpeta de destino
        path_layout = QHBoxLayout()
        self.path_label = QLabel('Carpeta de destino:')
        self.path_entry = QLineEdit()
        self.path_button = QPushButton('Buscar...')
        self.path_button.clicked.connect(self.browse_folder)
        path_layout.addWidget(self.path_label)
        path_layout.addWidget(self.path_entry)
        path_layout.addWidget(self.path_button)
        layout.addLayout(path_layout)

        # Establece la carpeta de descargas por defecto
        downloads_folder = os.path.expanduser('~/Downloads')
        self.path_entry.setText(downloads_folder)

        # Menú desplegable para seleccionar la calidad del audio
        self.quality_label = QLabel('Calidad de audio:')
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(['Baja', 'Media', 'Alta'])
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_combo)

        # Botones de descarga
        button_layout = QHBoxLayout()
        self.download_video_button = QPushButton('Descargar Video')
        self.download_video_button.clicked.connect(lambda: self.start_download(is_video=True, is_playlist=False))
        self.download_audio_button = QPushButton('Descargar Audio')
        self.download_audio_button.clicked.connect(lambda: self.start_download(is_video=False, is_playlist=False))
        self.download_playlist_button = QPushButton('Descargar Playlist (Audio)')
        self.download_playlist_button.clicked.connect(lambda: self.start_download(is_video=False, is_playlist=True))
        self.compress_audio_button = QPushButton('Comprimir Audio')
        self.compress_audio_button.clicked.connect(self.compress_audio)
        self.cancel_button = QPushButton('Cancelar')
        self.cancel_button.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.download_video_button)
        button_layout.addWidget(self.download_audio_button)
        button_layout.addWidget(self.download_playlist_button)
        button_layout.addWidget(self.compress_audio_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.download_thread = None
        self.compress_thread = None

    def browse_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de destino')
        if folder_selected:
            self.path_entry.setText(folder_selected)

    def start_download(self, is_video, is_playlist):
        url = self.url_entry.text()
        output_path = self.path_entry.text()
        selected_quality = self.quality_combo.currentText()

        if not url or not output_path:
            print('Error: Por favor, introduce la URL del video o playlist de YouTube y selecciona una carpeta de destino.')
            return

        # Crear la carpeta de destino si no existe
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        self.progress_bar.setValue(0)
        self.download_thread = DownloadThread(url, output_path, selected_quality, is_video, is_playlist)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.stopped.connect(self.download_canceled)
        self.download_thread.start()

    def compress_audio(self):
        input_folder = self.path_entry.text()
        output_folder = os.path.join(input_folder, "Comprimidos")  # Carpeta de salida para archivos comprimidos

        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)

        self.progress_bar.setValue(0)
        self.compress_thread = AudioCompressorThread(input_folder, output_folder)
        self.compress_thread.progress.connect(self.update_progress)
        self.compress_thread.finished.connect(self.compression_finished)
        self.compress_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self, filename):
        print('Descarga finalizada: El archivo se ha descargado correctamente.')

    def compression_finished(self, message):
        print(message)
        self.progress_bar.setValue(100)

    def download_canceled(self):
        self.download_thread = None
        self.progress_bar.setValue(0)
        print('Descarga cancelada.')

    def cancel_download(self):
        if self.download_thread:
            self.download_thread.cancel()

if __name__ == '__main__':
    style_sheet = """
        QWidget {
            background-color: #2E3440;
            color: #D8DEE9;
            font-size: 14px;
        }
        QLineEdit {
            background-color: #3B4252;
            color: #D8DEE9;
            padding: 5px;
            border: 1px solid #4C566A;
        }
        QPushButton {
            background-color: #4C566A;
            color: #D8DEE9;
            border: none;
            padding: 8px;
            margin: 5px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #5E81AC;
        }
        QProgressBar {
            background-color: #3B4252;
            color: #D8DEE9;
            border: 1px solid #4C566A;
        }
        """
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec_())
