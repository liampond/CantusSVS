from typing import List, Dict
import streamlit as st

# Phoneme options (including pauses and breaths)
PHONEMES = [
    "a", "ah", "au", "ay", "b", "c", "cl", "ct", "d", "dj",
    "e", "f", "g", "gr", "i", "ie", "iu", "j", "l", "m",
    "n", "ng", "nt", "o", "oh", "p", "r", "s", "t", "tr",
    "ts", "u", "uo", "v", "x", "AP", "BR"
]


def render_phoneme_editor(notes: List[Dict]) -> List[Dict]:
    """
    Display an editable phoneme alignment table in Streamlit.

    Args:
        notes: list of dicts, each with keys:
            - id: unique identifier
            - pitch: pitch string (e.g. "C4")
            - duration: float, duration in seconds
            - lyric: string, the syllable/lyric text
    Returns:
        List of dicts with same keys + 'phoneme': selected phoneme
    """
    st.header("2. Phoneme Alignment")
    st.write("Select one phoneme per note:")

    edited_notes: List[Dict] = []
    for note in notes:
        # Create columns for pitch, duration, lyric, and phoneme selector
        cols = st.columns([1, 1, 1, 2])
        cols[0].markdown(f"**Pitch:** {note['pitch']}")
        cols[1].markdown(f"**Dur:** {note['duration']}s")
        cols[2].markdown(f"**Lyric:** {note['lyric']}")
        phoneme = cols[3].selectbox(
            label="Phoneme",
            options=PHONEMES,
            index=0,
            key=f"phoneme_{note['id']}"
        )
        # Append the note with user-selected phoneme
        edited_notes.append({
            **note,
            "phoneme": phoneme
        })

    return edited_notes
