import yt_dlp
import os

def youtube_download(url):
    ydl_opts = {"outtmpl" : './tg-vinland/tg_vinland_bot/video.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    youtube_download('https://www.youtube.com/watch?v=2OC6ARG6fZA')