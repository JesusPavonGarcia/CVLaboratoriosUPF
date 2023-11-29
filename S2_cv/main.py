import subprocess
import json
import os


class Video_processor:

    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path

    def cut_and_process_video(self, start_time, duration):
        output_temp = "/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/temp.mp4"
        try:
            # Step 1: Cut the video using ffmpeg
            cmd = f"ffmpeg -i {self.input_path} -ss {start_time} -t {duration} -c copy {output_temp}"
            subprocess.run(cmd, shell=True)

            # Step 2: Process the cut video to show macroblocks and motion vectors
            # Command to generate a video showing macroblocks and motion vectors
            cmd = f"ffmpeg -flags2 +export_mvs -i {output_temp}  -vf codecview=mv=pf+bf+bb {self.output_path} "
            subprocess.run(cmd, shell=True)
        finally:
            # elimina archivo de video path temporal
            if os.path.exists(output_temp):
                os.remove(output_temp)

    def create_bbb_container(self, output_audio_mono, output_audio_lower, output_audio_aac, output_container):
        # Cut BBB into 50s video
        subprocess.run(f"ffmpeg -i {self.input_path} -ss 50 -t 50 -c:v copy -c:a copy {self.output_path}", shell=True)

        # audio as mono
        subprocess.run(f"ffmpeg -i {self.output_path} -ac 1 {output_audio_mono}", shell=True)

        # audio with lower bitrate
        subprocess.run(f"ffmpeg -i {self.output_path} -ac 2 -b:a 64k {output_audio_lower}", shell=True)

        # audio in AAC codec
        subprocess.run(f"ffmpeg -i {self.output_path} -strict experimental -ac 2 -b:a 128k -c:a aac {output_audio_aac}", shell=True)

        # Package in a .mp4
        subprocess.run(f'ffmpeg -i {self.output_path} -i {output_audio_mono} -i {output_audio_lower} -i {output_audio_aac}'
                  f'-c:v copy -c:a copy -map 0:v:0 -map 1:a:0 -map 2:a:0 -map 3:a:0 {output_container}', shell=True)

    def counter_tracks_container(self):
        ffprobe = f'ffprobe -v error -show_entries stream=codec_type -of json {self.input_path}'

        # get stream information
        result = subprocess.run(ffprobe, capture_output=True, text=True, shell=True)
        stream_info = json.loads(result.stdout)

        video = sum(1 for stream in stream_info['streams'] if stream['codec_type'] == 'video')
        audio = sum(1 for stream in stream_info['streams'] if stream['codec_type'] == 'audio')
        subtitle = sum(1 for stream in stream_info['streams'] if stream['codec_type'] == 'subtitle')

        num_tracks = audio + video + subtitle

        print(f"The Nº of video: {video}")
        print(f"The Nº of audio: {audio}")
        print(f"The Nº of subtitle: {subtitle}")
        print(f" The Nº of tracks of your Container is  {num_tracks}")

    def subtitles(self, subtitle_file):
        command = f"ffmpeg -i {self.input_path} -vf subtitles={subtitle_file} {self.output_path}"
        subprocess.run(command, shell=True)


def main():
    input_video_path = "bbb_720p.mp4"  # Replace with your input video file

    # Call ex1
    output_video_path = "/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/bbb_720_10s_20MB.mp4"
    processor = Video_processor(input_video_path, output_video_path)
    processor.cut_and_process_video(start_time=50, duration=9)

    # Call ex2
    output_name = "bbb_50s"
    output_video_path = f"/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/{output_name}.mp4"
    output_audio_mono = f"/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/{output_name}_mono.mp3"
    output_audio_lower = f"/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/{output_name}_lowrate.mp3"
    output_audio_aac = f"/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/{output_name}_aac.aac"
    output_container = f"/mnt/c/codificacion_video/CVLaboratoriosUPF/S2_cv/{output_name}_container.mp4"
    processor = Video_processor(input_video_path, output_video_path)
    processor.create_bbb_container(output_audio_mono, output_audio_lower, output_audio_aac, output_container)

    # Call ex3
    input_video_path = output_container
    processor = Video_processor(input_video_path, output_video_path)
    processor.counter_tracks_container()

    # Call ex4
    input_video_path = "bbb_720p.mp4"  # Replace with your input video file
    output_video_path = "bbb_720p_substitles.mp4"  # Replace with your input video file
    subtitle_file = 'big_buck_bunny.eng.srt'
    processor = Video_processor(input_video_path, output_video_path)
    processor.subtitles(subtitle_file)


if __name__ == "__main__":
    main()
