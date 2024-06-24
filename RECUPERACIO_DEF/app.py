from flask import Flask, request, send_file
import os
import zipfile
import lab_recu

app = Flask(__name__)


@app.route('/process_video', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return "No file part", 400

    file = request.files['video']
    file_path = f'./{file.filename}'
    file.save(file_path)

    usr_bitrate = request.form.get('bitrate')
    usr_chroma_subsampling = request.form.get('chroma_sub')

    # Procesar el video
    processed_zip_path = process_encoding_ladder(file_path, usr_bitrate, usr_chroma_subsampling)

    return send_file(processed_zip_path, as_attachment=True)


def process_encoding_ladder(file_path, usr_bitrate, usr_chroma_subsampling):
    # Aquí irían las funciones de encoding ladder creadas por ti
    # Ejemplo: usando ffmpeg para crear diferentes resoluciones
    output_path = './processed_video2.mp4'
    output_path_txt = './text/video_info_temp.txt'
    input_path_txt = './text/video_info_original.txt'

    #new_bitrate = lab_recu.get_random_bitrate(file_path)
    new_bitrate = int(usr_bitrate)
    chroma_sub = str(usr_chroma_subsampling)
    if chroma_sub is not None:
        lab_recu.parse_video_info(file_path, "text/video_info_original.txt")
        lab_recu.change_chroma_subsampling(file_path, output_path, chroma_sub)
        if new_bitrate is not None:
            # Comando de ejemplo para cambiar resolución y bitrate
            file_path = output_path
            output_path = './processed_video.mp4'
            lab_recu.encoding_ladder(file_path, new_bitrate, output_path)
            lab_recu.parse_video_info(output_path, "text/video_info_temp.txt")


        zip_path = output_path.rsplit('.', 1)[0] + '.zip'
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_path, os.path.basename(output_path))
            zipf.write(output_path_txt, os.path.basename(output_path_txt))
            zipf.write(input_path_txt, os.path.basename(input_path_txt))
        return zip_path


if __name__ == '__main__':
    app.run(port=5002, debug=True)


