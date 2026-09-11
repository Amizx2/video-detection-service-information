import argparse
import json
from pathlib import Path

import cv2
from ultralytics import YOLO


def detect_video_to_json(
    model_path,
    input_video,
    output_json,
    output_video=None,
    conf=0.25,
    classes=None,
):
    model = YOLO(model_path)

    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        raise RuntimeError(f"Не удалось открыть видео: {input_video}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    writer = None

    if output_video:
        Path(output_video).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    annotations = {
        "video": {
            "path": input_video,
            "fps": fps,
            "width": width,
            "height": height,
            "total_frames": total_frames,
        },
        "model": {
            "path": model_path,
            "names": model.names,
        },
        "frames": [],
    }

    frame_index = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        results = model.predict(frame, conf=conf, verbose=False)
        result = results[0]

        frame_data = {
            "frame_index": frame_index,
            "time_sec": frame_index / fps if fps else 0,
            "objects": [],
        }

        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])

                if classes is not None and cls_id not in classes:
                    continue

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                class_name = model.names[cls_id]

                obj = {
                    "class_id": cls_id,
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2),
                    },
                }

                frame_data["objects"].append(obj)

                # Если нужно сохранить видео с рамками
                if writer is not None:
                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2,
                    )

                    label = f"{class_name} {confidence:.2f}"

                    cv2.putText(
                        frame,
                        label,
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2,
                    )

        annotations["frames"].append(frame_data)

        if writer is not None:
            writer.write(frame)

        frame_index += 1

        if frame_index % 30 == 0:
            print(f"Обработано кадров: {frame_index}")

    cap.release()

    if writer is not None:
        writer.release()

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)

    print(f"Готово. JSON-разметка сохранена: {output_json}")

    if output_video:
        print(f"Видео с рамками сохранено: {output_video}")


def parse_classes(classes_str):
    if classes_str is None:
        return None

    return [int(x.strip()) for x in classes_str.split(",") if x.strip()]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model",
        required=True,
        help="Путь к YOLO-модели, например runs/detect/train/weights/best.pt",
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Путь к входному видео",
    )

    parser.add_argument(
        "--json",
        default="output/annotations.json",
        help="Куда сохранить JSON-разметку",
    )

    parser.add_argument(
        "--output-video",
        default=None,
        help="Куда сохранить видео с нарисованными рамками",
    )

    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="Минимальная уверенность YOLO",
    )

    parser.add_argument(
        "--classes",
        default=None,
        help="ID классов через запятую, например 0,1,2. Если не указано, берутся все классы.",
    )

    args = parser.parse_args()

    detect_video_to_json(
        model_path=args.model,
        input_video=args.input,
        output_json=args.json,
        output_video=args.output_video,
        conf=args.conf,
        classes=parse_classes(args.classes),
    )


if __name__ == "__main__":
    main()