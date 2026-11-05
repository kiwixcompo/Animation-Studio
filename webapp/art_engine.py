"""
2D Vector & Stickman Art Generator Engine
Produces full-bleed 16:9 cartoon vector scenes and sticker elements
either programmatically or via Google Flow integration.
"""
import math, os, re
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080

def get_font(size: int):
    for f in ["arialbd.ttf", "segoeui.ttf", "calibrib.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except:
            continue
    return ImageFont.load_default()

def draw_stickman_char(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, expr: str = "smile"):
    r = int(45 * scale)
    color = "#0f172a"
    # Round head
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#fef3c7", outline=color, width=int(6 * scale))
    # Dot eyes
    off = int(14 * scale)
    draw.ellipse([cx - off - 3*scale, cy - 8*scale, cx - off + 3*scale, cy - 2*scale], fill=color)
    draw.ellipse([cx + off - 3*scale, cy - 8*scale, cx + off + 3*scale, cy - 2*scale], fill=color)
    # Smile
    draw.arc([cx - 16*scale, cy, cx + 16*scale, cy + 18*scale], start=0, end=180, fill=color, width=int(5*scale))
    # Body
    neck_y = cy + r
    hip_y = neck_y + int(120 * scale)
    draw.line([cx, neck_y, cx, hip_y], fill=color, width=int(7 * scale))
    # Arms & Legs
    sh_y = neck_y + int(25 * scale)
    draw.line([cx, sh_y, cx - int(55*scale), sh_y + int(45*scale)], fill=color, width=int(6*scale))
    draw.line([cx, sh_y, cx + int(55*scale), sh_y + int(45*scale)], fill=color, width=int(6*scale))
    draw.line([cx, hip_y, cx - int(40*scale), hip_y + int(110*scale)], fill=color, width=int(6*scale))
    draw.line([cx, hip_y, cx + int(40*scale), hip_y + int(110*scale)], fill=color, width=int(6*scale))

def draw_2d_vector_char(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0, pose: str = "present", outfit_color: str = "#2563eb"):
    head_w, head_h = int(38 * scale), int(48 * scale)
    # Neck & head
    draw.rectangle([cx - int(8*scale), cy + int(20*scale), cx + int(8*scale), cy + int(38*scale)], fill="#fbcfe8")
    draw.ellipse([cx - head_w, cy - head_h, cx + head_w, cy + head_h], fill="#fbcfe8", outline="#0f172a", width=int(3*scale))
    # Modern vector hair
    draw.chord([cx - head_w, cy - head_h - int(5*scale), cx + head_w, cy + int(5*scale)], start=160, end=380, fill="#1e293b")
    # Expressive eyes & brows
    draw.line([cx - int(18*scale), cy - int(10*scale), cx - int(6*scale), cy - int(8*scale)], fill="#0f172a", width=int(3*scale))
    draw.line([cx + int(6*scale), cy - int(8*scale), cx + int(18*scale), cy - int(10*scale)], fill="#0f172a", width=int(3*scale))
    draw.ellipse([cx - int(14*scale), cy - int(5*scale), cx - int(8*scale), cy + int(3*scale)], fill="#0f172a")
    draw.ellipse([cx + int(8*scale), cy - int(5*scale), cx + int(14*scale), cy + int(3*scale)], fill="#0f172a")
    draw.arc([cx - int(10*scale), cy + int(10*scale), cx + int(10*scale), cy + int(22*scale)], start=20, end=160, fill="#0f172a", width=int(3*scale))
    # Torso (styled hoodie/jacket)
    torso_top = cy + int(38 * scale)
    torso_bot = torso_top + int(140 * scale)
    draw.rounded_rectangle([cx - int(55*scale), torso_top, cx + int(55*scale), torso_bot], radius=int(18*scale), fill=outfit_color, outline="#0f172a", width=int(3*scale))
    # Pants
    draw.rounded_rectangle([cx - int(50*scale), torso_bot - int(10*scale), cx - int(10*scale), torso_bot + int(150*scale)], radius=int(10*scale), fill="#334155")
    draw.rounded_rectangle([cx + int(10*scale), torso_bot - int(10*scale), cx + int(50*scale), torso_bot + int(150*scale)], radius=int(10*scale), fill="#334155")
    # Arms
    draw.line([cx - int(45*scale), torso_top + int(30*scale), cx - int(80*scale), torso_top + int(70*scale)], fill=outfit_color, width=int(18*scale))
    draw.line([cx + int(45*scale), torso_top + int(30*scale), cx + int(90*scale), torso_top - int(10*scale)], fill=outfit_color, width=int(18*scale))
    draw.ellipse([cx + int(85*scale), torso_top - int(20*scale), cx + int(105*scale), torso_top], fill="#fbcfe8")

def generate_scene_image(shot_id: int, title: str, text: str, format_type: str, style_name: str, out_path: str):
    """
    Renders high-quality full-bleed 16:9 scene illustration.
    """
    im = Image.new("RGB", (W, H), "#0b132b")
    draw = ImageDraw.Draw(im)

    # Color themes based on style
    if "Vector" in style_name:
        bg_color = ["#0f172a", "#1e1e38", "#172554", "#111827", "#1c1917"][shot_id % 5]
        card_color = ["#1e293b", "#312e81", "#1e3a8a", "#1f2937", "#292524"][shot_id % 5]
        accent = ["#06b6d4", "#10b981", "#f59e0b", "#3b82f6", "#ec4899"][shot_id % 5]
    elif "Warm" in style_name or "Cartoon" in style_name:
        bg_color = ["#78350f", "#854d0e", "#7c2d12", "#713f12", "#9a3412"][shot_id % 5]
        card_color = ["#451a03", "#713f12", "#431407", "#3b0764", "#2e1065"][shot_id % 5]
        accent = ["#fde047", "#fb923c", "#facc15", "#fdba74", "#fef08a"][shot_id % 5]
    else:
        bg_color = ["#090d16", "#022c22", "#450a0a", "#18181b", "#0b192c"][shot_id % 5]
        card_color = ["#111827", "#064e3b", "#7f1d1d", "#27272a", "#1e3e62"][shot_id % 5]
        accent = ["#38bdf8", "#4ade80", "#f87171", "#a1a1aa", "#22d3ee"][shot_id % 5]

    draw.rectangle([0, 0, W, H], fill=bg_color)
    # Ground/floor line
    draw.rectangle([0, 740, W, H], fill=card_color)

    # Architectural Backdrop & Big Screen Display
    draw.rounded_rectangle([150, 120, 1770, 700], radius=24, fill=card_color, outline=accent, width=5)

    # Header title banner
    short_title = title[:45].upper()
    draw.text((220, 160), f"SCENE {shot_id:02d} | {short_title}", font=get_font(36), fill=accent)

    # Core sentence preview card
    clean_text = text.strip()
    words = clean_text.split()
    lines_formatted = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 55:
            lines_formatted.append(" ".join(curr))
            curr = []
    if curr:
        lines_formatted.append(" ".join(curr))

    y_pos = 260
    for l in lines_formatted[:3]:
        draw.text((220, y_pos), l, font=get_font(42), fill="#f8fafc")
        y_pos += 56

    # Graphical tech lines / data visualization on background screen
    for i in range(4):
        draw.line([220 + i*360, 520, 480 + i*360, 520], fill=accent, width=8)
        draw.line([220 + i*360, 550, 420 + i*360, 550], fill="#64748b", width=6)

    # Draw Character
    char_x = 1450 if (shot_id % 2 == 1) else 450
    char_y = 500
    if "Stickman" in format_type:
        draw_stickman_char(draw, char_x, char_y, scale=1.5)
    else:
        draw_2d_vector_char(draw, char_x, char_y, scale=1.4, outfit_color=accent)

    im.save(out_path, quality=95)

def generate_sticker_badge(element_id: int, label: str, out_path: str):
    """
    Renders clean transparent cut-out badge for overlays.
    """
    im = Image.new("RGBA", (500, 500), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Circle badge backing
    d.ellipse([30, 30, 470, 470], fill=(15, 23, 42, 235), outline=(56, 189, 248, 255), width=8)
    # Badge text
    words = label.upper().split()
    t1 = words[0] if len(words) > 0 else f"CUE {element_id}"
    t2 = words[1] if len(words) > 1 else ""
    
    d.text((120, 200), t1, font=get_font(44), fill="#38bdf8")
    if t2:
        d.text((120, 260), t2, font=get_font(38), fill="#4ade80")
    im.save(out_path)
