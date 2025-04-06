#!/bin/bash
#SBATCH --account=def-ichiro            # Your project account
#SBATCH --gpus-per-node=1               # Request 1 GPU
#SBATCH --mem=125G                      # Memory per GPU
#SBATCH --cpus-per-task=8               # Request 8 CPU cores
#SBATCH --time=00:10:00                 # Request 4 hours of runtime
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
  --pl_trainer.precision=16-mixed
