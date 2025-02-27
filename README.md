# AutoGUI
a simple Python-based GUI for x-ray diffraction data processing with Global Phasing's autoPROC

# What is this?
AutoGUI started as a simple "Python-learning-by-doing"-project. The goal of the project was to design a GUI for processing of macromolecular x-ray diffraction data using autoPROC (https://www.globalphasing.com/autoproc/) from Global Phasing Ltd (UK). I routinely use autoPROC for processing of my datasets and I'm very happy with its perfomance. While autoPROC ideally requires only minimal input on the command line, I've encountered datasets that required quite some lines of parameters in order to be properly processed. Starting to learn Python at the same time, I decided that a GUI for generating the command line parameters, executing autoPROC and presenting the processing results might be a good beginner's project. (This is also why the code looks probably awful to professionals - but hey, it works.)
Some time has passed since then and AutoGUI grew and gained features and has been routinely used by my colleagues in the lab for quite a while now.
I now decided that the features of AutoGUI might be useful for other autoPROC users, that's why AutoGUI is now on GitHub.

# What are the features?
AutoGUI has basically two modes, termed "Classic" and "Batch". 
- "Classic" mode is for processing of single datasets and offers many options for data processing from the GUI. In a simple case, just select the type of data / type of instrument, set the folder where your processed data should go and browse for the input diffraction images and click on run. For more complicated cases there are plenty of options in the GUI to configure data processing without having to look up the correct command line parameters or syntax. A customizable inhouse-setup is available for those havin an inhouse X-ray source. MicroED is supported, too. You can even draw masks (for beamstop, etc.) on the diffraction image or do a circle fitting for the beam centre (if you suffer from iMOSFLM nostalgia ;-)). AutoGUI can also automatically create subfolders for further steps in your structure determination project and tries to order autoPROCs output files. And it terminates all processes that have been spawned when it is closed.
- "Batch" mode is for automated processing of several datasets, e.g. the yield of a night at the beamline. In principle, it is somewhat similar to the autoprocessing known from many beamlines. It has less options than "Classic"-mode, but will go through a list of datasets. Up to three different settings (fast, normal, problematic corresponding to the autoPROC macros "-M fast", no macro and "-M LowResOrTricky") can be tried and if processing of a dataset fails, the next "higher" setting will be tried. This mode runs using screen, so it will continue running if you close your terminal or disconnect from the server running AutoGUI. Live-processing and results will appear in a self-updating HTML-file.
- Both modes are started from the launcher window. This has some additional functions, such as the creation of processing reports (e.g. for all datasets and processing runs of a certain project) as HTML or CSV. "Batch"-Jobs running somewhere in a screen can also be controlled and users can configure their personal preferences, including color themes.

This is a very brief description of a few of the features that have been implemented in AutoGUI. A full description can be found in the soon to come manual.

# What do I need to run this?
So far, AutoGUI is developed, tested and routinely used on a server running openSUSE Leap 15.6. It also works on macOS 15.3, although several GUI elements need adjustments to look okay on a Mac (soon to be done). 
- First of all, you need to have a working installation of autoPROC (https://www.globalphasing.com/autoproc/) and the command "process" should be in your path.
- If you have autoPROC, you certainly also have CCP4i (https://www.ccp4.ac.uk) installed. Just make sure that it is in your path.
- The same is true for ImageMagick (https://imagemagick.org).
- You also need to have ADXV istalled, although it does not necessarily have to be in your path as you will have to define its location in the 'autogui.cfg' configuration file.
- AutoGUI uses Python3.X (tested so far only up to 3.9) and additional required modules are Pillow, psutil and PySimpleGUI (version 4.70.1)
- It is highly recommended to use a dedicated conda environment for setting up AutoGUI. It is in that case required to have Miniforge (https://www.conda-forge.org) or Miniconda/Anaconda (https://www.anaconda.org) installed on your system.

# How can I install it? 
- Extract the AutoGUI files to a folder where it should be located.  
- First check if all external programs (autoPROC, CCP4i, ImagMagic and ADXV) are installed and in the path (if required).
- Adjust the required parameters (and ideally also the others) in 'autogui.cfg' to match your setup.
  
- The easiest and absolutely recommended way would then be to use the provided setup script 'autogui_conda_setup.sh'. This automates most of the setup process but requires conda to be installed. Just make the script executable by typing 'chmod +x autogui_conda_setup.sh' and let it run. This will after successful setup create a file called 'autogui' that can be also added to your path for being able to execute it from anywhere.
