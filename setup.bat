Rem install python dependencies
Rem ffmpeg, ffprobe, tweepy, dotenv
echo Installing python dependencies
@echo off
pip install ffmpeg-python
pip install ffprobe-python
pip install tweepy
pip install python-dotenv
@echo on

echo Complete. Please restart your terminal to ensure all changes are applied. You may also need to add ffmpeg & ffprobe to your PATH variable.
pause