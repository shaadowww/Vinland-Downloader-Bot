import yt_dlp
import os

FFMPEG_PATH = os.path.join("C:", os.sep, "ffmpeg", "bin", "ffmpeg.exe")
DENO_PATH = os.path.join("C:", os.sep, "Deno", "deno.exe")

output_dir = 'downloads'
os.makedirs(output_dir, exist_ok=True)
# dir_path = os.path.dirname(os.path.realpath(__file__))

def youtube_download(url, audio = False):
    ydl_opts = {
        "quiet": True,
        "max_filesize": 50 * 1024 * 1025,
        "noplaylist": True,
        "outtmpl" : f"{output_dir}/%(title)s.%(ext)s",
    }
    
    if os.path.exists(FFMPEG_PATH):
        ydl_opts.update({
            "ffmpeg_location": FFMPEG_PATH,
        })

    if os.path.exists(DENO_PATH):
        ydl_opts.update({
            "js_runtimes": {
                "deno": {
                    "path" : DENO_PATH
                }
            },
        })

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
            "format": "bestvideo[ext=m4a]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
        })
    

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

        file_path = ydl.prepare_filename(info)

        if audio:
            file_path = os.path.splitext(file_path)[0] + ".mp3"
        
        return file_path

if __name__ == "__main__":
    youtube_download(
        "https://www.youtube.com/watch?v=2OC6ARG6fZA",
        audio=True
    )