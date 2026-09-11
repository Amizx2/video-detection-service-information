@echo off
chcp 65001 nul

echo Запуск удаления объектов через YOLO...

python process_video.py ^
  --model runsdetecttrainweightsbest.pt ^
  --input inputvideo.mp4 ^
  --output outputremoved_video.mp4 ^
  --conf 0.25 ^
  --remove ^
  --remove-mode inpaint

echo.
echo Готово. Видео с удалёнными объектами сохранено в outputremoved_video.mp4
pause