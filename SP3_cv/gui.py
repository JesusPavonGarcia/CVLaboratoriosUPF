import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import cv2
from PIL import Image, ImageTk
import lab3 as video_functions

class VideoConverterGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Video Converter")

        self.input_label = tk.Label(master, text="Input File:")
        self.input_label.grid(row=0, column=0, padx=10, pady=10)

        self.input_entry = tk.Entry(master, width=50)
        self.input_entry.grid(row=0, column=1, padx=10, pady=10)

        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.output_label = tk.Label(master, text="Output File:")
        self.output_label.grid(row=1, column=0, padx=10, pady=10)

        self.output_entry = tk.Entry(master, width=50)
        self.output_entry.grid(row=1, column=1, padx=10, pady=10)

        self.quality_label = tk.Label(master, text="Video Quality:")
        self.quality_label.grid(row=2, column=0, padx=10, pady=10)

        self.quality_var = tk.StringVar()
        self.quality_var.set("720p")  # Default quality
        qualities = ["720p", "480p", "240p", "120p"]
        self.quality_menu = tk.OptionMenu(master, self.quality_var, *qualities)
        self.quality_menu.grid(row=2, column=1, padx=10, pady=10)

        self.codec_label = tk.Label(master, text="Video Codec:")
        self.codec_label.grid(row=3, column=0, padx=10, pady=10)

        self.codec_var = tk.StringVar()
        self.codec_var.set("h264")  # Default codec
        codecs = ["h264", "h265", "vp8", "vp9"]
        self.codec_menu = tk.OptionMenu(master, self.codec_var, *codecs)
        self.codec_menu.grid(row=3, column=1, padx=10, pady=10)

        self.convert_button = tk.Button(master, text="Convert", command=self.convert_and_play)
        self.convert_button.grid(row=4, column=1, pady=20)

        # Canvas to display video
        self.canvas = tk.Canvas(master, width=640, height=480)
        self.canvas.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, file_path)

    def convert_and_play(self):
        self.convert_video()

        output_file = self.output_entry.get()
        if not output_file:
            return

        try:
            cap = cv2.VideoCapture(output_file)

            # Get the video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # Update the canvas size
            self.canvas.config(width=width, height=height)

            ret, frame = cap.read()
            while ret:
                # Convert the OpenCV BGR image to RGB
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img = ImageTk.PhotoImage(img)

                # Update the canvas with the new frame
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img)

                self.master.update_idletasks()
                self.master.update()

                ret, frame = cap.read()

            cap.release()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while playing the video: {str(e)}")

    def convert_video(self):
        input_file = self.input_entry.get()
        resolution = self.quality_var.get()
        format = self.codec_var.get()

        if not input_file:
            messagebox.showerror("Error", "Please select input and output files.")
            return

        video_class = video_functions.VideoConverter(input_file, resolution, format)
        video_converted = video_class.process_video()

        print("Converting video, please wait...")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterGUI(root)
    root.mainloop()
