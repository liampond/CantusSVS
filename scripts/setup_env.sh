# Load necessary modules only if not already loaded
if ! module list 2>&1 | grep -q gcc; then
  module load gcc/12.2.0
fi

if ! module list 2>&1 | grep -q arrow; then
  module load arrow/19.0.1
fi

# Create virtual environment only if it doesn't exist
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3.11 -m venv venv
else
  echo "Virtual environment already exists, skipping creation."
fi

# Activate the virtual environment
source venv/bin/activate

# Verify if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❗ Warning: Virtual environment is not active!"
  echo "Please activate it manually with: source venv/bin/activate"
  exit 1
fi

# Upgrade pip
pip install --upgrade pip

# Install PyTorch manually first (important for compatibility)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install remaining project dependencies
pip install -r requirements.txt