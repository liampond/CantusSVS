#!/bin/bash
#SBATCH --account=def-ichiro            # Project account
#SBATCH --gpus-per-node=1               # GPUs requested
#SBATCH --mem=125G                      # Memory per GPU
#SBATCH --cpus-per-task=8               # CPUs requested
#SBATCH --time=12:00:00                 # Runtime requested
#SBATCH --output=variance_training_%j.out  # Log file

# Load required modules
module load cuda/12.2 python/3.11

# Activate virtual environment
source ~/env-py311/bin/activate

# Set up PYTHONPATH
export PYTHONPATH=$(pwd):$(pwd)/basics:$(pwd)/training:$PYTHONPATH

# Check GPU
echo "GPU Check:"
nvidia-smi

# Launch training
python scripts/train.py \
  --config=configs/CantusSVS_variance.yaml \
  --exp_name=regular_variance_v1 \
  --pl_trainer.accelerator=gpu \
  --pl_trainer.devices=1 \
  --pl_trainer.precision=16-mixed \
  --reset
