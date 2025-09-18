import os
from pydub import AudioSegment
import subprocess


def normalize_audio_volume(input_path, output_suffix="_normalized", target_lufs=-16.0):
    """
    Нормализует аудио по EBU R128 (для голосовых).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    base_path, ext = os.path.splitext(input_path)
    ext = ext.lower()
    output_path = base_path + output_suffix + ext

    try:
        audio = AudioSegment.from_file(input_path, format=ext[1:])
        audio.export(
            output_path,
            format='wav',
            parameters=[
                "-af", f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11"
            ]
        )
        return os.path.abspath(output_path)
    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Ошибка при обработке аудио: {e}")


# Альтернативная функция в utils.py (без moviepy!)
def process_video_note(video_path, boost_db=10, output_suffix="_louder"):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Файл не найден: {video_path}")

    base_path, ext = os.path.splitext(video_path)
    output_path = base_path + output_suffix + ext

    try:
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-af", f"volume={boost_db}dB",  # Усиление звука
            "-vcodec", "libx264",
            "-vf", "scale=480:480:force_original_aspect_ratio=decrease,pad=480:480:(ow-iw)/2:(oh-ih)/2",
            "-pix_fmt", "yuv420p",
            "-tune", "stillimage",
            "-preset", "ultrafast",
            "-crf", "24",
            "-ac", "1",           # Моно
            "-ar", "44100",       # Частота
            "-c:a", "aac",        # Кодек аудио
            "-b:a", "128k",
            "-f", "mp4",
            "-y",                 # Перезаписать
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg ошибка: {result.stderr}")

        return os.path.abspath(output_path)

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Ошибка при обработке видео-сообщения: {e}")