import subprocess
import lab2 as util_functions
import os
import video_comparision as compare


def resolution_video(input_video, resolution):

    try:
        output_file = f"{input_video[:-4]}_res_{resolution[4:]}.mp4"
        util_functions.modify_resolution(input_video, output_file, resolution)

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
    except Exception as e:
        print(f"Error: {e}")

    return output_file


def modify_format(input_video, format):

    try:
        if format in ["vp8", "vp9"]:
            output_file = f"{input_video[:-4]}_format_{format}.webm"
        elif format in ["h265", "av1"]:
            output_file = f"{input_video[:-4]}_format_{format}.mp4"

        # Convert video to the specified format using ffmpeg
        cmd = [
            "ffmpeg",
            "-i", input_video,
            "-c:v", format,
            "-c:a", "copy",
            "-y", output_file
        ]
        subprocess.run(cmd, check=True)

        print(f"Video converted to {format}. Output file: {output_file}")
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


class VideoConverter:
    def __init__(self, input_video, resolution, format):
        self.input_video = input_video
        self.resolution = resolution
        self.format = format

    def process_video(self):
        try:
            new_res_video = resolution_video(self.input_video, self.resolution)
            new_res_format_video = modify_format(new_res_video, self.format)
        finally:
            if os.path.exists(new_res_video):
                os.remove(new_res_video)

        return new_res_format_video


def main():

    #Exercise 1
    input_path = "/mnt/c/codificacion_video/cvlaboratoriosupf/sp3_cv/Big_Buck_Bunny_720_10s_20MB.mp4"
    formats = ["vp9", "vp8", "h265", "av1"]
    resolutions = ["854:480", "1280:720", "360:240", "160:120"]

    # Si queremos obtener todas las combinaciones de res y formato posible
        # for format in formats:
        #     for resolution in resolutions:
        #         video = VideoConverter(input_path, resolution, format)
        #         video.process_video()

    video = VideoConverter(input_path, resolutions[0], formats[0])
    #input_path_2 = video.process_video()

    video2 = VideoConverter(input_path, resolutions[1], formats[1])
    #input_path_3 = video2.process_video()


    #Exercise 2
    input_path_4 = modify_format(input_path, formats[1])
    input_path_5 = modify_format(input_path, formats[0])


    output_file = f"{input_path_4[:-4]}_divide_screen.mp4"

    output_file = compare.videos_comparision(input_path_4, input_path_5, output_file)


if __name__ == "__main__":
    main()
