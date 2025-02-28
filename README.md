# AutoGUI
a simple Python-based GUI for x-ray diffraction data processing with Global Phasing's autoPROC

## What is this? And why?
AutoGUI started as a simple "Python-learning-by-doing"-project. The goal of the project was to design a GUI for processing of macromolecular x-ray diffraction data using autoPROC (https://www.globalphasing.com/autoproc/) from Global Phasing Limited (UK). I routinely use autoPROC for processing of my datasets and I'm very happy with its perfomance. While autoPROC ideally requires only minimal input on the command line, I've encountered datasets that required quite some lines of parameters in order to be properly processed. Starting to learn Python at the same time, I decided that a GUI for generating the command line parameters, executing autoPROC and presenting the processing results might be a good beginner's project. (This is also why the code looks probably awful to professionals - but hey, it works.)
Some time has passed since then and AutoGUI grew and gained features and is  used by my colleagues in the lab routinely for quite a while now.
So maybe AutoGUI might be useful for other autoPROC users, that's why AutoGUI is now on GitHub.

## Why could this be useful?
AutoGUI has basically two modes, termed "Classic" and "Batch". 
- "Classic" mode is for processing of single datasets and offers many options for data processing from the GUI. In a simple case, just select the type of data / type of instrument, set the folder where your processed data should go and browse for the input diffraction images and click on run. For more complicated cases there are plenty of options in the GUI to configure data processing without having to look up the correct command line parameters or syntax. You can use the macros that come with autoPROC or write/save/load your own macros. A customizable inhouse-setup is available for those having an inhouse X-ray source. MicroED is supported, too. You can even draw masks (for beamstop, etc.) on the diffraction image or do a circle fitting for the beam centre (if you suffer from iMOSFLM nostalgia :wink:). AutoGUI can also automatically create subfolders for further steps in your structure determination project and tries to order autoPROCs output files. And it terminates all processes that have been spawned when it is closed.
- "Batch" mode is for automated processing of several datasets, e.g. the yield of a night at the beamline. In principle, it is somewhat similar to the autoprocessing known from many beamlines. It has less options than "Classic"-mode, but will go through a list of datasets. Up to three different settings (fast, normal, problematic corresponding to the autoPROC macros "-M fast", no macro and "-M LowResOrTricky") can be tried and if processing of a dataset fails, the next "higher" setting will be tried. This mode runs using screen, so it will continue running if you close your terminal or disconnect from the server running AutoGUI. Live-processing and results will appear in a self-updating HTML-file.
- Both modes are started from the launcher window. This has some additional functions, such as the creation of processing reports (e.g. for all datasets and processing runs of a certain project) as HTML or CSV. "Batch"-Jobs running somewhere in a screen can also be controlled and users can configure their personal preferences, including color themes.

This is a very brief description of a few of the features that have been implemented in AutoGUI. A full description can be found in the (soon to come) manual.

## What do I need to run this?
So far, AutoGUI is developed, tested and routinely used on a server running openSUSE Leap 15.6. It also works on macOS 15.3, although several GUI elements need adjustments to look okay on a Mac (soon to be done). 
- First of all, you need to have a working installation of autoPROC (https://www.globalphasing.com/autoproc/) and the command "process" should be in your path.
- If you have autoPROC, you certainly also have CCP4i (https://www.ccp4.ac.uk) installed. Just make sure that it is in your path.
- The same is true for ImageMagick (https://imagemagick.org).
- You also need to have ADXV (https://www.scripps.edu/tainer/arvai/adxv.html) installed, although it does not necessarily have to be in your path as you will have to define its location in the 'autogui.cfg' configuration file. (Reason: On some systems, the command for it is written with a capital A on others not. I might include an automatic check for this at a later point.)
- It is highly recommended to use a dedicated Conda environment for setting up AutoGUI. It is in that case required to have Miniforge (https://www.conda-forge.org) or Miniconda/Anaconda (https://www.anaconda.org) installed on your system.
- AutoGUI uses Python3.X (tested so far only up to 3.9) and additional required modules are Pillow, Psutil and PySimpleGUI (version 4.70.1)

## How can I set it up? 
### Preparation
1. Extract the AutoGUI files to a folder on your system where you want it to be located.  
2. First check if all external programs (autoPROC, CCP4i, ImagMagic and ADXV) are installed and in the path. (ADXV does not need to be in the path, the location of it is set in the next step.)
3. Adjust the at least the parameters marked as required (and ideally also the rest) in 'autogui.cfg' to match your setup.
### Automatic setup
The easiest and absolutely recommended way from this point on is to use the provided setup script 'autogui_conda_setup.sh'. This automates the rest of the setup process but requires Conda to be installed. Just make the script executable by typing `chmod +x autogui_conda_setup.sh` and let it run. After successful setup, a file called 'autogui' will be created and you will be offered to add AutoGUI to your path for being able to execute it from anywhere. Done! :thumbsup:
### Manual setup
It is highly recommended to use the automatic setup script, as this avoids messing with system Python. But if you do not want to use Conda or have other reasons not to use the automatic setup:
- Install the required Python modules from 'requirements.txt' using pip. (`pip -r requirements.txt`)
- Rename the script 'autogui_no_conda' to 'autogui', open it with a text editor and adjust the paths to your python executable and to the location of 'autogui.py' and save the changes.
- Make 'autogui' executable (`chmod +x autogui`)
- Add the location of this script o your path. That should (hopefully) do it. :thumbsup:
