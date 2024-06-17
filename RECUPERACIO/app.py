from flask import Flask, request, send_file
import os
import subprocess
import lab_recu

app = Flask(__name__)


@app.route('/process_video', methods=['POST'])
def process_video():
    file = request.files['video']
    bitrate = request.form.get('bitrate')
    file_path = f'./{file.filename}'
    file.save(file_path)

    # Procesar el video
    processed_file_path = process_encoding_ladder(file_path, bitrate)

    return send_file(processed_file_path,as_attachment=True)


def process_encoding_ladder(file_path, new_bitrate):
    # Aquí irían las funciones de encoding ladder creadas por ti
    # Ejemplo: usando ffmpeg para crear diferentes resoluciones
    output_path = './temp.mp4'

    # Comando de ejemplo para cambiar resolución y bitrate
    lab_recu.encoding_ladder(file_path, int(new_bitrate), output_path)

    return output_path


if __name__ == '__main__':
    app.run(port=5001, debug=True)


