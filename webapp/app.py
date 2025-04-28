import os
import shutil
import traceback
import json
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Disable Streamlit file watcher
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

# Config
st.set_page_config(page_title="CantusSVS", layout="wide")

# CSS styling
st.markdown("""
<style>
html, body, [class*="css"] { font-size: 18px !important; }
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label {
    font-size: 13px; padding-bottom: 0px;
}
div[data-testid="stSlider"] label { font-size: 0px; }
button[kind="secondary"] {
    height: 32px; width: 32px;
    font-size: 20px; background-color: black !important;
    color: white !important; margin-top: 5px;
}
div.stButton > button:first-child {
    background-color: black; color: white;
    font-size: 16px; padding: 6px 24px;
}
section[data-testid="stFileUploaderDropzone"] {
    padding: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Phoneme mappings
phoneme_display_map = {
    "ap": "Pause",
    "br": "Breath"
}
display_to_phoneme = {v: k for k, v in phoneme_display_map.items()}
full_phoneme_list_display = [phoneme_display_map.get(p, p) for p in permitted_phonemes]

# Pitch list D4-D5
allowed_pitches = ["D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4", "C5", "C#5", "D5"]

# Title
st.title("CantusSVS: Latin Singing Voice Synthesis")

st.markdown("""
# About CantusSVS

CantusSVS is a web-based Singing Voice Synthesis (SVS) system designed for composers and musicians to synthesize Latin chant audio from a custom musical score.  
Built on top of the DiffSinger AI model, CantusSVS enables detailed, precise control over melody, rhythm, phonemes, and timing without any programming knowledge required.

---

# How to Use CantusSVS

## 1. Install MuseScore 4

Download and install [MuseScore 4](https://musescore.org/en/4.0).

## 2. Compose Your Music

In MuseScore, compose the chant you want to synthesize:

- Monophonic only (one note at a time, no harmonies or chords)
- Stay within the pitch range of **D4 to D5**
- Add lyrics (Latin) under each note

## 3. Export Your Score to MEI

When your score is complete:

- Go to **File → Export**
- Choose the **.mei** file format
- Save it to your computer

## 4. Upload Your Score to CantusSVS

In the CantusSVS web app:

- Select **MEI** mode
- Upload your `.mei` file
- Adjust the **tempo** if necessary using the provided slider
- Your score will be displayed using Verovio

## 5. Edit Phonemes, Durations, and Pitches

CantusSVS automatically suggests phoneme splits for each syllable.  
You will have the opportunity to review phonemes, durations, and pitches.

## 6. Synthesize the Audio

When you're done:

- Click **Confirm & Synthesize**
- CantusSVS will create a `.ds` file
- It processes the file through pretrained DiffSinger models
- The synthesized chant will be generated

This typically takes a few seconds to a few minutes depending on input length.

## 7. Listen and Download

After synthesis you can either listen to your chant directly in the app or download a .wav file to your computer.

---

# About DiffSinger

DiffSinger is a deep learning-based Singing Voice Synthesis (SVS) framework that uses diffusion models to generate natural singing voices from symbolic musical input.  
It improves quality over earlier SVS systems and allows higher fidelity control over timing, pitch, and vocal expression.

CantusSVS uses a custom-trained DiffSinger model specifically adapted for medieval chant synthesis.

---

""")

filetype = st.selectbox("Select file type:", ["MEI", "DS"])

def handle_exception(context_message):
    st.error(f"{context_message}. See console.")
    print("\n" + "="*30)
    print(f"Exception during {context_message}")
    traceback.print_exc()
    print("="*30 + "\n")
    st.stop()

# MEI Mode
if filetype == "MEI":
    st.header("1. Select MEI Source")
    use_demo = st.checkbox("Use demo MEI file (CantusSVSDemo.mei)", value=False)
    tempo = st.slider("Tempo (BPM)", 30, 300, 120)

    if use_demo:
        mei_path = UPLOAD_MEI_DIR / "CantusSVSDemo.mei"
        if not mei_path.exists():
            st.error("Demo MEI file missing.")
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

    if use_demo:
        fixed_syllables = [
            ["m", "u", "s"],
            ["i"],
            ["c", "a"],
            ["e", "s", "t"],
            ["v", "i"],
            ["t", "a"]
        ]
        fixed_note_seq = "G#4 G#4 F#4 F#4 G#4 G#4 A4 A4 A4 A4 A4 G#4 G#4".split()
        fixed_note_dur = [0.1, 0.5, 0.1, 0.5, 0.1, 0.5, 0.5, 0.05, 0.05, 0.1, 0.9, 0.1, 0.9]

        raw_notes = []
        idx = 0
        for syllable_phonemes in fixed_syllables:
            syllable_duration = 0
            for _ in syllable_phonemes:
                syllable_duration += fixed_note_dur[idx]
                idx += 1
            syllable_text = ''.join(syllable_phonemes)
            pitch = fixed_note_seq[idx - 1]
            raw_notes.append({
                "lyric": syllable_text,
                "pitch": pitch,
                "duration": syllable_duration
            })

    if "original_raw_notes" not in st.session_state:
        st.session_state.original_raw_notes = raw_notes

    syllable_groups = []

    for note in st.session_state.original_raw_notes:
        syllable_text = note["lyric"]
        pitch = note["pitch"]
        phonemes = list(syllable_text) if syllable_text else ["a"]
        syllable = []
        for ph in phonemes:
            syllable.append({
                "phoneme": ph if ph in permitted_phonemes else "a",
                "duration": max(0.05, (note["duration"] / len(phonemes)) * (60/tempo)),
                "pitch": pitch if pitch in allowed_pitches else "D4"
            })
        syllable_groups.append({
            "syllable": syllable_text,
            "phonemes": syllable
        })

    if "edited_syllables" not in st.session_state:
        st.session_state.edited_syllables = syllable_groups

    st.subheader("Score Preview")
    components.html(f"""
    <div id=\"app\" style=\"border: 1px solid lightgray; min-height: 400px;\"></div>
    <script type=\"module\">
        import 'https://editor.verovio.org/javascript/app/verovio-app.js';
        const app = new Verovio.App(document.getElementById("app"), {{
            defaultView: 'document',
            documentZoom: 4
        }});
        app.loadData(`{mei_text}`);
    </script>
    """, height=500)

    st.subheader("Edit Phonemes, Durations, and Pitches", divider="gray")
    updated_syllables = []

    for idx, group in enumerate(st.session_state.edited_syllables):
        st.markdown(f"#### {group['syllable'].capitalize()}")
        new_phonemes = []

        for j, ph in enumerate(group["phonemes"]):
            col1, col2, col3 = st.columns([3, 3, 3])

            with col1:
                phoneme_display = st.selectbox(
                    "Phoneme",
                    full_phoneme_list_display,
                    index=full_phoneme_list_display.index(phoneme_display_map.get(ph["phoneme"], ph["phoneme"])),
                    key=f"phoneme_{idx}_{j}"
                )
                phoneme_internal = display_to_phoneme.get(phoneme_display, phoneme_display)

            with col2:
                duration = st.number_input(
                    "Duration (seconds)",
                    min_value=0.05,
                    max_value=5.0,
                    value=float(ph["duration"]),
                    step=0.01,
                    format="%.2f",
                    key=f"duration_num_{idx}_{j}"
                )

            with col3:
                pitch = st.selectbox(
                    "Pitch",
                    allowed_pitches,
                    index=allowed_pitches.index(ph["pitch"]) if ph["pitch"] in allowed_pitches else 0,
                    key=f"pitch_{idx}_{j}"
                )

            new_phonemes.append({
                "phoneme": phoneme_internal,
                "duration": duration,
                "pitch": pitch
            })

        updated_syllables.append({
            "syllable": group["syllable"],
            "phonemes": new_phonemes
        })

        st.divider()

    st.session_state.edited_syllables = updated_syllables

    st.markdown("### Actions", unsafe_allow_html=True)
    col_confirm, col_clear = st.columns([1, 5])

    with col_confirm:
        confirm_clicked = st.button("✅ Confirm & Synthesize", key="confirm_button_mei")

    with col_clear:
        clear_clicked = st.button("🗑️ Clear All Files", key="clear_button_mei")

    if confirm_clicked:
        ds_path = TMP_DS_DIR / f"{mei_path.stem}.ds"
        try:
            all_phonemes = [ph for syllable in st.session_state.edited_syllables for ph in syllable["phonemes"]]
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

    if clear_clicked:
        for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True, exist_ok=True)
        st.experimental_rerun()

# DS Mode
elif filetype == "DS":
    st.header("1. Upload DS File")
    ds_file = st.file_uploader("Upload your .ds file", type=["ds", "json"])

    st.markdown("### Actions", unsafe_allow_html=True)
    col_syn, col_clear = st.columns([1, 5])

    with col_syn:
        synth_clicked = st.button("✅ Synthesize", key="synthesize_button_ds")

    with col_clear:
        clear_ds_clicked = st.button("🗑️ Clear All Files", key="clear_button_ds")

    if synth_clicked:
        if not ds_file:
            st.error("Please upload a .ds file.")
            st.stop()

        ds_path = UPLOAD_DS_DIR / ds_file.name
        with open(ds_path, "wb") as f:
            f.write(ds_file.getbuffer())
        with open(ds_path, "r", encoding="utf-8") as f:
            ds_data = json.load(f)

        try:
            validate_ds(ds_data)
        except Exception as e:
            st.error(f"Invalid DS file: {e}")
            st.stop()

        with st.spinner("Running DiffSinger inference…"):
            try:
                wav_path = run_inference(ds_path, OUTPUT_DIR, ds_path.stem)
            except Exception:
                handle_exception("inference")

        st.success("Synthesis complete!")
        st.audio(str(wav_path))
        st.download_button("Download WAV", data=open(wav_path, "rb"), file_name=wav_path.name)

    if clear_ds_clicked:
        for d in [UPLOAD_MEI_DIR, UPLOAD_DS_DIR, TMP_DS_DIR, OUTPUT_DIR]:
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True, exist_ok=True)
        st.experimental_rerun()
