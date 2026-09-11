# inpaint_choice.py
import argparse
import json
import cv2
import torch
from process_video import process_video  # твоя функция обработки видео
from remove_from_json import remove_objects  # твоя функция работы с JSON

def inpaint_opencv(frame, mask):
    """Inpaint с использованием OpenCV"""
    return cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)

def inpaint_lama(frame, mask, device='cuda'):
    """Inpaint с использованием LAMA / PyTorch"""
    # пример вызова модели LAMA
    from lama_model import run_lama  # предположим, есть такой скрипт
    return run_lama(frame, mask, device=device)

def main():
    parser = argparse.ArgumentParser(description="Выбор модели для Inpaint")
    parser.add_argument('--model', type=str, default='opencv', choices=['opencv', 'lama'],
                        help='Модель для Inpaint: opencv или lama')
    parser.add_argument('--video', type=str, default='input.mp4', help='Путь к видео')
    parser.add_argument('--json', type=str, default='input.json', help='Путь к JSON с объектами')
    parser.add_argument('--output', type=str, default='output.mp4', help='Выходное видео')
    args = parser.parse_args()

    # Загружаем JSON с объектами для удаления
    with open(args.json, 'r') as f:
        data = json.load(f)

    # Открываем видео
    cap = cv2.VideoCapture(args.video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Получаем маску для текущего кадра из JSON
        mask = remove_objects(frame_idx, data)  # возвращает маску 0/255

        # Выбираем модель
        if args.model == 'opencv':
            inpainted = inpaint_opencv(frame, mask)
        else:
            inpainted = inpaint_lama(frame, mask)

        out.write(inpainted)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"[INFO] Видео обработано. Сохранено в {args.output}")

if __name__ == '__main__':
    main()