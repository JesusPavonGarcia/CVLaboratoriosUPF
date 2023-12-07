import subprocess


def videos_comparision(video_1, video_2, output_file):
    try:
        # Concatenate videos horizontally for side-by-side comparison
        cmd = [
            "ffmpeg",
            "-i", video_1,
            "-i", video_2,
            "-filter_complex", "[0:v][1:v]hstack=inputs=2[v]",
            "-map", "[v]",
            "-c:v", "libx264",
            "-y", output_file
        ]
        subprocess.run(cmd, check=True)

        return output_file

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
