import yt_dlp
import os

FFMPEG_PATH = os.path.join("C:", os.sep, "ffmpeg", "bin", "ffmpeg.exe")
DENO_PATH = os.path.join("C:", os.sep, "Deno", "deno.exe")

def youtube_download(url, audio = False):
    ydl_opts = {
        "js_runtimes": {
            "deno": {
                "path" : DENO_PATH
            }
        },
        "ffmpeg_location": FFMPEG_PATH,
        "quiet": False,
        "nonplaylist": True,
        "outtmpl" : "tg-vinland/bot/%(title)s.%(ext)s",
    }

    if audio:
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })

    else:
        ydl_opts.update({
            "format": "bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
        })
    

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    youtube_download("https://www.youtube.com/watch?v=2OC6ARG6fZA", audio=True)