import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
from threading import Thread
import requests
import lab_recu
import subprocess
import shutil
import threading
import os
import signal


class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Encoding GUI")

        # Variables
        self.video_path = tk.StringVar()
        self.out_video_path = tk.StringVar()
        self.bitrate_aleatorio = tk.IntVar()
        self.current_color_sub = tk.StringVar()

        self.original_bitrate = None
        self.chroma_subsampling = ['yuv444p', 'yuv422p', 'yuv420p']
        self.current_subsampling_index = 0
        # Layout
        self.create_widgets()
        self.cap = None
        self.process_thread = None
        self.process_lock = threading.Lock()  # Crear un bloqueo

    def create_widgets(self):
        # Title and description
        title_label = tk.Label(self.root, text="JESÚS PAVÓN GARCÍA - VIDEO ENCODING LADDER SIMULATOR", font=("Helvetica", 16))
        title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        description_label = tk.Label(self.root,
                                     text="El aplicativo se basa en simular situaciones con diferentes anchos de banda (bps)."
                                          "Este compara el bitrate original con ancho de banda disponible (ej. disponible en red doméstica ).\n "
                                          "     Si bitrate original > ancho de banda disponible -> reducirá la resolución (2,4,8,16).\n"
                                          "     Si bitrate original <= ancho de banda disponible ->mantendrá resolución original.\n"
                                          "Además es posible variar el Chroma subsampling (420,422,444).\n"
                                          "\nInstrucciones:"
                                          "\n1.Selecciona video "
                                          "\n2.Selecciona: Bitrate + Chroma subsampling "
                                          "\n3.Start", wraplength=800, font=("Helvetica", 7))
        description_label.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # Video selection
        ttk.Label(self.root, text="Seleccione archivo de video:").grid(row=2, column=0, padx=10, pady=10)
        ttk.Entry(self.root, textvariable=self.video_path, width=50).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(self.root, text="Seleccionar", command=self.select_video).grid(row=2, column=2, padx=10, pady=10)

        # Metadatos
        self.metadata_text = tk.Text(self.root, height=5, width=80)
        self.metadata_text.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Video Player
        self.video_label = ttk.Label(self.root)
        self.video_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Bitrate aleatorio
        ttk.Label(self.root, text="(Bandwith) Bitrate Aleatorio: [bps]").grid(row=5, column=0, padx=10, pady=10)
        ttk.Label(self.root, textvariable=self.bitrate_aleatorio).grid(row=5, column=1, padx=10, pady=10)

        # Select random bitrate
        ttk.Button(self.root, text="Selecciona Bitrate Aleatorio", command=self.select_random_bitrate).grid(row=6,column=2,padx=10, pady=5)

        # Change chroma subsampling button
        ttk.Button(self.root, text="Cambiar Chroma Subsampling", command=self.change_chroma_subsampling).grid(row=7,column=2,padx=10,pady=10)
        ttk.Label(self.root, text="Chroma Subsampling seleccionado:").grid(row=7, column=0, padx=10, pady=10)
        ttk.Label(self.root, textvariable=self.current_color_sub).grid(row=7, column=1, padx=10, pady=10)

        # Start encoding process
        ttk.Button(self.root, text="Iniciar proceso", command=self.start_process).grid(row=8, column=2, padx=10,
                                                                                       pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv")])
        if file_path:
            self.video_path.set(file_path)
            self.display_metadata(file_path)
            self.play_video(file_path)

    def upload_video(self,file_path):
        bitrate = self.bitrate_aleatorio.get()
        if not file_path:
            return

        try:
            with open(file_path, 'rb') as f:
                response = requests.post('http://127.0.0.1:5001/process_video', files={'video': f}, data={'bitrate': bitrate})

            if response.status_code == 200:
                output_path = "./temp.mp4"
                #with open(output_path, 'wb') as f:
                    #self.write(response.content)
                self.play_video(output_path)
                self.display_metadata(output_path)
                self.video_path.set(output_path)
            else:
                print(f"Failed to process video")
        except Exception as e:
            print(f"An error occurred: {e}")

    def display_metadata(self, file_path):
        if file_path is not None:
            try:
                print(f" path es: {self.video_path.get()}")
                resolution,codec,bitrate = lab_recu.get_video_info(self.video_path.get())
                #resolution, codec, bitrate = lab_recu.get_video_info(file_path)
                metadata = (f"Bit Rate: {bitrate}\nCodec: {codec}\nResolution: {resolution[0]}x{resolution[1]} "
                            f"\nChroma Subsampling: {self.chroma_subsampling[self.current_subsampling_index]}")
                self.metadata_text.delete(1.0, tk.END)
                self.metadata_text.insert(tk.END, metadata)
                #self.out_video_path = self.video_path
            except Exception as e:
                self.metadata_text.delete(1.0, tk.END)
                self.metadata_text.insert(tk.END, f"Error obteniendo metadatos: {str(e)}")

    def play_video(self, file_path):
        self.cap = cv2.VideoCapture(file_path)
        self.show_frame()

    def show_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = cv2.resize(cv2image, (640, 480))
                imgtk = ImageTk.PhotoImage(image=Image.fromarray(img))
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
                self.root.after(10, self.show_frame)
            else:
                self.cap.release()

    def select_random_bitrate(self):
        try:
            # Generar un bitrate aleatorio
            new_bitrate = lab_recu.get_random_bitrate(self.video_path.get())
            self.bitrate_aleatorio.set(int(new_bitrate))

        except Exception as e:
            print(f"Error obteniendo el bitrate del video: {str(e)}")
            return None

    def change_chroma_subsampling(self):
        if self.video_path.get():
            self.current_subsampling_index = (self.current_subsampling_index + 1) % len(self.chroma_subsampling)
            subsampling = self.chroma_subsampling[self.current_subsampling_index]
            lab_recu.change_chroma_subsampling(self.video_path.get(), str(self.out_video_path.get()), subsampling)
            self.current_color_sub.set(f"{subsampling} ")
        else:
            print("Por favor, seleccione un archivo de video primero.")
            self.current_color_sub.set(f" N/A ")

    def start_process(self):
        if self.process_thread is None or not self.process_thread.is_alive():
            self.process_thread = Thread(target=self.run_encoding_process)
            self.process_thread.start()

    def run_encoding_process(self):
        # Llamar a la función encoding_ladder del archivo lab_recu.py
        #if self.bitrate_aleatorio.get():
        output_video_path = "./temp2.mp4"
        self.out_video_path.set(output_video_path)
            #self.upload_video()
            #self.video_path.set(self.out_video_path.get())
            # lab_recu.encoding_ladder(self.video_path.get(), int(self.bitrate_aleatorio.get().split()[0]),
                                     # output_video_path)
        if self.video_path.get():
            shutil.copy2(self.video_path.get(), self.out_video_path.get())
            self.upload_video(self.out_video_path.get())
            self.display_metadata(self.out_video_path.get())
            # Reproducir el video recodificado
            self.play_video(self.out_video_path.get())


def run_flask_app():
    subprocess.run(['python3', 'app.py'])


if __name__ == "__main__":

    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()

    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()

    flask_thread.join()

