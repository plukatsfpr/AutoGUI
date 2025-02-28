#!/bin/bash

# AutoGUI setup script (v20250301)
# This is a helper script for the easy distribution/installation of AutoGUI .
# Make sure that all required third-party software has been installed first and 'autogui.cfg' has been edited to match your settings. 
# It relies on a conda environment so Anaconda, Miniconda or Miniforge should be installed first.
# DISCLAIMER: This setup script was written with assistance by ChatGPT. The rest of this project - notably the Python part - was developed without the help of AI methods.
#  
# What this setup script does:
#   1.  Checks if the required software is installed. (Currently conda, autoPROC (a.k.a. process), ccp4i, screen, ImageMagick (a.k.a. magick)) The program list is found in "dependencies.txt".
#   2.  Some paths have to be set before within 'autogui.cfg'. (Currently path to Adxv, a browser, a pdf viewer).
#   3.  A conda environment will be created 
#   4.  The required non-standard python modules listed in "requirements.txt" will be installed (Currently Pillow, psutil, PySimpleGUI 4.70.1)
#   5.  A bash script "autogui" will be created that executes autogui.py from within the created conda environment
#   6.  The folder containing the "autogui" script can be added to the path (optional) to make sure that you can start dataprocessing anywhere typing "autogui" on the terminal. 
#       If you can't start AutoGUI, there might have been problems with adding it to your path. You will in that case have to add it manually.

echo " "
echo "This is a setup script for AutoGUI, a simple Python-based GUI for Global Phasing's autoPROC"
echo " "
echo "Copyright 2025 Peer Lukat"
echo "Helmholtz-Centre for Infection Research, Structure & Function of Proteins"
echo "peer.lukat@helmholtz-hzi.de"
echo "AutoGUI is released under the GNU General Public License Version 3 (or later)"
echo " "
echo "Required pre-installed software:"
echo "'conda':          Anaconda, Miniconda or Miniforge (https://www.anaconda.org, https://www.conda-forge.org)"
echo "'process':        GPhL autoPROC (https://www.globalphasing.com/autoproc)"
echo "'ccp4i':          CCP4 software suite (https://www.ccp4.ac.uk)"
echo "'magick':         ImageMagick (https://imagemagick.org)"
echo "'screen':         Screen (comes with Unix, but the script checks if it is available)"
echo " "
echo "You also need:    Adxv (https://www.scripps.edu/tainer/arvai/adxv.html)"
echo "                  The location of this program has to be defined in 'autogui.cfg'"
echo " "
echo "IMPORTANT:        Please make sure that you have edited 'autogui.cfg' before running this script."
echo "                  You will at least have to set the paths to your browser, a pdf viewer and Adxv for the installation to work."
echo " "
echo "If you proceed, we will first check if all required software is installed on your system and if the paths in 'autogui.cfg' are valid."
echo " "
read -p "Would you like to run the setup now? (Y/n): " run_setup
if [[ "$run_setup" == "n" || "$run_setup" == "N" ]]; then
    # Exit setup if answer is no
    echo "AutoGUI setup was cancelled."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Step 1: Check if required programs are installed
echo " "
echo "Checking required programs..."
missing_programs=()

# Read dependencies.txt and check if each program is installed
while IFS= read -r program; do
    echo "Checking if '$program' is installed..."
    if ! command_exists "$program"; then
        echo " - '$program' is NOT installed."
        missing_programs+=("$program")
    else
        echo " - '$program' is installed."
    fi
done < "dependencies.txt"

# If there are missing programs, prompt the user and exit
if [ ${#missing_programs[@]} -gt 0 ]; then
    echo "The following programs are missing and need to be installed:"
    for program in "${missing_programs[@]}"; do
        echo " - $program"
    done
    exit 1
fi

# Step 2: Check the autogui.cfg variables
echo " "
echo "Checking autogui.cfg for valid paths and commands..."

# Read autogui.cfg and extract values of interest
config_file="autogui.cfg"

# List of keys we care about
required_vars=("browser" "pdfviewer" "adxvpath")

# Loop through each variable and check its value
for var in "${required_vars[@]}"; do
    # Get the value for the current variable from the config file
    value=$(grep -m 1 "^$var =" "$config_file" | sed "s/^$var *= *//;s/[[:space:]]*$//")

    if [ -z "$value" ] || [ "$value" == "No" ]; then
        echo " - '$var' is not set correctly in autogui.cfg."
        echo "Please open 'autogui.cfg' in a text editor and set a valid value for '$var'."
        exit 1
    fi

    # Check if the value is a valid file or executable (path/command check)
    if [[ ! -e "$value" && ! -x "$value" ]]; then
        echo " - The path/command for '$var' (${value}) is NOT valid."
        echo "Please open 'autogui.cfg' in a text editor and correct the value for '$var'."
        exit 1
    else
        echo " - The path/command for '$var' (${value}) is valid."
    fi
done

# Step 3: Create and set up the conda environment
echo " "
echo "Creating conda environment 'autogui_env' with Python 3.9..."

# Create the conda environment
conda create --name autogui_env python=3.9 -y

# Activate the conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate autogui_env

# Step 4: Install Python dependencies
echo " "
echo "Installing Python dependencies from requirements.txt..."

# Install Python modules listed in requirements.txt
if [ -f "requirements.txt" ]; then
    echo " - requirements.txt found. Installing dependencies..."
    
    # Attempt to install the dependencies
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: One or more Python modules could not be installed from requirements.txt."
        exit 1
    fi
else
    echo " - requirements.txt not found. Skipping Python dependencies installation."
fi

# Deactivate the conda environment
echo " "
echo "Deactivating conda environment..."
conda deactivate

# Step 5: Create the autogui script
echo " "
echo "Creating 'autogui' script..."

# Get the absolute path to the current directory where the script is executed
SCRIPT_DIR="$(pwd)"

# Make sure we're working with the correct directory where the script should be saved
PYTHON_SCRIPT_PATH="$SCRIPT_DIR/autogui.py"  # Absolute path to autogui.py

# Create the autogui script in the current working directory
echo "#!/bin/bash" > "$SCRIPT_DIR/autogui"
echo "conda run -n autogui_env python $PYTHON_SCRIPT_PATH \"\$@\"" >> "$SCRIPT_DIR/autogui"

# Make the script executable
chmod +x "$SCRIPT_DIR/autogui"

# Provide feedback
echo "'autogui' script has been created and is executable."
echo " "


# Step 6: Ask the user if they want to add the script to the PATH
read -p "Would you like to add the 'autogui' script to the PATH (recommended)? (y/N): " add_to_path
if [[ "$add_to_path" == "y" || "$add_to_path" == "Y" ]]; then
    # Check if the user is using zsh or bash and update the appropriate shell config file
    if [[ "$SHELL" == *"zsh"* ]]; then
        config_file="$HOME/.zshrc"  # For zsh users
    elif [[ "$SHELL" == *"bash"* ]]; then
        config_file="$HOME/.bash_profile"  # For bash users (bash_profile for login shells)
    else
        echo "Unrecognized shell, unable to modify PATH."
        exit 1
    fi

    # Ensure the shell config file exists before modifying
    if [ ! -f "$config_file" ]; then
        echo "$config_file does not exist. Creating it..."
        touch "$config_file"
    fi

    # Check if the script's directory is already in the PATH
    echo " "
    if ! grep -q "$SCRIPT_DIR" "$config_file"; then
        echo "Adding '$SCRIPT_DIR' to the PATH in $config_file..."
        echo "export PATH=\$PATH:$SCRIPT_DIR" >> "$config_file"
        echo "Sourcing $config_file to apply the changes..."
        source "$config_file"
        echo "'$SCRIPT_DIR' has been added to the PATH."
        echo "Type 'autogui' to run AutoGUI from anywhere."
    else
        echo "'$SCRIPT_DIR' is already in the PATH."
        echo "Type 'autogui' to run AutoGUI from anywhere."
    fi
else
    echo "The 'autogui' script was not added to the PATH." 
    echo "Consider adding it to the PATH manually to be able to run it from anywhere."
fi

echo " "
echo "AutoGUI setup has finished."
