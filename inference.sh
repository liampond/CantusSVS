#!/bin/bash

# ========== CONFIGURATION ==========

# Input .ds file (should include ph_seq, ph_num, note_seq, note_dur, note_slur)
INPUT_DS=$1

# Output directory for audio and intermediate files
OUTPUT_DIR=$2

# Title (used for output filename)
TITLE=$(basename "$INPUT_DS" .ds)

# Model experiment names (must match folder names in checkpoints/)
VARIANCE_EXP=regular_variance_v1
ACOUSTIC_EXP=regular_acoustic_v1

# Optional: Seed for reproducibility
SEED=42

# Optional: Number of diffusion runs
NUM_RUNS=1

# ========== CHECK ==========

if [ -z "$INPUT_DS" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: ./inference.sh path/to/input.ds path/to/output_dir"
  exit 1
fi

# ========== RUN VARIANCE MODEL ==========

echo ">>> Step 1: Running variance model inference..."
python scripts/infer.py variance \
  "$INPUT_DS" \
  --exp "$VARIANCE_EXP" \
  --predict dur pitch \
  --out "$OUTPUT_DIR" \
  --title "$TITLE" \
  --seed "$SEED"

# ========== RUN ACOUSTIC MODEL ==========

COMPLETED_DS="$OUTPUT_DIR/${TITLE}.ds"

echo ">>> Step 2: Running acoustic model inference..."
python scripts/infer.py acoustic \
  "$COMPLETED_DS" \
  --exp "$ACOUSTIC_EXP" \
  --out "$OUTPUT_DIR" \
  --title "$TITLE" \
  --seed "$SEED" \
  --num "$NUM_RUNS"

echo ">>> Done! Output saved to: $OUTPUT_DIR/${TITLE}.wav"
