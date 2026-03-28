import argparse

from system import main


# Перех команды консоли
parser = argparse.ArgumentParser()
parser.add_argument('--video', type=str, required=True)  # Переменная с директорией видео
args = parser.parse_args()

video_file = args.video

# Вызов главной функции
main(video_file=video_file)
