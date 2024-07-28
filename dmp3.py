import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp
import os
from datetime import datetime

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, output_path, is_video=True, parent=None):
        super().__init__(parent)
        self.url = url
        self.output_path = output_path
        self.is_video = is_video

    def run(self):
        ydl_opts = {
            'format': 'best' if self.is_video else 'bestaudio/best',
            'outtmpl': f'{self.output_path}/%(title)s.%(ext)s',
            'progress_hooks': [self.yt_progress_hook],
            'noplaylist': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            self.finished.emit(str(e))

    def yt_progress_hook(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes', 0)
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes > 0:
                progress = int(downloaded_bytes / total_bytes * 100)
                self.progress.emit(progress)
        elif d['status'] == 'finished':
            self.finished.emit(d['filename'])

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # URL del video
        url_layout = QHBoxLayout()
        self.url_label = QLabel('URL del video de YouTube:')
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

        # Botones de descarga
        button_layout = QHBoxLayout()
        self.download_video_button = QPushButton('Descargar Video')
        self.download_video_button.clicked.connect(self.download_video)
        self.download_audio_button = QPushButton('Descargar Audio')
        self.download_audio_button.clicked.connect(self.download_audio)
        button_layout.addWidget(self.download_video_button)
        button_layout.addWidget(self.download_audio_button)
        layout.addLayout(button_layout)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

    def browse_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta de destino')
        if folder_selected:
            self.path_entry.setText(folder_selected)

    def download_video(self):
        self.start_download(is_video=True)

    def download_audio(self):
        self.start_download(is_video=False)

    def start_download(self, is_video):
        url = self.url_entry.text()
        output_path = self.path_entry.text()

        if not url or not output_path:
            QMessageBox.critical(self, 'Error', 'Por favor, introduce la URL del video de YouTube y selecciona una carpeta de destino.')
            return

        self.progress_bar.setValue(0)
        self.download_thread = DownloadThread(url, output_path, is_video)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.download_finished)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def download_finished(self, filename):
        if filename.endswith('.webm') and not self.download_thread.is_video:
            self.convert_to_mp3(filename)
        else:
            QMessageBox.information(self, 'Éxito', 'Descarga completada con éxito.')

    def convert_to_mp3(self, webm_file):
        mp3_file = webm_file.rsplit('.', 1)[0] + '.mp3'
        os.system(f'ffmpeg -i "{webm_file}" -vn -ar 44100 -ac 2 -b:a 192k "{mp3_file}"')
        os.remove(webm_file)
        QMessageBox.information(self, 'Éxito', 'Audio descargado y convertido a mp3 con éxito.')

if __name__ == '__main__':
    style_sheet = """
        QWidget {
            background-color: #2E3440;
            color: #D8DEE9;
            font-size: 14px;
        }
        QLineEdit {
            background-color: #4C566A;
            border: 1px solid #D8DEE9;
            border-radius: 5px;
            padding: 5px;
            color: #D8DEE9;
        }
        QPushButton {
            background-color: #5E81AC;
            border: none;
            border-radius: 5px;
            padding: 10px;
            color: #ECEFF4;
        }
        QPushButton:hover {
            background-color: #81A1C1;
        }
        QProgressBar {
            border: 1px solid #D8DEE9;
            border-radius: 5px;
            text-align: center;
            background-color: #4C566A;
        }
        QProgressBar::chunk {
            background-color: #88C0D0;
            border-radius: 5px;
        }
        QLabel {
            font-weight: bold;
        }
        QFileDialog {
            background-color: #2E3440;
            color: #D8DEE9;
        }
    """

    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)  # Aplica la hoja de estilo
    downloader = YouTubeDownloader()
    downloader.show()
    sys.exit(app.exec_())
