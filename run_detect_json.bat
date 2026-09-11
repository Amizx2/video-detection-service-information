@echo off
chcp 65001 >nul

:: ================================
:: Настройка чувствительности детектора
:: Значение от 0.0 до 1.0
:: Меньше — более чувствительный (ловит слабые объекты)
:: Больше — менее чувствительный (только уверенные объекты)
:: ================================
set CONF=0.25

echo ================================
echo Запуск YOLO-детектора
echo Видео с рамками + JSON-разметка
echo Минимальная уверенность (conf): %CONF%
echo ================================
echo.

py detect_to_json.py ^
  --model runs/detect/train/weights/best.pt ^
  --input input/video.mp4 ^
  --json output/annotations.json ^
  --output-video output/marked_video.mp4 ^
  --conf %CONF%

if errorlevel 1 (
  echo.
  echo ОШИБКА: скрипт не выполнился.
  echo Проверь сообщение об ошибке выше.
  echo.
  pause
  exit /b 1
)

echo.
echo Готово.
echo JSON сохранён сюда:
echo output/annotations.json
echo.
echo Видео с рамками сохранено сюда:
echo output/marked_video.mp4
echo.

pause