import subprocess
import tempfile


def extract_status():
    return ""


def get_video_frame_rate(filename):
    result = subprocess.run(
        [
            "./ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            "-show_entries",
            "stream=r_frame_rate",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result_string = result.stdout.decode("utf-8").split()[0].split("/")
    fps = float(result_string[0]) / float(result_string[1])
    return fps


def get_video_length_seconds(filename):
    result = subprocess.run(
        [
            "./ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    result_string = result.stdout.decode("utf-8").split()[0]
    return float(result_string)


def loop_video_until_length(filename, length):
    # use stream_loop to loop video until it's at least length seconds long
    video_length = get_video_length_seconds(filename)
    if video_length < length:
        loops = int(length / video_length)
        new_filename = tempfile.mkstemp(suffix=".mp4")[1]
        out = subprocess.call(
            [
                "./ffmpeg",
                "-stream_loop",
                str(loops),
                "-i",
                filename,
                "-c",
                "copy",
                "-y",
                new_filename,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        return new_filename
    else:
        return filename
