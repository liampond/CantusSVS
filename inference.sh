#!/bin/bash

# ========== CONFIGURATION ==========

INPUT_DS=$1
OUTPUT_DIR=$2
TITLE=$(basename "$INPUT_DS" .ds)

VARIANCE_EXP=regular_variance_v1
ACOUSTIC_EXP=debug_test

SEED=42
NUM_RUNS=1

# ========== CHECK ==========

if [ -z "$INPUT_DS" ] || [ -z "$OUTPUT_DIR" ]; then
  echo "Usage: ./inference.sh path/to/input.ds path/to/output_dir"
  exit 1
fi

# ========== STEP 1: VARIANCE ==========

echo ">>> Step 1: Running variance model inference..."
python scripts/infer.py variance "$INPUT_DS" \
  --exp "$VARIANCE_EXP" \
  --predict dur --predict pitch \
  --out "$OUTPUT_DIR" \
  --title "$TITLE" \
  --seed "$SEED"

VARIANCE_EXIT_CODE=$?
COMPLETED_DS="$OUTPUT_DIR/${TITLE}.ds"

if [ $VARIANCE_EXIT_CODE -ne 0 ] || [ ! -f "$COMPLETED_DS" ]; then
  echo "❌ Variance inference failed or output DS file was not created."
  exit 1
fi

# ========== STEP 2: ACOUSTIC ==========

echo ">>> Step 2: Running acoustic model inference..."
python scripts/infer.py acoustic "$COMPLETED_DS" \
  --exp "$ACOUSTIC_EXP" \
  --out "$OUTPUT_DIR" \
  --title "$TITLE" \
  --seed "$SEED" \
  --num "$NUM_RUNS"

ACOUSTIC_EXIT_CODE=$?
OUTPUT_WAV="$OUTPUT_DIR/${TITLE}.wav"

if [ $ACOUSTIC_EXIT_CODE -ne 0 ] || [ ! -f "$OUTPUT_WAV" ]; then
  echo "❌ Acoustic inference failed or output WAV file not created."
  exit 1
fi

echo "✅ Done! Output saved to: $OUTPUT_WAV"
