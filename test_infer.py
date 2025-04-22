from inference.pipeline import run_inference
from pathlib import Path

ds_path = Path("webapp/tmp_ds/CantusSVSTest.ds")   # change this!
output_dir = Path("webapp/output")
title = "CantusSVSTest"                     # no .ds, just the stem

wav_path = run_inference(ds_path, output_dir, title)
print(wav_path)
