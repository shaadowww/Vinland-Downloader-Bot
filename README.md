[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-orange?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Poetry](https://img.shields.io/badge/Poetry-2.0+-blueviolet?logo=poetry&logoColor=white)](https://python-poetry.org/)
[![Redis](https://img.shields.io/badge/redis-%23DC382D.svg?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/downloads/)

## Vinland Downloader — Media Extraction Bot

Vinland Downloader is a high-performance, asynchronous Telegram bot designed to extract and convert media from YouTube and SoundCloud seamlessly. Inspired by the relentless spirit of voyagers, the bot cuts through platform restrictions, tracking scripts, and bloated web interfaces to deliver raw, high-quality audio and video files directly to your chat.
### Features

    Dual-Mode Extraction: Download full-resolution video streams or extract high-bitrate audio tracks.

    Multi-Platform Support: Fully compatible with YouTube and SoundCloud architectures.

    Zero Bloat: No advertisements, no paywalls, just immediate delivery.

### The Tech Stack

The backend architecture is built from the ground up for speed, concurrency, and reliability:

    Core Engine: Asynchronous Python 3 utilizing modern concurrency paradigms to handle multiple download streams simultaneously without blocking the event loop.

    API & Bot Framework: Built on top of a robust asynchronous framework (Aiogram / FastAPI) to ensure sub-second response times and stable webhook/polling connections.

    Media Processing: Powered by optimized yt-dlp integration for reliable bypassing of platform rate limits and precise audio extraction.

    Infrastructure & Deployment: Hosted on AWS (Amazon Web Services) utilizing scalable cloud instances to ensure maximum uptime, high bandwidth, and efficient temporary file storage during processing.

    Data Management: PostgreSQL backend managed via SQLAlchemy for secure user state tracking and queue management.