---
name: stickman-hybrid
description: Make a complete explainer video in the HYBRID look (Stickman OR full 2D Animation), end to end: clean full-colour scene pictures (Google Flow, Nano Banana 2) with cut-out stickers that pop in on the spoken words, animated counters and paper collage beats, in the style of viral explainer channels. Supports both classic Stickman videos and full 2D Animated videos (Modern Flat Vector, Classic Hand-Drawn Cartoon, Graphic Novel, Anime/Chibi). Powered by free Microsoft Edge Neural TTS voices (Christopher, Guy, Jenny, Aria, Ryan, Sonia, Madhur, Swara) and Google Flow connector. Use when the user says "stickman hybrid", "hybrid stickman", "stickman sticker video", "2d animation", "stickman hybrid start", "animation start", "web app", or opens the animation folder.
---

# Animation Hybrid Studio: Stickman & 2D Cartoon Explainer

You make the whole video for the user, either through the **Interactive Web Studio** or directly via CLI/chat commands.

## Standard Voice Engine Default: Microsoft Edge Neural TTS
- **Voice Engine**: Microsoft Edge Neural TTS (`edge-tts`) is the permanent, default voice engine across all projects.
- **Cost**: 100% Free, zero server cost, no API keys or limits.
- **Narrators**: 
  - English: `en-US-ChristopherNeural` (Default authoritative documentary voice), `en-US-GuyNeural`, `en-US-JennyNeural`, `en-US-AriaNeural`, `en-GB-RyanNeural`, `en-GB-SoniaNeural`.
  - Hindi & Indian Languages: `hi-IN-MadhurNeural` (Default clear Hindi voice), `hi-IN-SwaraNeural`.
- Voice takes are generated directly via `webapp/voice_engine.py` using standard 24000Hz mono wave format with word-level forced alignment.

## Web Application Studio
- A full visual Web Application is available at: **`http://localhost:8501`**
- Launcher script: `webapp/run_studio.bat`
- Features:
  - Visual selector for **2D Animated Cartoon Video** vs **Stickman Video**.
  - Style selector: Modern Flat Vector (Kurzgesagt aesthetic), Storybook 2D Cartoon, Graphic Novel, Anime/Chibi.
  - Custom script box with automatic pacing line subdivision.
  - Voice dropdown and tuning controls (speech rate, pitch).
  - Google Flow extension status check and generation controls.
  - Direct video player with single-click MP4 file download.

## Google Flow Prerequisite
- User keeps a Google Flow tab open (`flow.google.com`) logged into their Google account with the Flow Connector browser extension active.
- `flow-auto doctor --site flow` monitors extension and bridge status.
