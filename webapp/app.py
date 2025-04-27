import os
import re
import shutil
import traceback
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Disable Streamlit file watcher to avoid Torch path issues
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# Ensure project root is on the import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from webapp.services.parsing.mei_parser import parse_mei_for_editor
from webapp.services.parsing.ds_builder import build_ds_from_notes
from webapp.services.parsing.ds_validator import validate_ds
from webapp.services.phonemes.phoneme_dict import PHONEMES as permitted_phonemes
from inference.pipeline import run_inference

# Directories
UPLOAD_MEI_DIR = PROJECT_ROOT / "webapp/uploaded_mei"
UPLOAD_DS_DIR = PROJECT_ROOT / "webapp/uploaded_ds"
TMP_DS_DIR = PROJECT_ROOT / "webapp/tmp_ds"
OUTPUT_DIR = PROJECT_ROOT / "webapp/output"
for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Page config
st.set_page_config(page_title="CantusSVS", layout="wide")

# Title
st.title("CantusSVS: Latin Singing Voice Synthesis")

# Styling tweaks
st.markdown("""
    <style>
    html, body, [class*="css"]  { font-size: 18px !important; }
    div[data-testid="stSelectbox"] label, div[data-testid="stNumberInput"] label,
    div[data-testid="stTextInput"] label { font-size: 13px; padding-bottom: 0px; }
    div[data-testid="stSlider"] label { font-size: 0px; }
    button[kind="secondary"] { height: 32px; width: 32px; padding: 0px; font-size: 20px; margin-top: 5px; }
    div.stButton > button:first-child { background-color: #28a745; color: white; font-size: 18px; height: 50px; width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# Intro text
st.markdown("""
# Welcome to CantusSVS

CantusSVS lets you synthesize singing voice from musical scores using the DiffSinger system.

---

### What this app does
- Upload a **MEI** file and edit phonemes if needed
- Or upload a prepared **DS** (DiffSinger) file

### How to use it
1. Select MEI or DS
2. Upload or use demo MEI
3. Edit phonemes (optional)
4. Click Confirm & Synthesize

---
""")

# Input type selector
filetype = st.selectbox("Select file type:", ["MEI", "DS"], help="**MEI**: Music Encoding Initiative\n\n**DS**: DiffSinger format")

def handle_exception(context_message):
    st.error(f"{context_message}. See console for details.")
    print("\n" + "="*30)
    print(f"Exception during {context_message}")
    traceback.print_exc()
    print("="*30 + "\n")
    st.stop()

if filetype == "MEI":
    st.header("1. Select MEI Source")
    use_demo = st.checkbox("Use demo MEI file (CantusSVSTest.mei)", value=False)
    tempo = st.slider("Tempo (BPM)", 30, 300, 120)

    if use_demo:
        mei_path = UPLOAD_MEI_DIR / "CantusSVSTest.mei"
        if not mei_path.exists():
            st.error("Demo MEI file not found.")
            st.stop()
        with open(mei_path, "rb") as f:
            mei_file_bytes = f.read()
    else:
        mei_file = st.file_uploader("Upload your MEI file", type="mei")
        if not mei_file:
            st.stop()
        mei_path = UPLOAD_MEI_DIR / mei_file.name
        with open(mei_path, "wb") as f:
            f.write(mei_file.getbuffer())
        mei_file_bytes = mei_file.getvalue()

    mei_text = mei_file_bytes.decode("utf-8")

    try:
        raw_notes = parse_mei_for_editor(mei_path, tempo)
    except Exception:
        handle_exception("MEI parsing")

    # Build syllable groups
    syllable_groups = []
    quarter_duration = 60 / tempo
    for note in raw_notes:
        syllable_text = note["lyric"]
        pitch = note["pitch"]
        phonemes = list(syllable_text) if syllable_text else ["a"]
        syllable = []
        for ph in phonemes:
            syllable.append({"phoneme": ph if ph in permitted_phonemes else "a", "duration": note["duration"] / len(phonemes), "pitch": pitch})
        syllable_groups.append({"syllable": syllable_text, "phonemes": syllable})

    # Verovio viewer
    st.subheader("Score Preview")
    components.html(f"""
    <div class="panel-body">
        <div id="app" class="panel" style="border: 1px solid lightgray; min-height: 400px;"></div>
    </div>
    <script type="module">
        import 'https://editor.verovio.org/javascript/app/verovio-app.js';
        const app = new Verovio.App(document.getElementById("app"), {{ defaultView: 'document', documentZoom: 3 }});
        app.loadData(`{mei_text}`);
    </script>
    """, height=450)

    # Editor
    st.subheader("Edit Phonemes, Durations, and Pitches", divider="gray")
    edited_syllables = []

    for idx, group in enumerate(syllable_groups):
        st.markdown(f"##### {group['syllable'].capitalize()}")
        new_phonemes = []
        for j, ph in enumerate(group["phonemes"]):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 2, 1])
            with col1:
                phoneme = st.selectbox(f"Phoneme {idx}-{j}", permitted_phonemes, index=permitted_phonemes.index(ph["phoneme"]) if ph["phoneme"] in permitted_phonemes else 0, key=f"phoneme_{idx}_{j}")
            with col2:
                duration = st.number_input(f"Duration {idx}-{j}", min_value=0.05, max_value=5.0, value=ph["duration"], step=0.01, format="%.2f", key=f"duration_num_{idx}_{j}")
            with col3:
                duration_slider = st.slider(f"Slider {idx}-{j}", min_value=0.05, max_value=5.0, value=duration, step=0.01, key=f"duration_slider_{idx}_{j}")
            if duration_slider != duration:
                duration = duration_slider
                st.session_state[f"duration_num_{idx}_{j}"] = duration
            with col4:
                pitch = st.text_input(f"Pitch {idx}-{j}", value=ph["pitch"], key=f"pitch_{idx}_{j}")
                if not re.match(r"^[A-G][#b]?[0-8]$", pitch):
                    st.caption("⚠️ Format: C4, F#3, Bb2")
            with col5:
                if len(group["phonemes"]) > 1:
                    if st.button("❌", key=f"remove_{idx}_{j}"):
                        continue
            new_phonemes.append({"phoneme": phoneme, "duration": duration, "pitch": pitch})

        if len(new_phonemes) < 1:
            st.error("Each syllable must have at least one phoneme.")
            new_phonemes.append({"phoneme": "a", "duration": quarter_duration, "pitch": group["phonemes"][0]["pitch"]})

        if st.button("➕ Add phoneme", key=f"add_{idx}"):
            new_phonemes.append({"phoneme": "a", "duration": quarter_duration, "pitch": new_phonemes[-1]["pitch"]})

        edited_syllables.append({"syllable": group["syllable"], "phonemes": new_phonemes})
        st.divider()

    # Confirm and synthesize
    if st.button("✅ Confirm & Synthesize"):
        ds_path = TMP_DS_DIR / f"{mei_path.stem}.ds"
        try:
            all_phonemes = [ph for syllable in edited_syllables for ph in syllable["phonemes"]]
            build_ds_from_notes(all_phonemes, ds_path)
            with open(ds_path, "r", encoding="utf-8") as f:
                ds_data = json.load(f)
            validate_ds(ds_data)
            st.success(f"DS file created: {ds_path.name}")
        except Exception:
            handle_exception("DS generation or validation")

        with st.spinner("Running DiffSinger inference…"):
            try:
                wav_path = run_inference(ds_path, OUTPUT_DIR, mei_path.stem)
            except Exception:
                handle_exception("inference")

        st.success("Synthesis complete!")
        st.audio(str(wav_path))
        st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

elif filetype == "DS":
    st.header("1. Upload DS File")
    ds_file = st.file_uploader("Upload your .ds file", type=["ds", "json"])

    if st.button("Synthesize from DS"):
        if not ds_file:
            st.error("Please upload a .ds file.")
        else:
            ds_path = UPLOAD_DS_DIR / ds_file.name
            with open(ds_path, "wb") as f:
                f.write(ds_file.getbuffer())
            with open(ds_path, "r", encoding="utf-8") as f:
                ds_data = json.load(f)
            try:
                validate_ds(ds_data)
            except Exception as e:
                st.error(f"Uploaded DS file is invalid: {e}")
                st.stop()
            st.success(f"DS file uploaded: {ds_path.name}")

            with st.spinner("Running DiffSinger inference…"):
                try:
                    wav_path = run_inference(ds_path, OUTPUT_DIR, ds_path.stem)
                except Exception:
                    handle_exception("inference")

            st.success("Synthesis complete!")
            st.audio(str(wav_path))
            st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

if st.button("Clear All Files"):
    for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)
    st.experimental_rerun()
