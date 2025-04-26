import os
import streamlit as st
import shutil
import traceback
from pathlib import Path
import sys

# Disable Streamlit file watcher to avoid Torch path issues
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

# Ensure project root is on the import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from webapp.services.parsing.mei_parser import parse_mei_for_editor
from webapp.services.parsing.ds_builder import build_ds_from_notes
from webapp.services.parsing.ds_validator import validate_ds
from webapp.components.phoneme_editor import render_phoneme_editor
from inference.pipeline import run_inference

# Directories
UPLOAD_MEI_DIR = PROJECT_ROOT / "webapp/uploaded_mei"
UPLOAD_DS_DIR = PROJECT_ROOT / "webapp/uploaded_ds"
TMP_DS_DIR = PROJECT_ROOT / "webapp/tmp_ds"
OUTPUT_DIR = PROJECT_ROOT / "webapp/output"
for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

st.title("CantusSVS: Latin Singing Voice Synthesis")

st.markdown("""
**Choose your input file type:**
- **MEI** (Music Encoding Initiative)
- **DS** (DiffSinger file)
""")

filetype = st.selectbox(
    "Select file type:",
    ["MEI", "DS"],
    help="**MEI**: Music Encoding Initiative\n\n**DS**: DiffSinger format"
)

def handle_exception(context_message):
    """Helper to log full traceback in console and show error nicely in app."""
    st.error(f"{context_message}. See console for details.")
    print("\n" + "="*30)
    print(f"Exception during {context_message}")
    traceback.print_exc()
    print("="*30 + "\n")
    st.stop()

if filetype == "MEI":
    st.header("1. Upload MEI File")
    mei_file = st.file_uploader("Upload your MEI file", type="mei")
    tempo = st.slider("Tempo (BPM)", 30, 300, 120)

    if mei_file:
        # Save uploaded MEI
        mei_path = UPLOAD_MEI_DIR / mei_file.name
        with open(mei_path, "wb") as f:
            f.write(mei_file.getbuffer())

        # Parse into note-level data
        try:
            notes = parse_mei_for_editor(mei_path, tempo)
        except Exception:
            handle_exception("MEI parsing")

        # Render phoneme editor
        notes_with_phoneme = render_phoneme_editor(notes)

        # Once edited, confirm and synthesize
        if st.button("Confirm & Synthesize"):
            ds_path = TMP_DS_DIR / f"{mei_path.stem}.ds"
            try:
                build_ds_from_notes(notes_with_phoneme, ds_path)

                # Validate the generated DS
                from webapp.services.parsing.ds_validator import validate_ds
                import json
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

elif filetype == 'DS':
    st.header("1. Upload .ds File")
    ds_file = st.file_uploader("Upload your .ds file", type=["ds", "json"])

    if st.button("Synthesize from DS"):
        if not ds_file:
            st.error("Please upload a .ds file.")
        else:
            ds_path = UPLOAD_DS_DIR / ds_file.name
            with open(ds_path, "wb") as f:
                f.write(ds_file.getbuffer())
            # Validate uploaded DS
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
