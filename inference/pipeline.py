# inference/pipeline.py

import json
from pathlib import Path
from typing import Optional

from utils.hparams import hparams  # set_hparams removed from here
from inference.ds_acoustic import DiffSingerAcousticInfer
from inference.ds_variance import DiffSingerVarianceInfer
from utils.infer_utils import parse_commandline_spk_mix, trans_key

def run_inference(ds_path: Path, output_dir: Path, title: str, *,
                  variance_exp: str = "regular_variance_v1",
                  acoustic_exp: str = "debug_test",
                  seed: int = 42,
                  num_runs: int = 1,
                  key_shift: int = 0,
                  gender: Optional[float] = None) -> Path:
    """
    Runs full inference pipeline (variance + acoustic) and returns the generated WAV file path.
    """
    if not ds_path.exists():
        raise FileNotFoundError(f"Input DS file not found: {ds_path}")

    # Load .ds file
    with open(ds_path, "r", encoding="utf-8") as f:
        params = json.load(f)
    if not isinstance(params, list):
        params = [params]

    # Inject dummy ph_seq if missing
    for param in params:
        if "ph_seq" not in param:
            text = param.get("text", "")
            param["ph_seq"] = " ".join(text.lower().replace(" ", ""))

    # Transpose if needed
    if key_shift != 0:
        params = trans_key(params, key_shift)

    # Speaker mix (not used here but included for extensibility)
    spk_mix = parse_commandline_spk_mix(None) if hparams.get("use_spk_id") else None
    for param in params:
        if gender is not None and hparams.get("use_key_shift_embed"):
            param["gender"] = gender
        if spk_mix is not None:
            param["spk_mix"] = spk_mix

    # Run variance model
    variance_infer = DiffSingerVarianceInfer(ckpt_steps=None, predictions={"dur", "pitch"})
    ds_out_path = output_dir / f"{title}.ds"
    variance_infer.run_inference(params, out_dir=output_dir, title=title, num_runs=1, seed=seed)

    if not ds_out_path.exists():
        raise RuntimeError(f"Variance inference failed; expected DS file not found at {ds_out_path}")

    # Run acoustic model
    acoustic_infer = DiffSingerAcousticInfer(load_vocoder=True, ckpt_steps=None)
    acoustic_infer.run_inference(params, out_dir=output_dir, title=title, num_runs=num_runs, seed=seed)

    wav_path = output_dir / f"{title}.wav"
    if not wav_path.exists():
        raise RuntimeError(f"Acoustic inference failed; expected WAV not found at {wav_path}")

    return wav_path


if __name__ == "__main__":
    import argparse
    import sys
    from utils.hparams import set_hparams  # call it only in CLI

    parser = argparse.ArgumentParser(description="Run full DiffSinger inference pipeline")
    parser.add_argument("ds_path", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--title", type=str, required=False)
    parser.add_argument("--variance_exp", type=str, default="regular_variance_v1")
    parser.add_argument("--acoustic_exp", type=str, default="debug_test")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num_runs", type=int, default=1)
    parser.add_argument("--key_shift", type=int, default=0)
    parser.add_argument("--gender", type=float, default=None)

    args = parser.parse_args()

    sys.argv = ["", "--exp_name", args.variance_exp, "--infer"]
    set_hparams(print_hparams=False)

    title = args.title or args.ds_path.stem
    run_inference(
        ds_path=args.ds_path,
        output_dir=args.output_dir,
        title=title,
        variance_exp=args.variance_exp,
        acoustic_exp=args.acoustic_exp,
        seed=args.seed,
        num_runs=args.num_runs,
        key_shift=args.key_shift,
        gender=args.gender,
    )
