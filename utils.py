import os
from pydub import AudioSegment

def normalize_audio_volume(input_path, output_suffix="_normalized", target_lufs=-16.0):
    """
    Нормализует аудио по воспринимаемой громкости (Loudness) по стандарту EBU R128.
    
    :param input_path: Путь к входному .mp3 или .ogg файлу
    :param output_suffix: Суффикс для имени выходного файла
    :param target_lufs: Целевой уровень громкости в LUFS (обычно -16 для музыки)
    :return: Полный путь к сохранённому нормализованному файлу
    """
    # Проверяем существование файла
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Файл не найден: {input_path}")

    # Определяем расширение
    base_path, ext = os.path.splitext(input_path)
    ext = ext.lower()
    output_path = base_path + output_suffix + ext

    try:
        # Загружаем аудио
        audio: AudioSegment = AudioSegment.from_file(input_path, format=ext[1:])

        # экспортируем с применением ffmpeg-фильтра loudnorm
        audio.export(
            output_path,
            format='wav',  # или оставить исходный формат
            parameters=[
                "-af",
                f"loudnorm=I={target_lufs}:TP=-1.5:LRA=11",
            ]
        )

        return os.path.abspath(output_path)

    except Exception as e:
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError(f"Ошибка при обработке аудио: {e}")