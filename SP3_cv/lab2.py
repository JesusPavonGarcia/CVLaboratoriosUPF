import subprocess
import os
import json
import rgb_yuv as lab1
import shutil


def convert_to_mp2(input_video, output_video):
    # Llamamos a ffmpeg para convertir video a mpeg2 (formato mp2)
    try:
        cmd = f"ffmpeg -i {input_video} -c:v mpeg2video {output_video}"
        subprocess.call(cmd, shell=True)
        print(f"Video converts to mp2 with FFMPEG. Output saved as {output_video}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_video_info(video_file, text_path):
    # Utilizando ffmpeg redirigimos toda la información del terminal a una cadena de texto
    cmd = f"ffmpeg -i {video_file}"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output, _ = process.communicate()

    # Escribe en un fichero la cadena de texto generada por ffmpeg en el terminal
    with open(text_path, "w") as file:
        file.write(output)


def modify_resolution(input_file, output_file, new_resolution, video_bitrate="2M"):
    # Modifica resolución de video con ffmpeg , estableciendo un rango de bitrate
    cmd = f"ffmpeg -i {input_file} -b:v {video_bitrate} -vf scale={new_resolution} {output_file}"
    subprocess.call(cmd, shell=True)


def change_chroma_subsampling(input_file, output_file, subsampling):
    # Cambia chroma subsampling usando ffmpeg
    cmd = f"ffmpeg -i {input_file} -vf format={subsampling} -c:v libx264 -crf 23 -preset medium -c:a copy {output_file}"
    subprocess.call(cmd, shell=True)


def get_video_info(input_file):
    # Utilizando ffprobe conseguimos toda la info del input_video
    cmd = f"ffprobe -v quiet -print_format json -show_format -show_streams {input_file}"
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)

    if result.returncode == 0:
        video_info = json.loads(result.stdout)
        if 'streams' in video_info:
            streams = video_info['streams'][0]  # resultado se carga en una lista en forma de cadena de texto

            # Selecciona la información relevante
            print(f"Video Information of \n{input_file}:\n")
            print(f"Duration: {streams['duration']} seconds")
            print(f"Resolution: {streams['width']}x{streams['height']}")
            print(f"Codec: {streams['codec_name']}")
            print(f"Format: {video_info['format']['format_name']}")

            if 'bit_rate' in streams:
                print(f"Bitrate: {streams['bit_rate']} bits/s")
            else:
                print("Bitrate information not available.")

            print("\n\n")
        else:
            print("No video streams found in the file.")
    else:
        print("Error occurred while retrieving video information.")


def color_to_bw_and_reduce(input_path,output_path,lvl_compression, width, height, quality=50):
    # Función heredada por funciones del archivo rgb_yuv.py del lab1. Primero convierte el video a b/w para mas tarde
    # reducir la resolucion.

    output_path2 = "/mnt/c/codificacion_video/CVLaboratoriosUPF/Lab2_cv/temp.mp4" # Path temporal que más tarde se elimina
    try:
        # llama 2 funciones de lab1
        lab1.color_to_black_and_white(input_path, output_path, lvl_compression)
        # copia video a path temporal
        shutil.copy(output_path, output_path2)
        lab1.resize_and_reduce_quality(output_path2, output_path, width, height, quality)
    finally:
        # elimina archivo de video path temporal
        if os.path.exists(output_path2):
            os.remove(output_path2)


def main():

    input_video_path = "Big_Buck_Bunny_720_10s_20MB.mp4"  # Replace with your input video file
    parse_video_info(input_video_path, "text/video_info_original.txt")

    # Call ex1
    # Convierte a mp2 y genera archivo de texto con la info
    output_video_path = "/mnt/c/codificacion_video/CVLaboratoriosUPF/Lab2_cv/video/Big_Buck_Bunny_conversion.mpg"
    convert_to_mp2(input_video_path, output_video_path)
    parse_video_info(output_video_path, "text/video_info_mp2.txt")

    # Call ex2
    # Cambia la resolución y genera archivo de texto con la info
    output_video_path_resolution = "/mnt/c/codificacion_video/CVLaboratoriosUPF/Lab2_cv/video/Big_Buck_Bunny_modified_res.mp4"
    new_resolution = "854:480"  # or # "2560:1440"
    modify_resolution(input_video_path, output_video_path_resolution, new_resolution)
    parse_video_info(output_video_path_resolution, "text/video_info_modified_res.txt")

    # Call ex3
    # Cambia el chroma subsampling y genera archivo de texto con la info
    output_video_path_changed_subsampling = \
        "/mnt/c/codificacion_video/CVLaboratoriosUPF/Lab2_cv/video/Big_Buck_Bunny_changeg_subsampling.mp4"
    new_subsampling = "yuv444p"
    change_chroma_subsampling(input_video_path, output_video_path_changed_subsampling, new_subsampling)
    parse_video_info(output_video_path_changed_subsampling, "text/video_info_subsampling.txt")

    # Call ex4
    # Print en terminal wsl diferente info relevante de los videos generados
    get_video_info(input_video_path)
    get_video_info(output_video_path)
    get_video_info(output_video_path_resolution)
    get_video_info(output_video_path_changed_subsampling)

    # Call ex5
    # Convierte video a bw , reduce resolución y genera archivo de texto con la info
    output_video_path_bw = "/mnt/c/codificacion_video/CVLaboratoriosUPF/Lab2_cv/video/Big_Buck_Bunny_bw.mp4"
    color_to_bw_and_reduce(input_video_path, output_video_path_bw, 20, 640, 360)
    parse_video_info(output_video_path_bw, "text/video_info_bw_reduce.txt")


if __name__ == "__main__":
    main()
