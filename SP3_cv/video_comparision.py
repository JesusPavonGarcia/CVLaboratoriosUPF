import subprocess


def videos_comparision(input_video_1, input_video_2, output_file):
    try:
        # Concatenate videos horizontally for side-by-side comparison
        cmd = [
            "ffmpeg",
            "-i", input_video_1,
            "-i", input_video_2,
            "-filter_complex", "[0:v][1:v]hstack=inputs=2[v];[0:a][1:a]amerge[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y", output_file
        ]
        subprocess.run(cmd, check=True)

        print(f"Comparison video created. Output file: {output_file}")
        return output_file

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# side-by-side comparison video
# compare_videos(input_video_1, input_video_2, "comparison_output.mp4")

# In the case of comparing vp8 and vp9, the video using the vp9 format has a better quality
# than the other. Infact it has a size of around 65Mb while the vp8 about 30Mb.