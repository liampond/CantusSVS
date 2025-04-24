import os
# Disable Streamlit file watcher to avoid Torch path issues
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

import streamlit as st
import shutil
from pathlib import Path
import sys

# Ensure project root is on the import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from inference.mei_parser import parse_mei
from inference.ds_generator import build_ds_input
from inference.pipeline import run_inference

# Directories
UPLOAD_MEI_DIR = PROJECT_ROOT / "webapp/uploaded_mei"
UPLOAD_DS_DIR = PROJECT_ROOT / "webapp/uploaded_ds"
TMP_DS_DIR = PROJECT_ROOT / "webapp/tmp_ds"
OUTPUT_DIR = PROJECT_ROOT / "webapp/output"
for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

st.title("CantusSVS: Latin Singing Voice Synthesis")

mode = st.radio("Select input mode:", ["MEI → DS", "Upload .ds"])

if mode == "MEI → DS":
    st.header("1. Upload MEI File")
    mei_file = st.file_uploader("Upload your MEI file", type="mei")
    tempo = st.slider("Tempo (BPM)", 30, 300, 120)
    if st.button("Generate & Synthesize from MEI"):
        if not mei_file:
            st.error("Please upload a MEI file.")
        else:
            mei_path = UPLOAD_MEI_DIR / mei_file.name
            with open(mei_path, "wb") as f:
                f.write(mei_file.getbuffer())
            try:
                parsed = parse_mei(mei_path, tempo)
            except Exception as e:
                st.error(f"MEI parsing error: {e}")
                st.stop()
            ds_path = TMP_DS_DIR / f"{mei_path.stem}.ds"
            build_ds_input(parsed, ds_path)
            st.success(f"DS file created: {ds_path.name}")
            with st.spinner("Running DiffSinger inference…"):
                try:
                    wav_path = run_inference(ds_path, OUTPUT_DIR, mei_path.stem)
                except Exception as e:
                    st.error(f"Inference failed: {e}")
                    st.stop()
            st.success("Synthesis complete!")
            st.audio(str(wav_path))
            st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

elif mode == "Upload .ds":
    st.header("1. Upload .ds File")
    ds_file = st.file_uploader("Upload your .ds file", type=["ds","json"])
    if st.button("Synthesize from DS"):
        if not ds_file:
            st.error("Please upload a .ds file.")
        else:
            ds_path = UPLOAD_DS_DIR / ds_file.name
            with open(ds_path, "wb") as f:
                f.write(ds_file.getbuffer())
            st.success(f"DS file uploaded: {ds_path.name}")
            with st.spinner("Running DiffSinger inference…"):
                try:
                    wav_path = run_inference(ds_path, OUTPUT_DIR, ds_path.stem)
                except Exception as e:
                    st.error(f"Inference failed: {e}")
                    st.stop()
            st.success("Synthesis complete!")
            st.audio(str(wav_path))
            st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

if st.button("Clear All Files"):
    for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True, exist_ok=True)
    st.experimental_rerun()
