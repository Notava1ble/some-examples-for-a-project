import yt_dlp


def download_video(url, output_path="downloads/%(title)s.%(ext)s"):
    options = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    download_video(video_url)
