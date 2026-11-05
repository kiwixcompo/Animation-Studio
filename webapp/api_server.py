"""
Local Studio API Server
Bridges the webapp frontend with local execution:
- Google Flow status diagnostics (via `flow-auto status --site flow --json` and direct bridge query)
- Triggers image/element generation live on Google Flow
- Generates Microsoft Edge Neural voiceover
- Renders full 1080p MP4 animations
"""
import os
import sys
import json
import subprocess
import threading
from typing import Optional, List
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Animation Studio Local Bridge Server")

# Allow CORS from any origin (local WAMP, Netlify, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global task state for live tracking in UI
CURRENT_JOB = {
    "status": "idle",
    "step": "",
    "progress": 0,
    "flow_active": False,
    "flow_prompt": "",
    "logs": [],
    "video_url": "",
    "error": None
}

class GenerateRequest(BaseModel):
    title: str
    script: str
    format: str = "2D Animated Video (Full Cartoon & Motion Design)"
    art_style: str = "Modern Flat Vector (Kurzgesagt / Infographics Show)"
    voice: str = "en-US-ChristopherNeural"
    use_flow: bool = True

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/flow-status")
def get_flow_status():
    """
    Checks exact status of Google Flow connector via flow-auto CLI & Port 8791 bridge.
    """
    result = {
        "bridge": False,
        "extension": False,
        "logged_in": False,
        "tab_visible": False,
        "side_panel_open": False,
        "plan": "unknown",
        "limits": {},
        "message": ""
    }
    
    # 1. Run doctor via cmd.exe /c flow-auto
    try:
        flow_cmd = "flow-auto.cmd" if os.name == "nt" else "flow-auto"
        res = subprocess.run([flow_cmd, "doctor", "--site", "flow", "--json"], shell=True, capture_output=True, text=True, timeout=8)
        raw = res.stdout
        if "[" in raw and "]" in raw:
            json_str = raw[raw.find("["):raw.rfind("]")+1]
            checks = json.loads(json_str)
            for c in checks:
                name = c.get("name", "")
                state = c.get("state", "")
                detail = c.get("detail", "")
                if name == "Bridge" and state == "ok":
                    result["bridge"] = True
                elif name == "Extension" and state == "ok":
                    result["extension"] = True
                elif name == "Signed in" and state == "ok":
                    result["logged_in"] = True
                elif name == "Tab visible":
                    result["tab_visible"] = (state == "ok")
                elif name == "Queue":
                    result["side_panel_open"] = (state == "ok")
                elif name == "Plan":
                    result["plan"] = detail
    except Exception as e:
        result["message"] = f"Doctor check error: {e}"

    # 2. Check directly via bridge port 8791 as secondary confirmation
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:8791/status?site=flow", timeout=2) as response:
            bridge_data = json.loads(response.read().decode("utf-8"))
            if bridge_data.get("bridge") == "up":
                result["bridge"] = True
            if bridge_data.get("extensionConnected"):
                result["extension"] = True
            if bridge_data.get("loggedIn"):
                result["logged_in"] = True
            if bridge_data.get("limits"):
                result["limits"] = bridge_data.get("limits")
    except Exception:
        pass

    return result

def run_production_pipeline(req: GenerateRequest):
    global CURRENT_JOB
    CURRENT_JOB["status"] = "running"
    CURRENT_JOB["progress"] = 5
    CURRENT_JOB["logs"] = ["Production started..."]
    CURRENT_JOB["error"] = None
    CURRENT_JOB["video_url"] = ""

    def log(msg: str, progress: int = None):
        CURRENT_JOB["logs"].append(msg)
        CURRENT_JOB["step"] = msg
        if progress is not None:
            CURRENT_JOB["progress"] = progress
        print(f"[{CURRENT_JOB['progress']}%] {msg}")

    try:
        slug = "".join([c.lower() if c.isalnum() else "-" for c in req.title])[:30].strip("-")
        project_dir = os.path.join(os.path.expanduser("~"), "StickmanHybrid", slug)
        os.makedirs(project_dir, exist_ok=True)
        
        # Step 1: Script Parsing
        log("Parsing script into timed explainer lines...", 15)
        raw_lines = [l.strip() for l in req.script.splitlines() if l.strip() and not l.startswith("#")]
        import re, csv
        processed_lines = []
        for line in raw_lines:
            for c in re.split(r'(?<=[.?!])\s+', line):
                c = c.strip()
                if c:
                    processed_lines.append(c)
                    
        lines_tsv = os.path.join(project_dir, "LINES.tsv")
        with open(lines_tsv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "text", "gap"], delimiter="\t")
            writer.writeheader()
            for idx, text in enumerate(processed_lines, start=1):
                writer.writerow({"id": str(idx), "text": text, "gap": "0.35"})
                
        # Step 2: Voiceover synthesis
        log(f"Synthesizing voiceover with Edge Neural ({req.voice})...", 30)
        takes_dir = os.path.join(project_dir, "takes")
        os.makedirs(takes_dir, exist_ok=True)
        
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from voice_engine import generate_voice_takes
        generate_voice_takes(lines_tsv, takes_dir, voice=req.voice, rate="+0%", pitch="+0Hz")
        
        # vo_join
        vo_join_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "vox-doc-sound", "scripts", "vo_join.py"))
        subprocess.run(["python", vo_join_script, "takes", "LINES.tsv"], cwd=project_dir, check=True)
        
        # Step 3: Google Flow or Local Art Generation
        img_dir = os.path.join(project_dir, "img")
        elements_dir = os.path.join(project_dir, "elements", "cut")
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(elements_dir, exist_ok=True)
        
        # Generate word timing WORDS.tsv
        from pipeline import VideoPipeline
        vp = VideoPipeline(project_dir)
        vp._generate_words_tsv()
        
        total_scenes = len(processed_lines)
        scene_rows = []
        
        for idx, text in enumerate(processed_lines, start=1):
            pct = 40 + int((idx / total_scenes) * 40)
            log(f"Generating visual scene {idx}/{total_scenes}: '{text[:40]}...'", pct)
            
            shot_name = f"s{idx:02d}.jpg"
            shot_path = os.path.join(img_dir, shot_name)
            elem_name = f"{idx}.png"
            elem_path = os.path.join(elements_dir, elem_name)
            
            # If use_flow is selected, submit directly to Flow Connector
            if req.use_flow:
                CURRENT_JOB["flow_active"] = True
                CURRENT_JOB["flow_prompt"] = f"{req.art_style} style: {text}"
                try:
                    # Submit scene to flow-auto
                    flow_cmd = [
                        "flow-auto", "generate", "create", "flow-text-to-image",
                        "--prompt", f"16:9 widescreen, {req.art_style} aesthetic illustration of: {text}",
                        "--aspect-ratio", "16:9",
                        "--model", "nano-banana-2",
                        "--folder", f"flow_{slug}",
                        "--index", str(idx)
                    ]
                    log(f"Submitting Scene {idx} to Google Flow tab in browser...", pct)
                    subprocess.run(flow_cmd, capture_output=True, text=True, timeout=15)
                except Exception as fe:
                    print(f"Flow submission warning: {fe}")
                CURRENT_JOB["flow_active"] = False
            
            # Always ensure an asset exists (art_engine acts as immediate render or fallback)
            from art_engine import generate_scene_image, generate_sticker_badge
            generate_scene_image(idx, req.title, text, req.format, req.art_style, shot_path)
            first_w = text.split()[0] if text.split() else f"KEY{idx}"
            generate_sticker_badge(idx, first_w, elem_path)
            
            scene_rows.append({"cue": f"{idx}.0", "img": f"img/{shot_name}", "text": "", "pos": "", "extra": ""})
            scene_rows.append({"cue": f"+{idx}.4", "img": f"elements/cut/{elem_name}", "text": "", "pos": "0.8,0.3,0.35", "extra": "pop"})

        # Write SCENES.tsv
        scenes_tsv = os.path.join(project_dir, "SCENES.tsv")
        with open(scenes_tsv, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["cue", "img", "text", "pos", "extra"], delimiter="\t")
            writer.writeheader()
            writer.writerows(scene_rows)
            
        # Step 4: Render Video
        log("Compositing 1080p MP4 explainer video...", 85)
        final_mp4 = vp.render_final_video()
        
        # Copy to sample directory for instant web preview
        web_sample_dir = os.path.join(os.path.dirname(__file__), "sample")
        os.makedirs(web_sample_dir, exist_ok=True)
        dest_mp4 = os.path.join(web_sample_dir, "latest_render.mp4")
        shutil.copy2(final_mp4, dest_mp4)
        
        log("Explainer video render complete!", 100)
        CURRENT_JOB["status"] = "done"
        CURRENT_JOB["video_url"] = "sample/latest_render.mp4"
    except Exception as e:
        import traceback
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"Pipeline error: {err_msg}")
        CURRENT_JOB["status"] = "error"
        CURRENT_JOB["error"] = str(e)
        CURRENT_JOB["logs"].append(f"Error: {e}")

@app.post("/api/generate")
def start_generation_endpoint(req: GenerateRequest, background_tasks: BackgroundTasks):
    global CURRENT_JOB
    if CURRENT_JOB["status"] == "running":
        raise HTTPException(status_code=400, detail="A job is already running.")
    
    background_tasks.add_task(run_production_pipeline, req)
    return {"status": "started", "message": "Video production initiated."}

@app.get("/api/job-status")
def get_job_status():
    global CURRENT_JOB
    return CURRENT_JOB

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="127.0.0.1", port=8000, reload=False)
