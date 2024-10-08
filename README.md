# YouTube Downloader and Audio Compressor

- En la carpta dist existe un ejecutable funcional
- Version 1.0.0

## Descripción

Este es un programa desarrollado en Python utilizando PyQt5, que permite descargar videos o listas de reproducción de YouTube, extraer el audio en formato MP3 y comprimir archivos de audio. Ofrece una interfaz gráfica simple y atractiva para gestionar descargas y conversiones, además de incluir una opción para comprimir audios previamente descargados o seleccionados.

## Características

- **Descarga de videos de YouTube**: Puedes descargar videos de YouTube en su mejor calidad disponible.
- **Descarga de audio de YouTube**: Descarga solo el audio de videos o listas de reproducción en formato MP3, con calidad seleccionable (Baja, Media o Alta).
- **Compresión de audio**: Comprime archivos de audio MP3, WAV, WEBM, o M4A a un formato MP3 más ligero.
- **Compatibilidad con listas de reproducción**: Puedes descargar el audio de listas completas de reproducción de YouTube.
- **Interfaz gráfica atractiva**: La aplicación cuenta con un diseño estilizado, sencillo y funcional, creado con PyQt5.

## Requisitos del Sistema

- **Python 3.7 o superior**
- **PyQt5**
- **yt-dlp** (para descargar videos y audios de YouTube)
- **ffmpeg** (para la conversión de formatos de audio)

## Instalación

1. Clona el repositorio o descarga el código fuente:

   git clone <https://github.com/Dylantv999/DescargarVideos-Music.git>

2. Instala las dependencias necesarias utilizando pip:

    - pip install PyQt5 

    - pip install yt-dlp

    - pip install ffmpeg-python

    pip install mutagen

3. Asegúrate de tener ffmpeg instalado en tu sistema. Puedes descargarlo desde FFmpeg.org.

  ## Uso

  Ejecuta el archivo principal:
    - python dmp3.py

## Detalles Técnicos
# Estructura del Código
- DownloadThread: Este hilo maneja las descargas de videos y audios mostrando el progreso y manejando listas de reproducción.
- AudioCompressorThread: Hilo dedicado a la compresión de audios a formato MP3, reduciendo el tamaño de los archivos.
- YouTubeDownloader: La clase principal que gestiona la interfaz gráfica y las interacciones del usuario.