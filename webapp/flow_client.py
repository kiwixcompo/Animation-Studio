"""
Google Flow Integration Client
Interfaces with the Flow Connector extension through `flow-auto` CLI.
"""
import json, os, re, shutil, subprocess
from typing import Dict, List, Optional, Tuple

class FlowClient:
    def __init__(self, port: int = 8791):
        self.port = port

    def check_status(self) -> Dict[str, bool]:
        """
        Check if flow-auto doctor reports Node, bridge and browser extension connected.
        """
        status = {
            "cli_installed": False,
            "bridge_running": False,
            "extension_connected": False,
            "ready": False,
            "message": ""
        }
        try:
            res = subprocess.run(["flow-auto", "doctor", "--site", "flow"], capture_output=True, text=True, timeout=8)
            status["cli_installed"] = True
            output = res.stdout + res.stderr
            status["bridge_running"] = "FAIL  Bridge" not in output
            status["extension_connected"] = "FAIL  Extension" not in output
            status["ready"] = status["bridge_running"] and status["extension_connected"]
            status["message"] = output.strip()
        except FileNotFoundError:
            status["message"] = "flow-auto CLI not found in PATH."
        except Exception as e:
            status["message"] = str(e)
        return status

    def start_bridge(self) -> bool:
        """Starts flow-auto bridge in the background if not active."""
        try:
            subprocess.Popen(["flow-auto", "bridge", "start"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def submit_scene_job(self, prompt: str, index: int, download_folder: str, ref_image: Optional[str] = None) -> bool:
        """
        Submits a single scene generation prompt to Google Flow via flow-auto.
        """
        cmd = [
            "flow-auto", "generate", "create", "flow-text-to-image",
            "--prompt", prompt,
            "--aspect-ratio", "16:9",
            "--model", "nano-banana-2",
            "--folder", download_folder,
            "--index", str(index)
        ]
        if ref_image and os.path.exists(ref_image):
            cmd.extend(["--image", ref_image])
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            return res.returncode == 0
        except Exception as e:
            print(f"Error submitting Flow job {index}: {e}")
            return False

    def submit_element_job(self, prompt: str, index: int, download_folder: str) -> bool:
        """
        Generates cut-out sticker element on solid magenta backdrop (1:1 aspect ratio).
        """
        magenta_prompt = f"{prompt}, isolated centered object sticker on pure solid flat magenta backdrop (#ff00ff), no shadow, crisp clean edges, 1:1"
        cmd = [
            "flow-auto", "generate", "create", "flow-text-to-image",
            "--prompt", magenta_prompt,
            "--aspect-ratio", "1:1",
            "--model", "nano-banana-2",
            "--folder", f"{download_folder}_el",
            "--index", str(index)
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
            return res.returncode == 0
        except Exception as e:
            print(f"Error submitting Flow element {index}: {e}")
            return False
