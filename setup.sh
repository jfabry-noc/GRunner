#!/usr/bin/env bash
# Check for Python.
python_path=$(which python3)
venv_base="$(pwd)/.venv"
local_python_path="$venv_base/bin/python3"
main_path="$(pwd)/src/main.py \$@"

# Validate that Python is installed.
if [ ! $python_path ]; then
	echo "Missing Python3! Intall it from your package manager."
	exit 1
fi

# Try to create the virtual environment if it doesn't already exist.
echo "Creating the virtual environment..."
if [ -d "$venv_base" ]; then
	echo ".venv already exists in this directory! Delete it to continue, e.g.: rm -rf .venv/"
	exit 1
fi
python3 -m venv .venv > /dev/null

# Switch to the context of the virtual environment. 
echo "Switching to the context of the virtual environment."
source "$venv_base/bin/activate"
echo "Python is here: $(which python3)"

# Update pip and setuptools.
echo "Ensuring pip is updated..."
python3 -m pip install -U pip setuptools > /dev/null

# Install requests.
echo "Installing required packages..."
python3 -m pip install -r requirements.txt > /dev/null

# Drop from the virtual environment.
echo "Getting out of the virtual environment."
deactivate

# Create the writepyly script in a $PATH location.
echo "Adding a 'grunner' executable at: /usr/local/bin/grunner"
echo "Note: You may be prompted for the root/sudo password to write here!"
echo "#!/usr/bin/env bash" | sudo tee /usr/local/bin/grunner
echo "$local_python_path $main_path" | sudo tee -a /usr/local/bin/grunner
sudo chmod +x /usr/local/bin/grunner

echo "Setup complete!"
