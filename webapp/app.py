"""
Animation Studio Web App (Streamlit)
Visual, intuitive UI to generate 2D Cartoon and Stickman Explainer MP4 videos
using free Microsoft Edge Neural TTS, Google Flow Connector, and the reverse-engineered render pipeline.
"""
import os, sys, time, shutil
import streamlit as st

# Configure page layout and style
st.set_page_config(
    page_title="Animation Hybrid Studio (2D & Stickman)",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from voice_engine import get_voice_catalog
from flow_client import FlowClient
from pipeline import VideoPipeline

# Custom styling for a polished creative studio feel
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎬 Animation Studio: 2D Cartoon & Stickman Explainer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Create high-impact, word-timed documentary explainers powered by free Microsoft Edge Neural Voices and Google Flow.</div>', unsafe_allow_html=True)

# Sidebar: System Health & Provider Status
with st.sidebar:
    st.header("⚡ System & Integrations")
    
    flow_client = FlowClient()
    flow_status = flow_client.check_status()
    
    st.subheader("Google Flow Connector")
    if flow_status["ready"]:
        st.success("🟢 Flow Connector: Connected & Ready")
    else:
        st.warning("🟡 Flow Connector: Standby / Bridge")
        with st.expander("Connector Details"):
            st.code(flow_status["message"] or "Extension or Bridge waiting for connection")
            if st.button("Start Flow Bridge"):
                if flow_client.start_bridge():
                    st.info("Bridge daemon started.")
                time.sleep(1)
                st.rerun()

    st.subheader("Voiceover Engine")
    st.success("🟢 Microsoft Edge Neural TTS: Active (Free Cloud HD)")
    st.caption("Zero cost, studio-grade voices with natural cadence.")

    st.markdown("---")
    st.info("💡 **Tip**: Keep a Google Flow tab open with the Flow Connector extension logged in to enable AI cloud generation.")

# Main Form Area
col_left, col_right = st.columns([1.1, 0.9])

with col_left:
    st.subheader("1. Project Details & Style")
    
    title = st.text_input("Video Title / Topic", value="Why Remote Work Is Reshaping Cities", placeholder="Enter the topic or title of your video...")
    
    c1, c2 = st.columns(2)
    with c1:
        video_format = st.selectbox(
            "Video Format",
            ["2D Animated Video (Full Cartoon & Motion Design)", "Stickman Video (Classic Stick Figure Explainer)"],
            index=0
        )
    with c2:
        if "2D" in video_format:
            art_style = st.selectbox(
                "2D Cartoon Art Style",
                [
                    "Modern Flat Vector (Kurzgesagt / Infographics Show)",
                    "Classic Hand-Drawn 2D Cartoon (Disney / Storybook)",
                    "Cinematic Graphic Novel (Bold Comic Contrast)",
                    "Stylized Anime / Chibi (Dynamic & Expressive)"
                ],
                index=0
            )
        else:
            art_style = st.selectbox(
                "Stickman Color Look",
                ["Bright Flat Cartoon (Default)", "Warm Amber Paper (Ancient / History)", "Ink on White (Numbers & Stats)", "Night Palette (Deep Blue Mystery)"],
                index=0
            )

    st.subheader("2. Script & Narration")
    default_script = """This morning, millions of professionals opened their laptops from thousands of miles away.
Office skyscrapers in major metropolitan centers suddenly stand half empty.
Economists call it the greatest geographical workforce shift in modern history.
When location no longer dictates talent, local housing markets and downtown economies completely transform.
Are major cities dying, or are they simply being reborn into something entirely new?"""
    
    user_script = st.text_area(
        "Voiceover Script (Sentences or paragraphs will be automatically timed to beats)",
        value=default_script,
        height=180
    )

with col_right:
    st.subheader("3. Voiceover Generator (Edge Neural)")
    
    voice_catalog = get_voice_catalog()
    voice_options = {f"{v['name']} — {v['accent']} ({v['badge']})": v['id'] for v in voice_catalog}
    
    selected_voice_label = st.selectbox(
        "Select Narrator Voice",
        list(voice_options.keys()),
        index=0
    )
    selected_voice_id = voice_options[selected_voice_label]
    
    vcol1, vcol2 = st.columns(2)
    with vcol1:
        rate_val = st.slider("Speech Rate / Speed", min_value=-30, max_value=30, value=0, step=5, format="%d%%")
        rate_str = f"{rate_val:+d}%"
    with vcol2:
        pitch_val = st.slider("Voice Pitch", min_value=-20, max_value=20, value=0, step=5, format="%dHz")
        pitch_str = f"{pitch_val:+d}Hz"
        
    st.subheader("4. Production Mode")
    prod_mode = st.radio(
        "Visual Generation Method",
        [
            "⚡ High-Speed Built-in Cartoon Vector Engine (Instant & 100% Free)",
            "🌐 Google Flow Cloud Generator (Requires logged-in Flow tab with extension)"
        ],
        index=0
    )

# Execution Button & Progress
st.markdown("---")
create_btn = st.button("🚀 Render & Export Explainer Video (MP4)", type="primary", use_container_width=True)

if create_btn:
    if not title.strip() or not user_script.strip():
        st.error("Please provide both a Title and a Script to begin production.")
    else:
        slug = "".join([c.lower() if c.isalnum() else "-" for c in title])[:30].strip("-")
        project_dir = os.path.join(os.path.expanduser("~"), "StickmanHybrid", slug)
        
        pipeline = VideoPipeline(project_dir)
        
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        try:
            # Step 1: Parse Script
            status_box.info("📝 Parsing script lines and pacing beats...")
            lines = pipeline.prepare_script_lines(user_script, title)
            progress_bar.progress(15)
            time.sleep(0.5)
            
            # Step 2: Voice Synthesis with Edge Neural
            status_box.info(f"🎙️ Generating studio-quality voiceover with {selected_voice_id}...")
            pipeline.generate_voiceover(
                voice_id=selected_voice_id,
                rate=rate_str,
                pitch=pitch_str,
                callback=lambda cur, tot, msg: status_box.info(f"🎙️ Voiceover: {msg}")
            )
            progress_bar.progress(45)
            
            # Step 3: Visual Scenes & Stickers Generation
            status_box.info(f"🎨 Generating 16:9 full-bleed {video_format} scenes and cut-out overlays...")
            pipeline.generate_visual_assets(
                title=title,
                format_type=video_format,
                style_name=art_style,
                callback=lambda cur, tot, msg: status_box.info(f"🎨 Visuals: {msg}")
            )
            progress_bar.progress(75)
            
            # Step 4: Video Compositing & Final MP4 Render
            status_box.info("🎬 Compositing word-timed audio, animated sticker pops, and scenes into MP4...")
            final_mp4 = pipeline.render_final_video()
            progress_bar.progress(100)
            
            status_box.success("🎉 Video successfully produced and ready!")
            
            # Display Results and Download
            st.balloons()
            st.subheader("📹 Video Preview & Download")
            
            p_col1, p_col2 = st.columns([1.2, 0.8])
            with p_col1:
                st.video(final_mp4)
            with p_col2:
                st.markdown(f"**File Location:** `{final_mp4}`")
                file_size_mb = os.path.getsize(final_mp4) / (1024 * 1024)
                st.markdown(f"**Size:** `{file_size_mb:.2f} MB`")
                with open(final_mp4, "rb") as f:
                    st.download_button(
                        label="⬇️ Download MP4 Video",
                        data=f,
                        file_name=f"{slug}.mp4",
                        mime="video/mp4",
                        type="primary",
                        use_container_width=True
                    )
        except Exception as e:
            status_box.error(f"Render failed: {str(e)}")
            st.exception(e)
