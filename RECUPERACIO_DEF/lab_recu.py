import subprocess
import os
import json
import random
import shutil


def parse_video_info(video_file, text_path):
    # Utilizando ffmpeg redirigimos toda la información del terminal a una cadena de texto
    cmd = f"ffmpeg -i {video_file}"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    output, _ = process.communicate()
    X,Y,Z = get_video_info(video_file)
    # Escribe en un fichero la cadena de texto generada por ffmpeg en el terminal
    with open(text_path, "w") as file:
        file.write(output)
        file.write(f"\n RES: {X}")
        file.write(f"\n CODEC: {Y}")
        file.write(f"\n BITRATE: {Z}")


def encoding_ladder(input_file, threshold_bitrate, output_file):
    #threshold_bitrate simula network bandwith del usuario
    print("INFO ORIGINAL")
    res, codec, bitrate = get_video_info(input_file)
    bitrate = int(bitrate)
    new_res = ""

    #parse_video_info(input_file, "text/video_info_original.txt")
    print(f"{threshold_bitrate}")
    if bitrate > threshold_bitrate:
        if bitrate >= 2*threshold_bitrate:
            new_res = f"{int(res[0]/2)}x{int(res[1]/2)}"
            if bitrate >= 4*threshold_bitrate:
                new_res = f"{int(res[0] / 4)}x{int(res[1] / 4)}"
                if bitrate >= 8*threshold_bitrate:
                    new_res = f"{int(res[0] / 8)}x{int(res[1] / 8)}"
    elif threshold_bitrate >= bitrate:
        new_res = f"{int(res[0])}x{int(res[1])}"

    try:
        if int(new_res[0]) < int(res[0]) and int(new_res[1]) < int(res[1]):
            encoding_video(input_file, output_file, new_res, codec, bitrate)
        else:
            encoding_video(input_file, output_file, res, codec, bitrate)
            #get_video_info(output_file)
            #parse_video_info(output_file, "text/video_info_temp.txt")
    except Exception as e:
        print(f"Error en la codificación: {str(e)}")


def get_video_info(input_file):
    # Utilizando ffprobe conseguimos toda la info del input_video
    cmd = f"ffprobe -v quiet -print_format json -show_format -show_streams {input_file}"
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    resolution = []
    codec = ""
    bitrate = ""
    if result.returncode == 0:
        video_info = json.loads(result.stdout)
        if 'streams' in video_info:
            streams = video_info['streams'][0]  # resultado se carga en una lista en forma de cadena de texto
            resolution = [int(streams['width']), int(streams['height'])]
            codec = f"{streams['codec_name']}"
            bitrate = f"{streams['bit_rate']}"
            # Selecciona la información relevante
            print(f"Video Information of \n{input_file}:\n")
            print(f"Duration: {streams['duration']} seconds")
            print(f"Resolution: {streams['width']}x{streams['height']}")
            print(f"Codec: {codec} ")
            print(f"Format: {video_info['format']['format_name']}")

            if 'bit_rate' in streams:
                print(f"Bitrate: {bitrate} bits/s")
            else:
                print("Bitrate information not available.")

            print("\n\n")
        else:
            print("No video streams found in the file.")
    else:
        print("Error occurred while retrieving video information.")
    return resolution, codec, bitrate


def change_chroma_subsampling(input_file, output_file, subsampling):
    # Cambia chroma subsampling usando ffmpeg
    cmd = f"ffmpeg -y -i {input_file} -vf format={subsampling} -c:v libx264 -crf 23 -preset medium -c:a copy {output_file}"
    subprocess.call(cmd, shell=True)


def encoding_video(input_file, output_file, new_resolution, codec, video_bitrate):
    # Modifica resolución de video con ffmpeg, estableciendo un rango de bitrate y sobrescribe sin confirmación
    cmd = f"ffmpeg -y -i {input_file} -b:v {video_bitrate} -vf scale={new_resolution} -c:v {codec} {output_file}"
    subprocess.call(cmd, shell=True)


def get_random_bitrate(input_file):
    new_bitrate = 0
    try:
        resolution, codec, bitrate = get_video_info(input_file)

        if bitrate is not None:
            # Generar un bitrate aleatorio
            options = [0.5, 0.25, 0.125, 0.0625, 1, 2, 4, 8]  # Múltiplos de bitrate original
            multiplier = random.choice(options)
            new_bitrate = int(int(bitrate) * multiplier)
            return new_bitrate
        else:
            new_bitrate = 0
    except Exception as e:
        print(f"Error obteniendo el bitrate del video: {str(e)}")
        return new_bitrate

