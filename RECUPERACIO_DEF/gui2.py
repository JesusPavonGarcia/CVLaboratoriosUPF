import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import zipfile
import os
import cv2
import vlc
import subprocess
import time
import re
from threading import Thread


class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Encoding GUI")

        self.video_path = tk.StringVar()
        self.bitrate = tk.StringVar()
        self.chroma_sub = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Título + descripción
        title_label = tk.Label(self.root, text="JESÚS PAVÓN GARCÍA - VIDEO ENCODING LADDER SIMULATOR",
                               font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Selector de video
        ttk.Label(self.root, text="Seleccione archivo de video:").grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.video_path, width=50).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(self.root, text="Seleccionar", command=self.select_video).grid(row=1, column=2, padx=10, pady=10)

        # Entrada bitrate
        ttk.Label(self.root, text="Bitrate (bps):").grid(row=2, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.bitrate, width=20).grid(row=2, column=1, padx=10, pady=10)

        # Entrada Chroma Subsampling
        ttk.Label(self.root, text="Chroma Subsampling ['yuv422p','yuv420p','yuv444p']:").grid(row=3, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.chroma_sub, width=20).grid(row=3, column=1, padx=10, pady=10)

        # Botón Iniciar proceso
        tk.Button(self.root, text="Iniciar Proceso", command=self.start_process).grid(row=4, column=2, padx=10, pady=10)

        # Botón de salida
        tk.Button(self.root, text="Salir", command=self.on_exit).grid(row=5, column=2, padx=10, pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.video_path.set(file_path)

    def process_video(self, file_path):
        # Primero, aseguramos que Flask esté en ejecución
        start_flask_server()

        #Get el bitrate y chroma_sub del usuario
        bitrate = int(self.bitrate.get())
        chroma_sub = self.chroma_sub.get()

        url = 'http://127.0.0.1:5002/process_video'

        files = {'video': open(file_path, 'rb')}
        try:
            response = requests.post(url, files=files, data={'bitrate': bitrate, 'chroma_sub': chroma_sub})

            if response.status_code == 200:
                zip_path = os.path.join('/tmp', 'processed_video.zip')
                with open(zip_path, 'wb') as f:
                    f.write(response.content)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('/tmp')

                video_path = [file for file in zip_ref.namelist() if file.endswith('.mp4')][0]
                video_full_path = os.path.join('/tmp', video_path)

                #Init Metadata Window , subdividir en frames
                metadata_window = tk.Toplevel(root)
                metadata_window.title("Metadata Videos")
                frame_ori = tk.Frame(metadata_window, bd=2, relief=tk.SUNKEN)
                frame_proc = tk.Frame(metadata_window, bd=2, relief=tk.SUNKEN)

                frame_ori.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)
                frame_proc.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)

                #Leemos archivo y display metadatos video original
                metadata_txt_path_ori = [file for file in zip_ref.namelist() if file.endswith('_original.txt')][0]
                metadata_full_path = os.path.join('/tmp', metadata_txt_path_ori)
                codec, colorsubsampling, resolution, bitrate = self.read_metadata(metadata_full_path)
                display_metadata(codec, colorsubsampling, resolution, bitrate, frame_ori, 'Original')

                # Leemos archivo y display metadatos video procesado
                metadata_txt_path = [file for file in zip_ref.namelist() if file.endswith('_temp.txt')][0]
                metadata_full_path = os.path.join('/tmp', metadata_txt_path)
                codec, colorsubsampling, resolution, bitrate = self.read_metadata(metadata_full_path)
                display_metadata(codec, colorsubsampling, resolution, bitrate, frame_proc, 'Processed')

                #Play processed y original video
                #play_video(video_full_path, 'processed')
                self.play_videos(file_path, video_full_path)
            else:
                messagebox.showerror("Error", "Error in processing the video")
        except Exception as e:
            print(f"An error occurred: {e}")

    def read_metadata(self, metadata_txt_path):
        codec = None
        resolution = None
        bitrate = None
        colorsubsampling = None

        with open(metadata_txt_path, 'r') as f:
            lines = f.readlines()
            # Linia pattern que queremos identifcar
            # r'Stream #\d+:\d+\(\w*\): Video: (\w+) \(.*\), (\w+), (\d+x\d+) \[.*\], (\d+) kb/s,.*')
            stream_pattern = re.compile(
                r'Stream #\d+:\d+\(\w*\): Video: (\w+) \(.*\), (\w+), (\d+x\d+) \[.*\], (\d+) ?kb/s,.*')

            for line in lines:
                # Buscar la línea que contiene la información del stream de video
                stream_match = stream_pattern.search(line)
                if stream_match:
                    print("MATCH: datos del archivo coinciden con los datos solicitados.")
                    codec = stream_match.group(1)
                    colorsubsampling = stream_match.group(2)
                    resolution = stream_match.group(3)
                    bitrate = stream_match.group(4)
                    return codec, colorsubsampling, resolution, bitrate
                else:
                    print(".")

    def play_videos(self, video_path1, video_path2):
        cap1 = cv2.VideoCapture(video_path1)
        cap2 = cv2.VideoCapture(video_path2)

        if not cap1.isOpened() or not cap2.isOpened():
            messagebox.showerror("Error", "No se puede abrir uno o ambos archivos de video")
            return

        width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
        height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
        height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

        cv2.namedWindow("Video Original", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Original", width1, height1)
        cv2.namedWindow("Video Procesado", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Video Procesado", width1, height1)

        while cap1.isOpened() and cap2.isOpened():
            ret1, frame1 = cap1.read()
            ret2, frame2 = cap2.read()
            if ret1 and ret2:
                cv2.imshow("Video Original", frame1)
                cv2.imshow("Video Procesado", frame2)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            else:
                break

        cap1.release()
        cap2.release()
        cv2.destroyAllWindows()

    def start_process(self):
        self.process_video(self.video_path.get())

    def on_exit(self):
        if messagebox.askokcancel("Salir", "¿Realmente quieres salir?"):
            root.destroy()


def display_metadata(codec, colorsubsampling, resolution, bitrate, frame, title):
    label = tk.Label(frame, text=f"Metadata Video {title}", font=("Helvetica", 14, "bold"))
    label.pack(pady=5)

    text = tk.Text(frame)
    text.insert(tk.END, f"Codec: {codec}\n")
    text.insert(tk.END, f"Resolution: {resolution}\n")
    text.insert(tk.END, f"Color Subsampling: {colorsubsampling}\n")
    text.insert(tk.END, f"Bitrate: {bitrate} kb/s\n")
    text.pack(expand=True, fill=tk.BOTH)


def play_video(video_path, title):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        messagebox.showerror("Error", f"No se puede abrir el archivo de video: {video_path}")
        return

    # Obtener la resolución del video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Crear una ventana para mostrar el video
    cv2.namedWindow("Reproducción de Video", cv2.WINDOW_NORMAL)
    cv2.resizeWindow(f"Reproducción de Video {title}", width, height)

    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Reproducción de Video", frame)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


def start_flask_server():
    subprocess.run(['python3', 'app.py'])


if __name__ == "__main__":
    flask_thread = Thread(target=start_flask_server)
    flask_thread.start()

    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()

    flask_thread.join()




