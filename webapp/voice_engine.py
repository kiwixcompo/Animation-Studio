"""
Robust Microsoft Edge Neural TTS Client with DNS Fallback
Ported from Voiceover_Generator with full vocal catalog & parameter controls.
"""
import asyncio, csv, os, re, socket, subprocess
from typing import List, Dict, Optional

# Reliable DNS resolution bypass for edge-tts in restrictive/local network setups
ORIG_GETADDRINFO = socket.getaddrinfo
def patched_getaddrinfo(host, port, *args, **kwargs):
    if host and "speech.platform.bing.com" in str(host):
        # Microsoft Edge Speech IP bypass
        return ORIG_GETADDRINFO("150.171.27.10", port, *args, **kwargs)
    return ORIG_GETADDRINFO(host, port, *args, **kwargs)

socket.getaddrinfo = patched_getaddrinfo

import edge_tts

# Comprehensive curated voice list matching Voiceover_Generator
CURATED_VOICES = [
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (Authoritative)",
        "gender": "Male",
        "accent": "American",
        "category": "Documentary / Explainer",
        "badge": "Executive Narrator"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy (Professional)",
        "gender": "Male",
        "accent": "American",
        "category": "Broadcaster / News",
        "badge": "Pro News"
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny (Natural Warm)",
        "gender": "Female",
        "accent": "American",
        "category": "Warm / Conversational",
        "badge": "Popular"
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria (Expressive)",
        "gender": "Female",
        "accent": "American",
        "category": "Storytelling / Cinematic",
        "badge": "Expressive"
    },
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan (British Cinematic)",
        "gender": "Male",
        "accent": "British",
        "category": "Cinematic / Trailer",
        "badge": "Cinematic"
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (British Natural)",
        "gender": "Female",
        "accent": "British",
        "category": "Sophisticated / BBC Style",
        "badge": "British RP"
    },
    {
        "id": "en-AU-NatashaNeural",
        "name": "Natasha (Australian)",
        "gender": "Female",
        "accent": "Australian",
        "category": "Engaging / Friendly",
        "badge": "Aussie Friendly"
    },
    {
        "id": "hi-IN-MadhurNeural",
        "name": "Madhur (Hindi Natural Male)",
        "gender": "Male",
        "accent": "Hindi",
        "category": "Hindi Explainer",
        "badge": "Hindi Pro"
    },
    {
        "id": "hi-IN-SwaraNeural",
        "name": "Swara (Hindi Expressive Female)",
        "gender": "Female",
        "accent": "Hindi",
        "category": "Hindi Storytelling",
        "badge": "Hindi Warm"
    }
]

def get_voice_catalog() -> List[Dict]:
    return CURATED_VOICES

async def synthesize_speech(text: str, voice: str, out_wav_path: str, rate: str = "+0%", pitch: str = "+0Hz", volume: str = "+0%"):
    temp_mp3 = out_wav_path + ".temp.mp3"
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(temp_mp3)
    
    # Standardize to 24000Hz mono wav for ffmpeg/alignment
    cmd = [
        "ffmpeg", "-y", "-i", temp_mp3,
        "-ar", "24000", "-ac", "1",
        out_wav_path, "-loglevel", "error"
    ]
    subprocess.run(cmd, check=True)
    if os.path.exists(temp_mp3):
        os.remove(temp_mp3)

def generate_voice_takes(lines_file: str, out_dir: str, voice: str = "en-US-ChristopherNeural", rate: str = "+0%", pitch: str = "+0Hz", progress_callback=None):
    os.makedirs(out_dir, exist_ok=True)
    with open(lines_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    
    total = len(rows)
    for idx, r in enumerate(rows):
        lid = r["id"]
        text = r["text"]
        out_wav = os.path.join(out_dir, f"{lid}.wav")
        asyncio.run(synthesize_speech(text, voice, out_wav, rate=rate, pitch=pitch))
        if progress_callback:
            progress_callback(idx + 1, total, f"Generated voice take {lid}/{total}")
    return rows
