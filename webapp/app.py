import streamlit as st
import shutil
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from inference.mei_parser import parse_mei
from inference.ds_generator import build_ds_input
from inference.pipeline import run_inference

UPLOAD_DIR = Path("webapp/uploaded_mei")
TMP_DS_DIR = Path("webapp/tmp_ds")
OUTPUT_DIR = Path("webapp/output")

for d in [UPLOAD_DIR, TMP_DS_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

st.title("CantusSVS: Singing Voice Synthesis from MEI")

uploaded_file = st.file_uploader("Upload your MEI file", type="mei")
tempo = st.slider("Tempo (BPM)", min_value=30, max_value=300, value=120)

if st.button("Synthesize"):
    if uploaded_file is None:
        st.error("Please upload an MEI file.")
    else:
        mei_path = UPLOAD_DIR / uploaded_file.name
        with open(mei_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            parsed = parse_mei(mei_path, tempo=tempo)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        title = mei_path.stem
        ds_path = TMP_DS_DIR / f"{title}.ds"
        build_ds_input(parsed, ds_path)

        try:
            wav_path = run_inference(ds_path, OUTPUT_DIR, title)
        except Exception as e:
            st.error("Inference failed:")
            st.text(str(e))
            st.stop()

        if not wav_path.exists():
            st.error("Expected output WAV not found.")
        else:
            st.success("Synthesis complete!")
            st.audio(str(wav_path))
            st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

if st.button("Clear Uploads"):
    for d in [UPLOAD_DIR, TMP_DS_DIR, OUTPUT_DIR]:
        shutil.rmtree(d)
        d.mkdir()
