#!/bin/bash
#SBATCH --account=def-ichiro            # Project account
#SBATCH --gpus-per-node=1               # GPUs requested
#SBATCH --mem=125G			                # Memory per GPU
#SBATCH --cpus-per-task=8               # CPUs requested
#SBATCH --time=10:00:00                 # Runtime requested
#SBATCH --output=acoustic_training_%j.out  # Log file will be named like training_12345678.out

# Load required modules
module load cuda/12.2 python/3.11

# Activate virtual environment
source ~/env-py311/bin/activate

# Add project folders to PYTHONPATH
export PYTHONPATH=$(pwd):$(pwd)/basics:$(pwd)/training:$PYTHONPATH

# Check GPU
echo "GPU Check:"
nvidia-smi

python scripts/train.py \
  --config=configs/CantusSVS_acoustic.yaml \
  --exp_name=debug_test \
  --pl_trainer.accelerator=gpu \
  --pl_trainer.devices=1 \
  --pl_trainer.precision=16-mixed \
  --reset
