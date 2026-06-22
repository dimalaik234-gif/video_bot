"""
Обёртка над yt-dlp.
yt-dlp синхронный, поэтому тяжёлые операции выполняются в отдельном потоке
через run_in_executor, чтобы не блокировать event loop бота.
"""
import asyncio
import glob
import os
import shutil

import yt_dlp

from config import DOWNLOAD_DIR

# Есть ли ffmpeg в системе. Нужен для:
#  - склейки bestvideo+bestaudio (иначе максимум — «прогрессивные» потоки),
#  - конвертации аудио в MP3.
FFMPEG_AVAILABLE = shutil.which("ffmpeg") is not None

# Форматы со склейкой (если есть ffmpeg) — даёт максимальное качество
MERGE_FMT = {
    "best": "bestvideo+bestaudio/best",
    "2160": "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
    "1440": "bestvideo[height<=1440]+bestaudio/best[height<=1440]/best",
    "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "360": "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
}
# Форматы без ffmpeg — только готовые потоки с уже совмещёнными видео+аудио
SINGLE_FMT = {
    "best": "best",
    "2160": "best[height<=2160]",
    "1440": "best[height<=1440]",
    "1080": "best[height<=1080]",
    "720": "best[height<=720]",
    "480": "best[height<=480]",
    "360": "best[height<=360]",
}


def _base_opts() -> dict:
    return {
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "noplaylist": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        "ignoreerrors": False,
        "retries": 3,
        "fragment_retries": 3,
        "restrictfilenames": True,
    }


def _run_sync(opts: dict, url: str, download: bool):
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=download)


async def extract_info(url: str) -> dict:
    """Информация о ОДНОМ видео (без скачивания)."""
    opts = {**_base_opts(), "skip_download": True}
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _run_sync, opts, url, False)


async def get_playlist(url: str):
    """
    Быстрая «плоская» проверка: плейлист ли это.
    Возвращает {'title', 'urls': [...]} или None.
    """
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "nocheckcertificate": True,
    }
    loop = asyncio.get_running_loop()
    info = await loop.run_in_executor(None, _run_sync, opts, url, False)
    if not info or info.get("_type") != "playlist":
        return None

    urls = []
    for e in (info.get("entries") or []):
        if not e:
            continue
        u = e.get("url") or ""
        if u and not u.startswith("http"):
            # некоторые экстракторы возвращают «голый» ID
            ie = (e.get("ie_key") or "").lower()
            if ie.startswith("youtube") or len(u) == 11:
                u = "https://www.youtube.com/watch?v=" + u
        if u.startswith("http"):
            urls.append(u)
        elif e.get("webpage_url"):
            urls.append(e["webpage_url"])

    if not urls:
        return None
    return {"title": info.get("title") or "Playlist", "urls": urls}


def _unique_template():
    import secrets

    uid = secrets.token_hex(8)
    template = os.path.join(str(DOWNLOAD_DIR), uid + ".%(ext)s")
    return template, uid


def _download_sync(url: str, quality: str, audio_only: bool, hook):
    template, uid = _unique_template()
    opts = {**_base_opts(), "outtmpl": template, "progress_hooks": [hook]}

    if audio_only:
        opts["format"] = "bestaudio/best"
        if FFMPEG_AVAILABLE:
            opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ]
    else:
        if FFMPEG_AVAILABLE:
            opts["format"] = MERGE_FMT.get(quality, MERGE_FMT["best"])
            opts["merge_output_format"] = "mp4"
        else:
            opts["format"] = SINGLE_FMT.get(quality, SINGLE_FMT["best"])

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Находим итоговый файл
    filepath = None
    if isinstance(info, dict):
        rd = info.get("requested_downloads")
        if rd and isinstance(rd, list) and rd[0].get("filepath"):
            filepath = rd[0]["filepath"]
    if not filepath:
        matches = glob.glob(os.path.join(str(DOWNLOAD_DIR), uid + ".*"))
        if matches:
            filepath = max(matches, key=os.path.getsize)
    return filepath, info


async def download_with_progress(url, quality, audio_only, status_cb=None):
    """
    Скачивание с живым прогрессом.
    status_cb(progress: dict) — корутина, вызывается раз в ~2.5 сек.
    Возвращает (filepath, info). Кидает исключение при ошибке.
    """
    progress = {"percent": 0.0, "speed": "", "eta": "", "phase": "download"}

    def hook(d):
        st = d.get("status")
        if st == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            done = d.get("downloaded_bytes") or 0
            if total:
                progress["percent"] = min(100.0, done / total * 100)
            progress["speed"] = (d.get("_speed_str") or "").strip()
            progress["eta"] = (d.get("_eta_str") or "").strip()
        elif st == "finished":
            progress["percent"] = 100.0
            progress["phase"] = "convert"

    loop = asyncio.get_running_loop()
    fut = loop.run_in_executor(None, _download_sync, url, quality, audio_only, hook)

    while not fut.done():
        if status_cb is not None:
            try:
                await status_cb(progress)
            except Exception:
                pass
        await asyncio.sleep(2.5)

    return await fut


async def download_subtitles(url: str):
    """Скачивает доступные субтитры (ru/en). Возвращает список путей к файлам."""
    template, uid = _unique_template()
    opts = {
        **_base_opts(),
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["ru", "en"],
        "subtitlesformat": "best",
        "outtmpl": template,
    }
    loop = asyncio.get_running_loop()

    def _run():
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        return glob.glob(os.path.join(str(DOWNLOAD_DIR), uid + "*"))

    return await loop.run_in_executor(None, _run)


def cleanup(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
