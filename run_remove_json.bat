@echo off
chcp 65001 >nul

echo Запуск удаления объектов по JSON-разметке...
echo.

py remove_from_json.py ^
  --input input/video.mp4 ^
  --json output/annotations.json ^
  --output output/removed_video.mp4 ^
  --mode inpaint ^
  --padding 10 ^
  --min-conf 0.25

echo.
echo Готово.
echo Видео после удаления: output/removed_video.mp4
echo.

pause