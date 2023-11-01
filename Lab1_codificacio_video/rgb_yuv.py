import sys
import subprocess
import os
import io
from PIL import Image
import numpy as np
from scipy.fft import dct, idct

# Script Python creado con Windows. Para llamar a ffmpeg he utilizado WSL,
# llamando script mediante python3 rgb_yuv.py en cada ejecución.
def rgb_to_yuv(r, g, b):
    # Formula
    y = 0.257 * r + 0.504 * g + 0.098 * b + 16
    Cb = u = -0.148 * r - 0.291 * g + 0.439 * b + 128
    Cr = v = 0.439 * r - 0.368 * g - 0.071 * b + 128
    return y, u, v


def yuv_to_rgb(y, u, v):
    #Formula
    r = 1.164 * (y - 16) + 1.596 * (v - 128)
    g = 1.164 * (y - 16) - 0.813 * (v - 128) - 0.391 * (u - 128)
    b = 1.164 * (y - 16) + 2.018 * (u - 128)
    return r, g, b


# Metodo para printar la conversion de los metodos anteriores según sea rgb o yuv
def color_coordinates(type, arg1, arg2, arg3):
    if type == "rgb":
        r = arg1
        g = arg2
        b = arg3
        y, u, v = rgb_to_yuv(r, g, b)
        print(f"RGB({r}, {g}, {b}) -> YUV({y}, {u}, {v})")
    else:
        y = arg1
        u = arg2
        v = arg3
        r, g, b = yuv_to_rgb(y, u, v)
        print(f"YUV({y}, {u}, {v}) -> RGB({r}, {g}, {b})")


def resize_and_reduce_quality(input_image, output_image, width, height,quality):
    # Con el comando de ffmpeg cmd reduce el tamaño y calidad de la imagen.
    try:
        cmd = [
            'ffmpeg',
            '-i', input_image,
            '-vf',  f'scale={width}:{height}',
            '-q:v', f'{quality}',
            output_image
        ]
        subprocess.run(cmd)
        print(f"Image reduce size with FFMPEG. Output saved as {output_image}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def serpentine(input_image, output_file):
    #Obtiene valores de la imagen y crea lista donde aplica la manera de lectura de bytes serpentine
    with Image.open(input_image) as img:
        width, height = img.size
        image_bytes = img.tobytes()

    serpentine_bytes = []
    # Se leen los bytes de las columnas pares. Se recorren las columnas de izquierda a derecha y se agregan los bytes
    for y in range(height):
        if y % 2 == 0:
            for x in range(width):
                index = y * width + x
                if index < len(image_bytes):
                    serpentine_bytes.append(str(image_bytes[index]))
        else:
            # En caso contrario se leen filas impares. Recorre las columnas en orden inverso
            for x in range(width - 1, -1, -1):
                index = y * width + x
                if index < len(image_bytes):
                    serpentine_bytes.append(str(image_bytes[index]))

    # Escritura en un fichero de los bytes resultantes
    output = output_file

    with open(output, 'w') as output_file:
        output_file.write(' '.join(serpentine_bytes))


def color_to_black_and_white(input_image, output_image, level_compresion):
        # Con el comando de ffmpeg cmd convierte imagen en blanco y negro y despues aplica una compresión alta ee la imagen output
        try:
            # FFMPEG command to convert image to black and white with high compression
            cmd = [
                'ffmpeg',
                '-i', input_image,
                '-vf', 'format=gray',
                '-crf', f'{level_compresion}', output_image
            ]
            # Ejecuta FFMPEG cmd usando subprocess
            subprocess.run(cmd)
            print(f"Image converted to black and white and compressed with FFMPEG. Output saved as {output_image}")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


def run_length_encode(data):
    # El código que proporcionaste implementa un algoritmo de compresión llamado "Run-Length Encoding" (RLE),
    # el cual busca reducir la cantidad de datos necesarios para representar una secuencia manteniendo la misma información.
    encoded = []
    i = 0
    n = len(data)

    while i < n:
        count = 1
        # cuenta cuántas veces se repite un valor consecutivo en la secuencia, actualiza la variable
        while i < n - 1 and data[i] == data[i + 1]:
            count += 1
            i += 1
        # Añade datos a la lista
        encoded.append((count, data[i]))
        i += 1

    # Print resultado
    print("\nEncoded data:", encoded)


def dct_transform(data):
    #  DCT transformation
    transform_data = dct(dct(data.T, norm='ortho').T, norm='ortho')
    print("\nDCT Transformed Data:")
    print(transform_data)

    return transform_data


def inverse_dct_transform(data):
    # inverse DCT transformation
    original_data = idct(idct(data.T, norm='ortho').T, norm='ortho')
    print("\nOriginal Data from Inverse DCT:")
    print(original_data)

    return original_data


def main():

    #call ex1
    print("\nRGB/YUV Transformation:")
    # example of rgb->yuv rang RGB 0-255
    color_coordinates("rgb",255,255,255)
    # example of yuv->rgb rang YCbCr (16-235 ; 0-128 , 0-128)
    color_coordinates("yuv", 16, 128, 128)

    # example of rgb->yuv rang RGB 0-255
    color_coordinates("rgb",120,30,90)
    # example of yuv->rgb rang YCbCr (16-235 ; 0-128 , 0-128)
    color_coordinates("yuv", 128, 90, 50)

    #call ex2
    # Ejemplo de redimensionar y reducir calidad de una imagen (puedes personalizar esto)
    input_image = 'input_image.jpg'
    output_image = '/mnt/c/codificacion_video/lab1_codificacio_video/output_image_lower_quality.jpg'
    width = 640
    height = 200
    quality = 50
    resize_and_reduce_quality(input_image, output_image, width, height, quality)

    #call ex3
    output_file = 'output_serpentine_file.txt'
    serpentine(input_image, output_file)

    # call ex4
    level_compresion= 50
    output_image = '/mnt/c/codificacion_video/lab1_codificacio_video/output_image_black_and_white.jpg'
    color_to_black_and_white(input_image, output_image, level_compresion)

    #call ex5
    input_bytes = b'AAABBCCCCDDDD'
    run_length_encode(input_bytes)

    #call ex6
    input_data = np.array([[231, 32, 233, 161, 24, 71, 140, 245],
                           [247, 40, 248, 245, 124, 204, 36, 107],
                           [234, 202, 245, 167, 9, 217, 239, 173],
                           [193, 190, 100, 167, 43, 180, 8, 70],
                           [11, 24, 210, 177, 81, 243, 8, 112],
                           [97, 195, 203, 47, 125, 114, 165, 181],
                           [193, 70, 174, 167, 41, 30, 127, 63],
                           [169, 141, 29, 178, 38, 224, 209, 25]])

    # DCT transformation
    transformed_data = dct_transform(input_data)

    # Inverse DCT transformation
    original_data = inverse_dct_transform(transformed_data)


if __name__ == "__main__":
    main()
