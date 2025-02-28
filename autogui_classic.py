# This file is part of AutoGUI.
# Copyright 2025 Peer Lukat
# Peer.Lukat@helmholtz-hzi.de
# Helmholtz-Centre for Infection Research, Structure & Function of Proteins
#
#    AutoGUI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    any later version.
#
#    AutoGUI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AutoGUI.  If not, see <http://www.gnu.org/licenses/>.


version = 'v.20250301'                             # current version

# Dependencies required:
# PySimpleGui 4.70.1 (pip install pysimplegui==4.70.1)
# psutil (pip install psutil)
# PIL (pip install Pillow)
# Working installation of GPhL AutoPROC (www.globalphasing.com/autoproc/)
# Working installation of CCP4i (www.ccp4.ac.uk)
# Working installation of Adxv for Image viewing (www.scripps.edu/tainer/arvai/adxv.html)
# Working installation of ImageMagick (www.imagemagick.org)
# Something to open PDFs
# Some webbrowser


# Fallback configuration if config file can't be read
inpath = "/Data/"                           # change this to default in path
outpath = ""                                # change this to default out path, leave empty if to be set via gui
adxvpath = "/software/bin/adxv"             # path to/ command to run Adxv 
browser = "chromium"                        # path to/ command to start browser
pdfviewer = "okular"                        # path to/ command to run pdf-viewer 
nprocs = "8"                                # default number of processors
maxprocs  = "32"                            # maximum number of processors available
preplist = 'refine coot mr xtriage autobuild pdb_deposit ccp4 pymol' # list of folders to create if "prepare folders" is checked. "autoproc" is required and will always be created automatically. "images" will be created if linking image files is enabled. "beamline_processed" will be created if linking of beamline-processed data is enabled and such data is found.
inhouse_pars = 'autoPROC_XdsKeyword_SENSOR_THICKNESS="0.45" autoPROC_XdsKeyword_SEPMIN="2" autoPROC_XdsKeyword_CLUSTER_RADIUS="2" KapparotSite="AFC-11" autoPROC_TwoThetaAxisRotationAxisFactor="1.0" autoPROC_XdsDistanceFac="1" autoPROC_XdsMaxDistanceJitter="2.0" XdsOptimizeIdxrefAlways="yes"' # parameters required for proper indexing with SFPR's Rigaku 007HF + AFC11 + Pilatus300K setup
inhouse_detector = "In-house: PILATUS 300K" # name of inhouse detector
inhouse_message = ('This works only for images that have been exported from CrysAlisPro(red) in D*TREK-format!\nDue to the way images are recorded by CrysAlisPro, screw axes are likely to be missed.\n\nIt is thus highly recommended to run POINTLESS from the GUI again after AutoPROC has finished!')
display_inhouse_message = True # display above message if inhouse detector is selected?
dark_theme = False                                    # use dark or light theme
prepfolder_classic = True                             # prepare subfolders in classic mode?
prepfolder_batch = True                               # prepare subfolders in batch mode?
 

theme_highlight_color = '#458eaf'
dark_theme_color = '#2b2a32' 
light_theme_color = 'white'




# Python stuff starts here

import PySimpleGUI as sg
import time
import subprocess
import os
import threading
import psutil
import re
import sys
import shutil
import gc
import faulthandler
from PIL import Image
import math

# icon
ag_icon = b'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WHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4KPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNC40LjAtRXhpdjIiPgogPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgeG1sbnM6aXB0Y0V4dD0iaHR0cDovL2lwdGMub3JnL3N0ZC9JcHRjNHhtcEV4dC8yMDA4LTAyLTI5LyIKICAgIHhtbG5zOnhtcE1NPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvbW0vIgogICAgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIKICAgIHhtbG5zOnBsdXM9Imh0dHA6Ly9ucy51c2VwbHVzLm9yZy9sZGYveG1wLzEuMC8iCiAgICB4bWxuczpHSU1QPSJodHRwOi8vd3d3LmdpbXAub3JnL3htcC8iCiAgICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgICB4bWxuczpleGlmPSJodHRwOi8vbnMuYWRvYmUuY29tL2V4aWYvMS4wLyIKICAgIHhtbG5zOnRpZmY9Imh0dHA6Ly9ucy5hZG9iZS5jb20vdGlmZi8xLjAvIgogICAgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIgogICB4bXBNTTpEb2N1bWVudElEPSJnaW1wOmRvY2lkOmdpbXA6YWE1YmZkYTUtZGEzMy00OWI4LWI5ODktOGNjMWRhNWNhYjYxIgogICB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjdjMzZhMWRhLTZmMzEtNDU0My05ZGIxLWIzNzVmYWFmYTA2MyIKICAgeG1wTU06T3JpZ2luYWxEb2N1bWVudElEPSJ4bXAuZGlkOjQ1ODg3YWUxLTA0MTEtNDVkNy1iNDFlLWM4YjJjM2Q1ZjgwMCIKICAgR0lNUDpBUEk9IjIuMCIKICAgR0lNUDpQbGF0Zm9ybT0iTWFjIE9TIgogICBHSU1QOlRpbWVTdGFtcD0iMTY2MzMzOTE3MDAzNjYzNyIKICAgR0lNUDpWZXJzaW9uPSIyLjEwLjYiCiAgIGRjOkZvcm1hdD0iaW1hZ2UvcG5nIgogICBleGlmOkNvbG9yU3BhY2U9IjEiCiAgIGV4aWY6UGl4ZWxYRGltZW5zaW9uPSIyOTk5IgogICBleGlmOlBpeGVsWURpbWVuc2lvbj0iMTY4NyIKICAgdGlmZjpPcmllbnRhdGlvbj0iMSIKICAgdGlmZjpSZXNvbHV0aW9uVW5pdD0iMiIKICAgdGlmZjpYUmVzb2x1dGlvbj0iMjI1IgogICB0aWZmOllSZXNvbHV0aW9uPSIyMjUiCiAgIHhtcDpDcmVhdG9yVG9vbD0iR0lNUCAyLjEwIj4KICAgPGlwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25DcmVhdGVkPgogICA8aXB0Y0V4dDpMb2NhdGlvblNob3duPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6TG9jYXRpb25TaG93bj4KICAgPGlwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6QXJ0d29ya09yT2JqZWN0PgogICA8aXB0Y0V4dDpSZWdpc3RyeUlkPgogICAgPHJkZjpCYWcvPgogICA8L2lwdGNFeHQ6UmVnaXN0cnlJZD4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZmFmOTA0YWYtMmYyMC00MTg0LWI3ZjAtYWIxNzQxZGE2MzczIgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKE1hYyBPUykiCiAgICAgIHN0RXZ0OndoZW49IjIwMjItMDktMTZUMTY6Mzk6MzArMDI6MDAiLz4KICAgIDwvcmRmOlNlcT4KICAgPC94bXBNTTpIaXN0b3J5PgogICA8cGx1czpJbWFnZVN1cHBsaWVyPgogICAgPHJkZjpTZXEvPgogICA8L3BsdXM6SW1hZ2VTdXBwbGllcj4KICAgPHBsdXM6SW1hZ2VDcmVhdG9yPgogICAgPHJkZjpTZXEvPgogICA8L3BsdXM6SW1hZ2VDcmVhdG9yPgogICA8cGx1czpDb3B5cmlnaHRPd25lcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkNvcHlyaWdodE93bmVyPgogICA8cGx1czpMaWNlbnNvcj4KICAgIDxyZGY6U2VxLz4KICAgPC9wbHVzOkxpY2Vuc29yPgogIDwvcmRmOkRlc2NyaXB0aW9uPgogPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgIAo8P3hwYWNrZXQgZW5kPSJ3Ij8+IMG9ZQAAAAZiS0dEAAAAAAAA+UO7fwAAAAlwSFlzAAAimgAAIpoBvt37KgAAAAd0SU1FB+YJEA4nHeKdlGcAABbwSURBVHja7VtpdBTXlf6qq6q7el/U3ZK6taMdIbAQSAYBYrFZbBzbOMbByYkdEmeZzJyxjyeZiWcmM8cOjteZOJl4EgeCAcdOvOAYYxZjB2ywWY0BgQRoQRJaW2r1vlR1Vc0P/MrVWC1hx0vmHNc5fdSIVtW737v3u9+99zXw5fXl9eX1RVzXXXfddAAz1a+SkpKrNm7caP4810F91g84c+YM88gjjyx64YUXGu12eyPDMLUjtNlryS8FRVHgLHZQGg0SwTFIkojYyAC0w51BmqZPOhyOo5FI5O3ly5e/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'

# path to configuration file
config_path = os.path.join(os.path.dirname(__file__), 'autogui.cfg')
# path to changelog
changelog_path = os.path.join(os.path.dirname(__file__), 'autogui_changelog.txt')      
# path to personal config
personal_config = os.path.join(os.path.expanduser('~'), ".autogui_priv.cfg")
# path to GNU GENERAL PUBLIC LICENSE Version 3
license_path = os.path.join(os.path.dirname(__file__), 'COPYING')            

# initial values of variables
welcome = "Welcome to AutoGUI " + version + ",\na python-based GUI for running GPhL autoPROC"
win_title = 'AutoGUI ' + version
opened1 = False
opened2 = False
opened3 = True
disable_sub =True
disable_macro = False
disable_res = True
disable_spg = False
disable_ref = True
disable_free = True
disable_cust = False
vFlag = False
killflag = False
subdir = None
h5 = None
watch = False
EIGER = True
h52cbf = False
INHOUSE = False
checkprep = preplist.split()
prepcommands = ''
linkcommands = ''
imglinkcommands = ''
proclinkcommands = ''
custpars = ''
separator = '==============================================================================================================================='
folder = inpath
runnumber = 1
hits = []
hitno = 0
sweeps = []
IDs = []
PATHs = []
TEMPLATEs = []
STARTs = []
ENDs = []
oldcntr = 0
setsweeps = ''
cntr = oldcntr
listindex = 0
sweepcommands =''
tempsweeps=[]
m_list = []
start_t = 0
current_t = 0
timetext = ""
progword = ""
xds_inp = ""
cbffolder =''
tmpcbffolder = 'tempcbfs'
keepcbfs = False
cbflist =[]
BAR_MAX = 36
success = False
cutmod = False
findimgpath = ''
show_eiger = False
img_hit_list = []
ds_numimgs = ''
nslabs = 1 
numfoundsweeps = 0
beamcentremode = "header"
beamcentrex = "n/a"
beamcentrey = "n/a"
distance = "n/a"
wavelength = "n/a"
oscillation = "n/a"
overload = "n/a"
pixelsizex = "n/a"
pixelsizey = "n/a"
nopixelx = "n/a"
nopixely = "n/a"
headertwotheta = 0
untrusted_rectangles = []
untrusted_ellipses = []
untrusted_rectangle_coords = []
untrusted_ellipse_coords = []
untrusted_quad_coords = []
untrusted_quads = []
dectris_gap_coords = []
dectris_gaps = []
modified_beamcenter =""
xdsupdate = False
debug = False
show_errors = False
datasaving = True
silent = True
reroute_out = True
echo_out = False
csv_header = ['Date', 'Dataset', 'Success', 'Space group', 'Cell dimensions [Å]', 'Cell angles [°]', 'Isotropic diffraction limit [Å]', 'Anisotropic diffraction limits [Å]', 'Autoproc command line']
csv_entry = [] # 0 = proc_date, 1 = image template, 2 = success, 3 = space group, 4 = cell dimensions, 5 = cell angles, 6 = isotropic diff limit, 7 = anisotropic diff limits, 8 = command line for autoproc
ds_name = ''
proc_date = ''
#rec_date = '' not implemented yet
cleanup_args = '-not -name "*.html" -not -name "*.htm" -not -name "*.HTML" -not -name "*.png" -not -name "*.jpg" -not -name "HTM" -not -name "*.LP" -not -name "*.log" -print0 | xargs -I {} -0 rm "{}"'
useful_files_to_copy = ["CORRECT.LP", "aimless.log", "xscale_XSCALE.LP", "XDS.INP", "XDS_ASCII.HKL", "INTEGRATE.HKL", "remark200.pdb", "staraniso_remark200.pdb"]
beamcentreactions = ["header", "try possible transformations", "guess", "specified below"]
beamcentreactions_eiger = ["header", "specified below"]
iceringranges = [3.890,3.657,3.435,2.665,2.247,2.066,1.946,1.914,1.880,1.717,1.522,1.472,1.442,1.370,1.365,1.298,1.275,1.260,1.223,1.170,1.123] # ice rings according to M.Kumai, 1967

microED_pars = 'autoPROC_XdsKeyword_REFINECORRECT="ORIENTATION CELL AXIS BEAM"'  # XDS-tweak for processing of microED data

SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'

pointless = "pointless"                     # path to/ command to run Pointless

#definition of parameters for autoproc
param_d = ''                                        # output dir "-d"
param_I = ''                                        # image dir "-I"
param_h5 = ''                                       # .h5 master file "-h5"
param_R = ''                                        # resolution limiter "-R <low> <high>"
param_Ano = ''                                      # anomalous data "-Ano" if true
param_ref = ''                                      # path to reference MTZ "-ref"
param_free = ''                                     # path to MTZ with free R "-free"
param_M = ''                                        # run with. macro "-M"
param_symm = ''                                     # set space group "symm = ..."
param_cell = ''                                     # set cell parameters "cell = ..."
param_sweeps =''                                    # sweep definitions "-Id <idN>,<dirN>,<templateN>,<fromN>,<toN>"
param_extra =''                                     # definitions for inhouse setup
param_bad_imgs =''                                  # automatically exclude bad images (default behavior = yes)
param_cutcchalf=''                                  # determine high res cutoff based on CC(1/2) (default behavior = no)
param_nthreads = "-nthreads " + nprocs              # max number of threads
param_appended = ''                                 # parameters to be directly appended to the command line
param_exp = ''                                      # experimental parameters such as beamcenter, wavelength, distance, ...
param_untrusted = ''                                # XDS untrusted regions, including detector gaps, if masked
param_footprint = 'AutoProcSmallFootprint="yes"'    # Try to make less (useless) files

# Start in debug mode
if len(sys.argv) != 1:
    print('***DEBUG MODE***')
    print("All output will be written to 'autogui_debug.log'")
    print("Additional faults might show up in 'autogui_classic_faults.log'")
    print('')
    debug = True
    echo_out = False
    reroute_out = False
    fault_out = open(os.path.join(current_path, "autogui_classic_faults.log"), mode="w")
    faulthandler.enable(fault_out)

# thread for autoproc function to keep gui working
def autoproc_thread(window):
    time.sleep(0.5)
    bash_process = subprocess.Popen(bash_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        time.sleep(0.05)
        output = bash_process.stdout.readline()
        #print(output.strip())
        autoprocline = output.strip()
        window.write_event_value('-AUTOPROCLINE-', autoprocline)
        # Do something else
        return_code = bash_process.poll()
        if return_code is not None:
            time.sleep(1)
            # print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            for output in bash_process.stdout.readlines():
                #print(output.strip())
                time.sleep(0.05)
                autoprocline = output.strip()
                window.write_event_value('-AUTOPROCLINE-', autoprocline)
            time.sleep(1)    
            window.write_event_value('-THREADOFF-', '')
            break

#helper function to start autoproc thread
def autoproc_function(bash_command):
    threading.Thread(target=autoproc_thread, args=(window,), daemon=True).start()

# thread for mini-cbf conversion function to keep gui working
def cbfconversion_thread(window):
    time.sleep(0.5)
    #window['-LOGBROWSER-'].update(disabled = True)
    imgnum = 0
    imgids = []
    imgpath  = "/".join(h5.split("/")[:-1])
    imgpattern = re.compile("List of identifiers")
    if os.path.exists(cbffolder) == True:
        print('')
        print('Temporary folder with mini-cbf files seem to be already there, please check this!')
        print('')
        status = '  \u2398  Temporary files seem to be already there! Strange... Skipping EIGER HDF5 to mini-cbf conversion.'
        window.write_event_value('-STATUSUPDATE-', status) 
        window.write_event_value('-THREADON-', '')       
    else:
        os.makedirs(cbffolder)
        cbflist.append(cbffolder)
        #print(cbflist)
        print('')
        print("Created temporary folder for mini-cbf output", cbffolder)        
        find_command = 'find_images -h5 -l -d ' + imgpath +' > ./expectedimgs.tmp'
        find_process = subprocess.Popen(find_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            return_code = find_process.poll()
            if return_code is not None:
                with open ('./expectedimgs.tmp', 'rt') as findimages:
                    for line in findimages:
                        if imgpattern.search(line) != None:  # If pattern search finds a match,
                            imgids = line.split(",")
                            #print("")
                            #print(line)
                            #print("")
                            imgnum = int(imgids[4])
                findimages.close
                os.remove("./expectedimgs.tmp")
                break

        conversion_command = "hdf2mini-cbf -m " + h5
        conversionpattern = re.compile("output file will be image.*0\.cbf")
        print('')
        print("Running",conversion_command)
        print("Converting", str(imgnum), "images. This may take a while...")
        print('')
        b = 0
        progword = 'CONVERTING HDF5 TO MINI-CBF'
        window.write_event_value('-PROGRESSUPDATE-', progword) 
        window.write_event_value('-BARUPDATE-', b)
        conversion_process = subprocess.Popen(conversion_command, cwd=cbffolder, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            output = conversion_process.stdout.readline()
            output = output.strip()
            if conversionpattern.search(output) != None:
                convmessage = "Converted " + ((output.split('output file will be '))[-1])
                print(convmessage)
            # Do something else
            return_code = conversion_process.poll()
            i = (sum([len(files) for r, d, files in os.walk(cbffolder)]))
            file_count = str(i)
            if i >= 1:
                b = int((i / imgnum) * BAR_MAX)
            else:
                b = i    
            window.write_event_value('-BARUPDATE-', b)
            status = '  \u2398  Converting EIGER HDF5 to mini-cbf. This may take a while.                                                                                      Converted images: ' + file_count + ' of ' + str(imgnum)
            window.write_event_value('-STATUSUPDATE-', status) 
            if return_code is not None:
                # print('RETURN CODE', return_code)
                # Process has finished, read rest of the output
                i = (sum([len(files) for r, d, files in os.walk(cbffolder)]))
                file_count = str(i)
                if i >= 1:
                    b = int((i / imgnum) * BAR_MAX)
                else:
                    b = i
                window.write_event_value('-BARUPDATE-', b)
                status = '  \u2398  Converting EIGER HDF5 to mini-cbf. This may take a while.                                                                                      Converted images: ' + file_count + ' of ' + str(imgnum)
                window.write_event_value('-STATUSUPDATE-', status)
                for output in conversion_process.stdout.readlines():
                    time.sleep(0.05) 
                    output = conversion_process.stdout.readline()
                    output = output.strip()
                    if conversionpattern.search(output) != None:
                        convmessage = "Converted " + ((output.split('output file will be '))[-1])
                        #print(convmessage) 
                        window.write_event_value('-CONVERSIONLINE-', convmessage)
                time.sleep(1)
                window.write_event_value('-THREADON-', '')
                print('')
                print(separator)
                print("Conversion of EIGER HDF5 files to (temporary) mini-cbf files is done!")
                print(separator)
                print('')
                break

#helper function to start cbf-conversion thread
def cbfconversion_function(cbffolder, h5, BAR_MAX):    
    threading.Thread(target=cbfconversion_thread, args=(window,), daemon=True).start()

# thread for generic long function to keep gui working
def utility_thread(utility_command, silent):
    time.sleep(0.5)
    if silent == False:
        utility_process = subprocess.Popen(utility_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    else:
        utility_process = subprocess.Popen(utility_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True, shell=True)    
    while True:
        if silent == False:
            time.sleep(0.05)
            output = utility_process.stdout.readline()
            utilityline = output.strip()
            window.write_event_value('-UTILITYLINE-', utilityline)
        # Do something else
        return_code = utility_process.poll()
        if return_code is not None:
            # print('RETURN CODE', return_code)
            # Process has finished, read rest of the output
            time.sleep(1)
            if silent == False:
                for output in utility_process.stdout.readlines():
                    utilityline = output.strip()
                    window.write_event_value('-UTILITYLINE-', utilityline)
                    time.sleep(0.05)
            break
        
#helper function to start utility thread
def utility_function(utility_command, silent):
    threading.Thread(target=utility_thread, args=(utility_command, silent,), daemon=True).start()

# thread for macro-list retrieval and function to keep gui working 
def list_thread(window):
    time.sleep(0.5)
    window4['-MLIST-'].print(" Retrieving list of supported macros, please be patient ...")
    window4['-MLIST-'].print("")
    window4['-MLIST-'].print(" ---------------------------------------------------------------------------")
    list_command = "process -M "+ m_list_par + " > ./macros.tmp"
    list_process = subprocess.Popen(list_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    decider = False
    mlistpattern = re.compile("Macro name")
    macrolist = ""
    while True:
        return_code = list_process.poll()
        if return_code is not None:
            with open ('./macros.tmp', 'rt') as macros:
                for line in macros:
                    if (mlistpattern.search(line) != None):
                        decider = True
                    if  decider == True: 
                        #print(line)
                        macrolist = macrolist + line
            macros.close
            os.remove("./macros.tmp")
            #print(macrolist)
            window4.write_event_value('-MACROLIST-', macrolist)               
            break 

#helper function to start macro listing thread
def list_function(m_list_par):
    threading.Thread(target=list_thread, args=(window,), daemon=True).start()

# thread for log function to keep gui working        
def log_thread(window):
    time.sleep(0.2)
    file = open(filename)
    log = file.read()
    window2['-LOG-'].print(log)  

# helper function to run log thread
def log_read(filename):
    threading.Thread(target=log_thread, args=(window,), daemon=True).start()

# thread for running adxv and keeping gui working        
def adxv_thread(window):
    #os.system(adxv)
    adxv_process = subprocess.Popen(adxv, stdout=subprocess.PIPE, universal_newlines=True, shell=True)

# helper function to run adxv thread
def run_adxv(adxv):
    threading.Thread(target=adxv_thread, args=(window,), daemon=True).start()

# thread for displaying elapsed time
def timer_thread(window):
    checkfilepath = dumppath + "/output-files"
    checkfile = os.path.join(checkfilepath, 'stopped.txt')
    while True:
        current_t = time.time() - start_t
        currtime = time.gmtime(current_t)
        timetext = time.strftime("%H:%M:%S",currtime)
        window.write_event_value('-TIMEUPDATE-', timetext)
        time.sleep(1)     
        if os.path.exists(checkfile) == True:
            time.sleep(0.5)
            break

# helper function for timer-thread
def timer_function(dumppath):
    threading.Thread(target=timer_thread, args=(window,), daemon=True).start()

# thread for coordinate info deletion timer       
def coordel_thread(coordel_timeout):
    time.sleep(coordel_timeout)
    window_imageview.write_event_value('-COORDTIMESUP-', True)

# helper function for coordinate info deletion timer  
def coordel_timer(coordel_timeout):
    threading.Thread(target=coordel_thread, args=(coordel_timeout,), daemon=True).start()

# thread for icon_blinking
def blink_thread(window):
    checkfilepath = dumppath + "/output-files"
    checkfile = os.path.join(checkfilepath, 'noblink.txt')
    time.sleep(1.5)
    while True:      
        window.write_event_value('-BLINKUPDATE-', blink_color2)
        time.sleep(1)
        window.write_event_value('-BLINKUPDATE-', blink_color1)
        if os.path.exists(checkfile) == True:
            #print('blinking stopped')
            #print('')
            time.sleep(1)
            break
        else:
            time.sleep(1)


# helper function for icon-blinking-thread
def blink_function(dumppath, blink_color1, blink_color2):
    threading.Thread(target=blink_thread, args=(window,), daemon=True).start()    

# thread for progress bar       
def progress_thread(window):
    progstats = [re.compile(" href=.*\.setup\">"), re.compile(" href=.*\.index\">"), re.compile(" href=.*\.integ\">"), re.compile(" href=.*\.postref\">"), re.compile(" href=.*\.process\">"), re.compile(" href=.*\.scale\">"), re.compile(" href=.*\.analyse\">"), re.compile(" href=.*\.finish\">")]  # determine states from entry in html sidebar menu
    pw =['PROCESSING STARTED','SPOT SEARCH & INDEXING','INTEGRATION (INITIAL)','POST-REFINEMENT','INTEGRATION (FURTHER)','SCALING','ANISOTROPY ANALYSIS','FINISHED'] # progress states
    status = 0
    prev_status = 0
    b = status
    sweep_counter = 1
    fail_timeout = 300
    if (numfoundsweeps > 1) and (status < 5):
        progword = "Sweep " + str(sweep_counter) + " of "+ str(numfoundsweeps)+ ": " + pw[status]
    else:    
        progword = pw[status]
    time.sleep(0.5)
    window.write_event_value('-PROGRESSUPDATE-', progword) 
    window.write_event_value('-BARUPDATE-', b)
    stuffpath = dumppath + "/output-files"
    side_html_menu = os.path.join(stuffpath, "summary.html.menu")
    while True:
        time.sleep(2)
        if os.path.exists(side_html_menu) == True:
            with open (side_html_menu, 'rt') as side_menu_items:
                for line in side_menu_items:
                    line = line.strip() 
                    for progstat in progstats:
                        if progstat.search(line) != None:
                            status = progstats.index(progstat)
                if status < prev_status:
                    sweep_counter = sweep_counter + 1
                if (numfoundsweeps > 1) and (status < 5):
                    progword = "Sweep " + str(sweep_counter) + " of "+ str(numfoundsweeps)+ ": " + pw[status]
                else:    
                    progword = pw[status]
                prev_status = status
            side_menu_items.close() 

        elif os.path.exists("./summary.tar.gz") == True:   
            status = 7
            if (numfoundsweeps > 1) and (status < 5):
                progword = "Sweep " + str(sweep_counter) + " of "+ str(numfoundsweeps)+ ": " + pw[status]
            else:    
                progword = pw[status]
            break
        else:  
            if (numfoundsweeps > 1) and (status < 5):
                progword = "Sweep " + str(sweep_counter) + " of "+ str(numfoundsweeps)+ ": " + pw[status]
            else:    
                progword = pw[status]
            fail_timeout = fail_timeout - 1
            if fail_timeout == 0:
                break 

        b = int(((status + 1) / 8) * BAR_MAX)
        window.write_event_value('-PROGRESSUPDATE-', progword) 
        window.write_event_value('-BARUPDATE-', b)
        if status >= 7:
            break
    

# helper function to run progress thread
def progress_bar(dumppath, BAR_MAX, numfoundsweeps):
    threading.Thread(target=progress_thread, args=(window,), daemon=True).start()
    
       
# helper function to run sweep-finding
def find_sweeps(imgpath, EIGER):
    time.sleep(0.5)
    sweeppattern = re.compile("  /")
    linenum = 0 
    hits = []
    print('')
    print("Finding images ...")
    if EIGER == True:
        find_command = 'find_images -h5 -d ' + imgpath +' > ./findimages.tmp'
    else:    
        find_command = 'find_images -d ' + imgpath +' > ./findimages.tmp'
    find_process = subprocess.Popen(find_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        return_code = find_process.poll()
        if return_code is not None:
            with open ('./findimages.tmp', 'rt') as findimages:
                for line in findimages:
                    linenum += 1
                    if sweeppattern.search(line) != None:  # If pattern search finds a match,
                        hits.append(line.rstrip('\n'))            

            findimages.close
            os.remove("./findimages.tmp")
            return hits
            break

# helper function to run pointless, parse and check log
def pointless_function():
    time.sleep(0.5)
    plhits = []
    inspg = ''
    outspg = ''
    pllinenum = 0
    plhitline = 0
    plpattern1 = re.compile("Space group from HKLIN file")
    plpattern2 = re.compile("Best Solution")
    pl_command = pointless + ' hklin isotropic.mtz hklout pointless_isotropic.mtz > ./output-files/re-pointless.log; pointless hklin anisotropic.mtz hklout pointless_anisotropic.mtz'
    pl_process = subprocess.Popen(pl_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        return_code = pl_process.poll()
        if return_code is not None:
            with open ('./output-files/re-pointless.log', 'rt') as pointlessout:
                for line in pointlessout:
                    #print(line)
                    pllinenum += 1
                    if plpattern1.search(line) != None:  
                        inspg = (line.rstrip('\n'))               
                    if plpattern2.search(line) != None:  
                        plhitline = pllinenum + 10
                        outspg = (line.rstrip('\n')) 
                    if pllinenum < plhitline:
                        plhits.append(line.rstrip('\n'))

            inspg = " ".join(inspg.split())

            window_ptless['-POINTLESS-'].print(inspg)
            print('')
            print('POINTLESS says:')
            print(inspg)

            for plhit in plhits:
                window_ptless['-POINTLESS-'].print(plhit)
                #print(plhit)

            inspg = "".join(((inspg.split(":"))[1]).split())
            outspg = "".join(((outspg.split("group"))[1]).split())
            
            window_ptless['-POINTLESS-'].print('')
            window_ptless['-POINTLESS-'].print('--------------------------------------------------------------------------')

            if inspg == outspg:
                window_ptless['-POINTLESS-'].print('')
                window_ptless['-POINTLESS-'].print("It seems that your space group is already correct")
                print("It seems that your space group is already correct.")
                window_ptless['-PL_STAT-'].update(value = "No different space group found. \nCarry on, nothing to see here!", text_color = "white", background_color = "dark green")
                os.remove("pointless_isotropic.mtz")
                os.remove("pointless_anisotropic.mtz")
                
            else:
                outfileiso = outspg + "_isotropic.mtz"
                outfileaniso = outspg + "_anisotropic.mtz"
                window_ptless['-POINTLESS-'].print('')
                window_ptless['-POINTLESS-'].print("Isotropic MTZ with space group from POINTLESS is:", outfileiso)
                window_ptless['-POINTLESS-'].print('')
                window_ptless['-POINTLESS-'].print("Anisotropic MTZ with space group from POINTLESS is:", outfileaniso)
                print("Isotropic MTZ with space group from POINTLESS is:", outfileiso)
                print("Anisotropic MTZ with space group from POINTLESS is:", outfileaniso)
                message = "Different space group " + outspg + " found! \nProceed with the corresponding MTZs or reprocess data!"
                print("")
                print(message)
                window_ptless['-PL_STAT-'].update(value = message, text_color = "white", background_color = "dark red")
                copy_cmd = "cp pointless_isotropic.mtz " + outfileiso + "; cp pointless_anisotropic.mtz " + outfileaniso
                os.system(copy_cmd)
                os.remove("pointless_isotropic.mtz")
                os.remove("pointless_anisotropic.mtz")
            break        

# thread to expand freeR flags in Reference MTZ to high resolution
def refmtzexpand_thread(mtzfilein, refmtzout, set_reso):
    try:
        dmp_command = 'mtzdmp ' + mtzfilein +' > ./mtzdmp.tmp'
        dmp_process = subprocess.Popen(dmp_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        mtz_spg_pattern = re.compile(' * Space group = ')
        mtz_cell_pattern = re.compile(' * Cell Dimensions :')
        mtz_reso_pattern = re.compile(' *  Resolution Range :')
        mtz_columns_pattern = re.compile(' * Column Labels :')
        mtz_spg = ''
        mtz_cell = ''
        mtz_free_label = ''
        linenum = 0
        celllinetogo = None
        labellinetogo = None
        while True:
            return_code = dmp_process.poll()
            if return_code is not None:
                with open ('./mtzdmp.tmp', 'rt') as mtzdmp:
                    for line in mtzdmp:
                        linenum += 1
                        if mtz_spg_pattern.search(line) != None:  # If pattern search finds a match,
                            mtz_spg = ((re.split(r'\'', line))[1])
                            print('Space group:')
                            print(mtz_spg)
                        if mtz_cell_pattern.search(line) != None:  # If pattern search finds a match,
                            celllinetogo = linenum +2
                        if linenum == celllinetogo:
                            print("Cell:")
                            mtz_cell = (re.sub(r'^\s+', '', line)).strip()
                            mtz_cell = re.sub(r'\s+', ' ', mtz_cell)
                            print(mtz_cell) 
                        if mtz_columns_pattern.search(line) != None:  # If pattern search finds a match,
                            labellinetogo = linenum +2
                        if linenum == labellinetogo:
                            print("Free-R label:")
                            labels = line.split()
                            for label in labels:
                                freehit = re.search('free|FREE|Free', label)
                                if freehit != None:
                                    mtz_free_label = label.strip()
                            print(mtz_free_label)         
                mtzdmp.close
                os.remove("./mtzdmp.tmp")
                break

        print('Expand to', set_reso, 'Å')
        print('')
        unique_command = """unique HKLOUT UNIQUE_temp.mtz << EOF
        TITLE  Reference MTZ expansion via AutoGUI
        LABOUT F=FUNI SIGF=SIGFUNI
        SYMMETRY '""" + mtz_spg + """'
        RESOL """ + set_reso + """
        CELL """ + mtz_cell + """
        EOF"""
        unique_process = subprocess.Popen(unique_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            return_code = unique_process.poll()
            if return_code is not None:
                print('unique: done.')
                break    

        cad_command = """cad HKLIN2 ./UNIQUE_temp.mtz HKLIN1 """ + mtzfilein + """ HKLOUT CAD_temp.mtz << EOF

        LABIN FILE 1 ALLIN
        LABIN FILE 2 ALLIN
        END
        EOF"""
        cad_process = subprocess.Popen(cad_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            return_code = cad_process.poll()
            if return_code is not None:
                print('cad: done.')
                break     

        freer_command = """freerflag HKLIN ./CAD_temp.mtz HKLOUT FREER_temp.mtz << EOF
        COMPLETE FREE="""+ mtz_free_label +"""
        END
        EOF"""
        freer_process = subprocess.Popen(freer_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            return_code = freer_process.poll()
            if return_code is not None:
                print('freerflag: done.')
                break    

        mtzutils_command = """mtzutils HKLIN ./FREER_temp.mtz HKLOUT """ + refmtzout + """ << EOF
        EXCLUDE FUNI SIGFUNI
        END
        EOF"""
        mtzutils_process = subprocess.Popen(mtzutils_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        while True:
            return_code = mtzutils_process.poll()
            if return_code is not None:
                print('mtzutils: done.')
                break
        time.sleep(0.2)    
        os.remove("./UNIQUE_temp.mtz")
        os.remove("./CAD_temp.mtz")
        os.remove("./FREER_temp.mtz")
        print('Temporary files removed.')
    except:
        print('There was an error processing your input MTZ!')         
    window_makeref.write_event_value('-REFMTZDONE-', True)
    
# helper function to expand freeR flags in Reference MTZ to high resolution
def refmtzexpand(mtzfilein, refmtzout, set_reso) :
    threading.Thread(target=refmtzexpand_thread, args=(mtzfilein, refmtzout, set_reso), daemon=True).start()

# helper function to kill sub-processes
def killtree(pid, including_parent):
    parent = psutil.Process(pid)
    print('')
    print('Aborting...')
    print('')
    print('Process ID is:')
    print(pid)
    print('Parent process information:')
    print(parent)
    print('')
    for child in parent.children(recursive=True):
        print("Stopped child-process: ", child)
        time.sleep(0.5)
        try:
            child.kill()
        except psutil.Error as error:
            stringerror = str(error)
            print ("Error: " + stringerror)
    if including_parent == True:
        print("Stopped parent-process: ", parent)
        time.sleep(0.5)
        try:
            parent.kill()
        except psutil.Error as error:
            stringerror = str(error)
            print ("Error: " + stringerror)
        
# helper function to create autogui_log.html
def HTML_log(runnumber, dumppath, refresh):
    f = open("./autogui_log.html", "w")
    f.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n')
    f.write('"http://www.w3.org/TR/html4/loose.dtd">\n')
    f.write('<html>\n')
    f.write('<head>\n') 
    if refresh == True:
        title = '    <title>AutoProc run ' + str(runnumber) + ': Self-refreshing processing log</title>\n'
        f.write(title)
        f.write('	<meta http-equiv="refresh" content="30" >\n')
    else:
        title = '    <title>AutoProc Run ' + str(runnumber) +': Processing finished</title>\n'
        f.write(title)
    f.write('    <style type="text/css">\n') 
    f.write('        html {\n') 
    f.write('            overflow: auto;\n') 
    f.write('        }\n') 
    f.write('\n')          
    f.write('        html,\n') 
    f.write('        body,\n') 
    f.write('        div,\n') 
    f.write('        iframe {\n') 
    f.write('            margin: 0px;\n') 
    f.write('            padding: 0px;\n') 
    f.write('            height: 100%;\n') 
    f.write('            border: none;\n') 
    f.write('        }\n') 
    f.write('\n')          
    f.write('        iframe {\n') 
    f.write('            display: block;\n') 
    f.write('            width: 100%;\n') 
    f.write('            border: none;\n') 
    f.write('            overflow-y: auto;\n') 
    f.write('            overflow-x: hidden;\n') 
    f.write('        }\n') 
    f.write('    </style>\n') 
    f.write('</head>\n') 
    f.write('<body>\n')
    f.write('	<iframe src="')
    #f.write(dumppath)
    #f.write('/output-files/summary.html"\n')
    f.write('./output-files/summary.html"\n')         #better to use relative path
    f.write('	            frameborder="0"\n') 
    f.write('	            marginheight="0"\n') 
    f.write('	            marginwidth="0"\n') 
    f.write('	            width="100%"\n') 
    f.write('	            height="100%"\n') 
    f.write('	            scrolling="auto">\n') 
    f.write('	  </iframe>\n')
    f.write('</body>\n')
    f.write('</html>\n')
    f.close()    

# helper function to load default template
def def_temp():
   window3['-PARDAT-'].print('## Uncomment parameters you need by removing the # at the start of the corresponding lines')
   window3['-PARDAT-'].print('## More parameters (and explanations) can be found at http://www.globalphasing.com/autoproc/manual/appendix1.html')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Should existing files be overwritten? (default is to stop)')
   window3['-PARDAT-'].print('#StopIfSubdirExists="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Images for Background estimation (important for Pilatus fineslicing, can be deactivated for Saturn)')
   window3['-PARDAT-'].print('#autoPROC_XdsKeyword_BACKGROUND_RANGE="1 100"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## What to do, if several datasets are detected (default is to scale them together)')
   window3['-PARDAT-'].print('#ScaleAllDatasetsTogether="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## If using Saturn 944+ images, activate this')
   window3['-PARDAT-'].print('#autoPROC_XdsDistanceFacSaturnp="-1"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Define beam centre or use advanced search, if not found correctly')
   window3['-PARDAT-'].print('## set explicit beam centre')
   window3['-PARDAT-'].print('#beam="519.5 521.5"')
   window3['-PARDAT-'].print('## try to find beam by exchanging/inverting X/Y')
   window3['-PARDAT-'].print('#BeamCentreFrom="getbeam:init"')
   window3['-PARDAT-'].print('## search for beam centre')
   window3['-PARDAT-'].print('#BeamCentreFrom="getbeam:refined"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Adjust if you just want to process onlypart of your dataset')
   window3['-PARDAT-'].print('#XdsSpotSearchNumImages="999999"')
   window3['-PARDAT-'].print('#XdsSpotSearchAngularRange=180')
   window3['-PARDAT-'].print('#XdsSpotSearchNumImagesAngularRange="10.0"')
   window3['-PARDAT-'].print('#XdsSpotSearchNumRanges=4')
   window3['-PARDAT-'].print('')     
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Advanced settings (I hope you know what you are doing...):')
   window3['-PARDAT-'].print('## ---------------------------------------------------------')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Path to pilatus geometry correction files, if available')
   window3['-PARDAT-'].print('#autoPROC_ExtraFilesDir="../../"')
   window3['-PARDAT-'].print('## For PetraIII P11:')
   window3['-PARDAT-'].print('# autoPROC_ExtraFilesDir="/nero/plu11/Projects/Templates/P11_corr/"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Pilatus 2M gap definitions: (should not be necessary but may help):')
   window3['-PARDAT-'].print('#autoPROC_Img2Xds_Pilatus2MGaps=" 0 1476  195  213|  0 1476  407  425|  0 1476  619  637|  0 1476  831  849|  0 1476 1043 1061|  0 1476 1255 1273|  0 1476 1467 1485|487  495    0 1680|981  989    0 1680"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Pilatus 6M gap definitions: (should not be necessary but may help):')
   window3['-PARDAT-'].print('#autoPROC_Img2Xds_Pilatus6MGaps="487  495    0 2528| 981  989    0 2528|1475 1483    0 2528|1969 1977    0 2528|   0 2464  195  213|   0 2464  407  425|   0 2464  619  637|   0 2464  831  849|   0 2464 1043 1061|   0 2464 1255 1273|   0 2464 1467 1485|   0 2464 1679 1697|   0 2464 1891 1909|   0 2464 2103 2121|   0 2464 2315 2333"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Allow compressed images')
   window3['-PARDAT-'].print('#FindImages_AllowCompressedImages="yes"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Activate these and play with the values if indexing is difficult/fails:')
   window3['-PARDAT-'].print('#XdsOptimizeIdxrefAlways="yes"')
   window3['-PARDAT-'].print('#RunIdxrefStartWithTop="1000"')
   window3['-PARDAT-'].print('#autoPROC__XdsKeyword_SPOT_RANGE="1 10|91 100"')
   window3['-PARDAT-'].print('#XdsSpotSearchNumImages="20"')
   window3['-PARDAT-'].print('#XdsSpotSearchAngularRange="60"')
   window3['-PARDAT-'].print('#XdsSpotSearchNumRanges="4"')
   window3['-PARDAT-'].print('#RunIdxrefExcludeIceRingShells="yes"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Automatically optimize data processing for anomalous signal, if detected (default = yes)')
   window3['-PARDAT-'].print('#autoPROC_AnomalousSignal_AdjustAutomatically="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## If scaling several datasets together, it might be required to prevent stopping after scaling errors.')
   window3['-PARDAT-'].print('#StopAfterScalingError="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Manually tweak hires cutoff parameters') 
   window3['-PARDAT-'].print('## (Value pairs are for scaling cycles, each cycle has a pair of "RUN:FULL_DATASET". FULL_DATASET value of last pair is important!)')
   window3['-PARDAT-'].print('#ScaleAnaCChalfCut_123="-1.0:-1.0 0.0:0.0 0.1:0.1 0.3:0.3"')
   window3['-PARDAT-'].print('#ScaleAnaCompletenessCut_123="0.0:0.0"')
   window3['-PARDAT-'].print('#ScaleAnaISigmaCut_123="0.1:0.1 0.5:0.5 0.5:1.0 1.0:2.0"')
   window3['-PARDAT-'].print('#ScaleAnaRmeasallCut_123=""99.9999:99.9999"')
   window3['-PARDAT-'].print('#ScaleAnaRmergeCut_123="99.9999:99.9999"')
   window3['-PARDAT-'].print('#ScaleAnaRpimallCut_123="99.9999:99.9999"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Which programs to use for scaling (default is Aimless, both "no" is Scala)')
   window3['-PARDAT-'].print('#autoPROC_ScaleWithXscale="yes"')
   window3['-PARDAT-'].print('#autoPROC_ScaleWithAimless="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## If you have troubles with (ice) rings, activate and modify this')
   window3['-PARDAT-'].print('#XdsExcludeIceRingsAutomatically="no"')
   window3['-PARDAT-'].print('#XdsExcludeIceRingsAutomaticallyIfKnownValue="yes"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_MinSpot2="20"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_Prec="0.01"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_IceRingMinScore="0.1"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_IceRingWidth=" 0.03"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_IceRingWidthMult=" 1.0"')
   window3['-PARDAT-'].print('#Xds_Spot2Res_IceRings=" 3.90 strong | 3.67 strong | 3.44 strong | 2.67 strong | 2.25 strong | 2.07 strong | 1.95 weak | 1.92 strong | 1.88 weak | 1.72 weak"')
   window3['-PARDAT-'].print('#RunIdxrefExcludeIceRingShells="no"')
   window3['-PARDAT-'].print('#AutoProcScaleStatsUseMrfanaIgnoreIceRingShells="no"')
   window3['-PARDAT-'].print('#AutoProcScaleStatsUseMrfanaIgnoreIceRingReso=""')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Disable/enable anisotropy correction on merged intensity data (default = yes)')
   window3['-PARDAT-'].print('#AutoProcScale_RunStaraniso="no"')
   window3['-PARDAT-'].print('')
   window3['-PARDAT-'].print('## Generate amplitudes (if possible) for F(early)-F(late) difference fourier maps (default = yes)')
   window3['-PARDAT-'].print('#autoPROC_ScaleEarlyLateCreate="no"')
    
# helper function to load parameter-file        
def read_param(parfile):
    file = open(parfile)
    params = file.read()
    window3['-PARDAT-'].print(params)
    file.close()    

# helper function to save parameter-file        
def save_param(pardat, custpars):
    file = open(pardat, "w")
    file.write(custpars)
    file.close()

# helper function to extract parameters from XDS.INP file       
def extract_xds(xds_inp):
    xds_keywords = []
    xds_values = []
    xds_excludelist =["JOB", "SPACE_GROUP_NUMBER", "ORGX", "ORGY", "UNIT_CELL_CONSTANTS", "LIB", "NAME_TEMPLATE_OF_DATA_FRAMES", "FRIEDEL'S_LAW", "REFINE(IDXREF)", "REFINE(INTEGRATE)", "REFINE(CORRECT)", "MAXIMUM_NUMBER_OF_JOBS", "MAXIMUM_NUMBER_OF_PROCESSORS"]
    xds_pattern1 = re.compile("^\s*!")
    xds_pattern2 = re.compile("\s*!")
    xds_pattern3 = re.compile("[A-Z_0-9'()-/]+=")
    xds_beam_x = ''
    xds_beam_y = ''

    with open (xds_inp, 'rt') as xdsinp:
        for line in xdsinp:
            if xds_pattern1.search(line) == None:
                if xds_pattern2.search(line) != None:
                    x = re.split(xds_pattern2, line)
                    line = x[0]
                if xds_pattern3.search(line)!= None:
                    xdskwds = re.findall(xds_pattern3, line)
                    xdsvals = re.split(xds_pattern3, (line.rstrip('\n')))
                    #print(xdsvals)
                    xdsvals.pop(0)
                    #print(xdskwds)
                    #print(xdsvals)
                    for xdskwd in xdskwds:  
                        xdskwd = xdskwd.replace('=','')
                        xds_keywords.append(xdskwd)
                    for xdsval in xdsvals:
                        xdsval = xdsval.strip()
                        xds_values.append(xdsval)
    xdsinp.close()                    

    window3['-PARDAT-'].print('# === Parameters extracted from existing XDS.INP file ===')
    window3['-PARDAT-'].print('')
    window3['-PARDAT-'].print('# Parameters that have been commented out should be set elsewhere in AutoGUI.')
    window3['-PARDAT-'].print('# (Uncomment them, if required.)')
    window3['-PARDAT-'].print('')
    for i in range(len(xds_keywords)):
        if xds_keywords[i] not in xds_excludelist:
            mod_keyword = re.sub(r'[-()\'\/]', '', xds_keywords[i]) 
            string = 'autoPROC_XdsKeyword_' + mod_keyword + '="' + xds_values[i] + '"' 
            window3['-PARDAT-'].print(string)
        else:
            mod_keyword = re.sub(r'[-()\'\/]', '', xds_keywords[i])
            string = '# autoPROC_XdsKeyword_' + mod_keyword + '="' + xds_values[i] + '"'
            window3['-PARDAT-'].print(string)
            
        if xds_keywords[i] == "ORGX":
            xds_beam_x = xds_values[i]
            #print(xds_values[i])
            if xds_beam_x != '' and xds_beam_y != '':
                string = 'beam' + '="' + xds_beam_x + ' ' + xds_beam_y + '"'
                window3['-PARDAT-'].print(string)
        if xds_keywords[i] == "ORGY":
            xds_beam_y = xds_values[i]
            #print(xds_values[i])
            if xds_beam_x != '' and xds_beam_y != '':
                string = 'beam' + '="' + xds_beam_x + ' ' + xds_beam_y + '"'
                window3['-PARDAT-'].print(string)   

# Helper function for collapsible sections (collapsed)
def collapse(layout, key):
   return sg.pin(sg.Column(layout, key=key, visible = False))

# helper function to display fisnish-message        
def finish_popup(runnumber, dumppath, folder, cutmod, success):
    time.sleep(1)
    if success == True:
        log_pattern1 = re.compile("\s*===== finishing processed and scaled data from XDS")
        log_pattern2 = re.compile("\s*Spacegroup name\s+")
        log_pattern3 = re.compile("\s*Unit cell parameters\s+")
        log_pattern4 = re.compile("\s*High resolution limit\s+")
        log_pattern5 = re.compile("\s*Diffraction limits & principal axes of ellipsoid fitted to diffraction cut-off surface:")
        process_list = []
        process_no = 0
        process_hit_cntr = 0
        log_check = 1
        log_line = 0
        hit_line = 0
        finish_message = []
        file = os.path.join(dumppath, "log.txt")
        log = open (file, 'rt')
        process_list = re.findall(log_pattern1, log.read())
        process_no = len(process_list)
        log.close()
        
        with open (file, 'rt') as log:
            for line in log:
                log_line += 1
                if log_check == 1 :
                    if log_pattern1.search(line) != None:  # If pattern search finds a match
                        process_hit_cntr += 1
                        #print(str(process_hit_cntr))
                        if process_hit_cntr == process_no:
                            log_check = 2
                if log_check == 2 :
                    if log_pattern2.search(line) != None:
                        mval = re.split(log_pattern2, (line.rstrip('\n')))
                        finish_message.append(mval[1])
                        log_check = 3
                if log_check == 3 :
                    if log_pattern3.search(line) != None:
                        mval = re.split(log_pattern3, (line.rstrip('\n')))
                        mvals = re.split('\s+', mval[1])
                        finish_message.append(mvals[0])
                        finish_message.append(mvals[1])
                        finish_message.append(mvals[2])
                        finish_message.append(mvals[3])
                        finish_message.append(mvals[4])
                        finish_message.append(mvals[5])
                        log_check = 4
                if log_check == 4 :
                    if log_pattern4.search(line) != None:
                        mval = re.split(log_pattern4, (line.rstrip('\n')))
                        mvals = re.split('\s+', mval[1])
                        finish_message.append(mvals[2])
                        log_check = 5
                if log_check == 5 :
                    if log_pattern5.search(line) != None:
                        hit_line = log_line + 4
                    if (log_line) < hit_line and log_line > (hit_line - 4):
                        mvals = re.split('\s\s+', (line.rstrip('\n')))
                        anisocomp = mvals[5]
                        #anisocomp = re.sub('\s*', '', mvals[5])
                        anisocomp = re.sub("_", "", anisocomp)
                        finish_message.append('{:<26s}'.format(anisocomp))
                        finish_message.append('{:>5s}'.format(mvals[1]))                 
                             
        # print(finish_message)
        print('')
        print('===============================================================================================================================')
        print('')
        if process_no >= 2:
            success_status = 'Data processing of job no. '+ str(runnumber)+ ' in\n'+ dumppath+ '\nhas finished.\n\nResults from processing of ' + str(process_no - 1) + ' sweeps:'
        else:
            success_status = 'Data processing of job no. '+ str(runnumber)+ ' in\n'+ dumppath+ '\nhas finished.'
        print(success_status)
        if len(finish_message) > 10:
            csv_entry.append('True')
            success_sg = finish_message[0]
            csv_entry.append(success_sg)
            print('')
            print('Space group:')
            print(success_sg)
            success_cell = finish_message[1] + ' Å, ' + finish_message[2] + ' Å, ' + finish_message[3] + ' Å, ' + finish_message[4] + '°, ' + finish_message[5] + '°, ' + finish_message[6] + '°'
            print('Unit cell:')
            print(success_cell)
            csv_entry.append((finish_message[1] + ', ' + finish_message[2] + ', ' + finish_message[3]))
            csv_entry.append((finish_message[4] + ', ' + finish_message[5] + ', ' + finish_message[6]))
            success_iso = finish_message[7] + ' Å'
            csv_entry.append(finish_message[7])
            if cutmod == True:
                success_cutoff = 'Isotropic high resolution limit (based on I/sig(I) >= 2.0, CC(1/2) >= 0.3, Rpim <= 0.6):'
            elif cutmod == False:
                success_cutoff = 'Isotropic high resolution limit (based mainly on CC(1/2) >= 0.3):'
            else:
                success_cutoff = 'Isotropic high resolution limit (based on I/sig(I) >= '+ cutmod[0] +', CC(1/2) >= '+ cutmod[1] +', Rpim <= '+ cutmod[2] +'):'
            print(success_cutoff)
            print(success_iso)
            success_aniso = finish_message[8] +': '+ finish_message[9] + ' Å\n' + finish_message[10] +': '+ finish_message[11] + ' Å\n' + finish_message[12] +': '+ finish_message[13] + ' Å'
            print('Anisotropic diffraction limits (local I/sig(I) >= 1.2):')
            print(success_aniso)
            csv_entry.append((finish_message[9] + ', ' + finish_message[11] + ', ' + finish_message[13]))
            print('')
            print('===============================================================================================================================')
            print('')
            log.close

            layout_success = [[sg.Frame(layout=[
                              [sg.Text("")],
                              [sg.Column(layout=[  
                                  [sg.Text(success_status, justification = 'center', font = 'Arial 12', background_color = theme_color1, text_color = "dark green")]], element_justification = 'center', background_color = theme_color1)],
                              [sg.Text("")],
                              [sg.HorizontalSeparator(color = None)],
                              [sg.Text('Space group:')],
                              [sg.Text(success_sg ,text_color = theme_color, font = "Courier 10 bold")],
                              [sg.Text("")],
                              [sg.Text('Unit cell:')],
                              [sg.Text(success_cell ,text_color = theme_color, font = "Courier 10 bold")],
                              [sg.Text("")],
                              [sg.Text(success_cutoff)],
                              [sg.Text(success_iso ,text_color = theme_color, font = "Courier 10 bold")],
                              [sg.Text("")],
                              [sg.Text('Anisotropic diffraction limits (local I/sig(I) >= 1.2):')],
                              [sg.Text(success_aniso ,text_color = theme_color, font = "Courier 10 bold")],
                              [sg.Text('')]],title='\u2714 Success!', title_color="dark green", font = "Arial 12", element_justification = 'center', relief=sg.RELIEF_GROOVE)],
                              [sg.Button('Yay!', highlight_colors = (theme_color, theme_color))]]           
            window_success = sg.Window('Success!', layout_success, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                event_success, values_success = window_success.read()
                if event_success == sg.WIN_CLOSED or event_success == 'Yay!':
                    window_success.close()
                    layout_success = None
                    window_success = None
                    gc.collect()
                    break
        else:
            print("An Error occured during the finalizing stage.\nPlease check the log files!")
            print('')
            success = False
            
    if success == False:
        print('')
        print('===============================================================================================================================')
        print('')
        print('Something went terribly wrong!')
        fail_status = 'Data processing of job no. '+ str(runnumber)+ ' in\n'+ folder+ '\nhas failed.'
        print(fail_status)
        print('')
        print('===============================================================================================================================')
        print('')
        layout_fail = [[sg.Frame(layout=[
                          [sg.Text("")],  
                          [sg.Column(layout=[  
                              [sg.Text(fail_status, justification = 'center', font = 'Arial 12', background_color = theme_color1, text_color = "dark red")]], element_justification = 'center', background_color = theme_color1)],
                          [sg.Text("")],  
                          [sg.HorizontalSeparator(color = None)],
                          [sg.Text('Uh oh!', justification = "center", font = "Arial 12")],
                          [sg.Text('Somewhere something went terribly wrong ...', text_color = theme_color, justification = "center")],
                          [sg.Text('')]],title='\u26a0 Fail!', title_color="dark red", font = "Arial 12", element_justification = 'center', relief=sg.RELIEF_GROOVE)],
                       [sg.Button('Cry!', highlight_colors = (theme_color, theme_color))]]            
        window_fail = sg.Window('Fail!', layout_fail, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_fail, values_fail = window_fail.read()
            if event_fail == sg.WIN_CLOSED or event_fail == 'Cry!':
                window_fail.close()
                layout_fail = None
                window_fail = None
                gc.collect()
                break
        csv_entry.append('False')
        csv_entry.append('N/A')
        csv_entry.append('N/A')
        csv_entry.append('N/A')
        csv_entry.append('N/A')
        csv_entry.append('N/A')    
    csv_entry.append(auto_command) 
    export_csv(dumppath, csv_header, csv_entry)

#export csv table
def export_csv(dumppath, csv_header, csv_entry):
    filetoexport = os.path.join(dumppath, "useful_files/datasets.csv")
    try:
        f = open(filetoexport, "w")
        line = ';'.join(csv_header)
        f.write(line +'\n')
        table_line = ';'.join(csv_entry)
        f.write(table_line +'\n')
        f.close()
        print('')
        print('Exported metadata CSV to:', filetoexport)
        print('') 
    except:
        print('')
        print('Unable to export CSV!')
        print('')

# helper function to display found datasets in folder
def show_sets(show_eiger, findimgpath):
    sweeps = []
    hits = []
    hitno = 0
    found = []
    error = False

    time.sleep(0.5)
    sweeppattern = re.compile("  /")
    errorpattern = re.compile("ERROR")
    linenum = 0 
    hits = []
    print('')
    print("Finding images ...")
    if show_eiger == True:
        find_command = 'find_images -h5 -d ' + findimgpath +' > ./findimages.tmp'
    else:    
        find_command = 'find_images -d ' + findimgpath +' > ./findimages.tmp'
    find_process = subprocess.Popen(find_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        return_code = find_process.poll()
        if return_code is not None:
            with open ('./findimages.tmp', 'rt') as findimages:
                for line in findimages:
                    linenum += 1
                    if sweeppattern.search(line) != None:  # If pattern search finds a match,
                        hits.append(line.rstrip('\n'))
                    if errorpattern.search(line) != None:  # If pattern search finds a match,
                        error = True            

            findimages.close
            os.remove("./findimages.tmp")
            break

    if error == False:    
        for hit in hits:
            hitno += 1
            hit = " ".join(hit.split(":"))
            hit = " ".join(hit.split(" - "))
            hit = " ".join(hit.split())
            hit = str(hitno) + " " + hit
            sweep = hit.split(" ")
            sweeps.append(sweep)
            #print(hit)

        if len(sweeps[0]) < 5:
            print('')
            print("No datasets found!")
            print('')
            sg.popup('No datasets found!\n', location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        else:
            ds_numimgs = ''
            print('')
            if len(sweeps) == 1:
                foundtitle = str(len(sweeps)) + " dataset in this folder.\n"
                for sweep in sweeps:
                    found.append('Dataset:\n    ' + sweep[2] + '\n    Images: ' + str((int(sweep[4]) - int(sweep[3])) + 1))
                ds_numimgs = (int(sweep[4]) - int(sweep[3])) + 1     
            else:
                foundtitle = str(len(sweeps)) + " datasets or sweeps in this folder.\n"
                ds_numimgs = 0
                for sweep in sweeps:
                    found.append('Dataset (or sweep) no. '+ sweep[0] + ':\n    ' + sweep[2] + '\n    Images: ' + str((int(sweep[4]) - int(sweep[3])) + 1))
                    ds_numimgs = ds_numimgs + ((int(sweep[4]) - int(sweep[3])) + 1)
            window.write_event_value('-DSNUMIMGS-', ds_numimgs)
            img_hit_list = []
            if show_eiger == True:
                img_list_path = os.path.join(findimgpath, '*data*.h5')      
            else:
                img_list_pattern = re.sub("#", "?", str(sweeps[0][2]))
                #print(img_list_pattern)
                img_list_path = os.path.join(findimgpath, img_list_pattern)
            list_imgs_command = 'ls -1 -F ' + img_list_path +' > ./listimgs.tmp'
            list_imgs_process = subprocess.Popen(list_imgs_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            while True:
                return_code = find_process.poll()
                if return_code is not None:
                    time.sleep(0.2)
                    with open ('./listimgs.tmp', 'rt') as listimages:
                        for line in listimages:
                            line = line.rstrip('\n')
                            line = line.rstrip('\*')
                            line = os.path.join(findimgpath, line)
                            img_hit_list.append(line)            
                    findimages.close
                    os.remove("./listimgs.tmp")
                    break

            window.write_event_value('-IMAGESSET-', img_hit_list)    
            print(foundtitle)
            print("")
            
                
            foundmsg = "\n\n".join(found)
            print(foundmsg)
            print('')
            if os.path.exists(os.path.join(findimgpath, 'info.txt')) == True:
                f =  open(os.path.join(findimgpath, 'info.txt'), "r")
                dsinfofile = f.read()
                print('Beamline settings for this dataset:')
                print(dsinfofile)
                print('')
                f.close()
                dsinfovisible = True
            else:
                dsinfofile = 'No beamline information available'
                dsinfovisible = False

            layout_found_info = [[sg.Frame(layout=[
                              [sg.Text("")],
                              [sg.Column(layout=[  
                                  [sg.Text(foundtitle, justification = 'center', font = 'Arial 12', background_color = theme_color1, text_color = theme_color)]], element_justification = 'center', background_color = theme_color1)],
                              [sg.HorizontalSeparator(color = None)],
                              [sg.Multiline(default_text = foundmsg, size=(35,7), write_only = True, disabled = True, background_color = theme_color1, text_color = theme_color2, autoscroll = False)],
                              [sg.Text('', visible = dsinfovisible)],
                              [sg.Text('Beamline settings for this dataset:', text_color = theme_color, visible = dsinfovisible)],
                              [sg.Multiline(default_text = dsinfofile, size=(40,15), key='-DSINFOS-', write_only = True, disabled = True, background_color = theme_color1, font = "Courier 8", text_color = theme_color2, autoscroll = False, visible = dsinfovisible)],
                              [sg.Text('')]],title='\u2714 Data found', title_color= theme_color, font = "Arial 12", element_justification = 'center', relief=sg.RELIEF_GROOVE)],
                              [sg.Button('Okay', highlight_colors = (theme_color, theme_color))]]           
            window_found_info = sg.Window(foundtitle, layout_found_info, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                event_found_info, values_found_info = window_found_info.read()
                if event_found_info == sg.WIN_CLOSED or event_found_info == 'Okay': 
                    window_found_info.close()
                    layout_found_info = None
                    window_found_info = None
                    gc.collect()
                    break
            
    if error == True:
        print('')
        print("No datasets found!")
        print('')
        sg.popup('No datasets found!\n', location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))

    return len(sweeps)

# thread for image conversion function to keep gui working
def imgconv_thread(imgconv_command_1,imgconv_command_2,imgconv_command_3,conv_first_image):
    imgconv_process_1 = subprocess.Popen(imgconv_command_1, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        return_code = imgconv_process_1.poll()
        if return_code is not None:
            time.sleep(0.5)
            break
    print('Adxv export done.')    
    imgconv_process_2 = subprocess.Popen(imgconv_command_2, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    while True:
        return_code = imgconv_process_2.poll()
        if return_code is not None:
            time.sleep(0.5)
            break
    print('Image conversion done.')      
    os.remove(imgconv_command_3)
    print('Temporary files removed.')
    time.sleep(1)
    if conv_first_image == True:
        window.write_event_value('-IMGCONVDONE-', True)
    else:
        window_imageview.write_event_value('-IMGCONVDONE-', True)    

# helper function to run image conversion thread
def imgconv_function(imgconv_command_1,imgconv_command_2,imgconv_command_3,conv_first_image):
    threading.Thread(target=imgconv_thread, args=(imgconv_command_1,imgconv_command_2,imgconv_command_3,conv_first_image,), daemon=True).start()   

# image info retrieval
def imginfo_function(info_image):
    time.sleep(0.5)
    #window['-IMGINFO-'].print(" Getting Image info ...")
    imginfo_command = "imginfo "+ info_image + " > ./imginfo.tmp"
   # window['-IMGINFO-'].print(imginfo_command)
    #window['-IMGINFO-'].print("")
    #window['-IMGINFO-'].print(" ---------------------------------------------------------------------------")
    imginfo_process = subprocess.Popen(imginfo_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    decider = False
    imginfopattern = re.compile(" ===== Header information:")
    distpattern = re.compile(" distance")
    wlpattern = re.compile(" wavelength")
    Xsizepattern = re.compile(" Pixel size in X")
    Ysizepattern = re.compile(" Pixel size in Y")
    Xnumpattern = re.compile(" Number of pixels in X")
    Ynumpattern = re.compile(" Number of pixels in Y")
    Xcentrepattern = re.compile(" Beam centre in X            \[pixel\]")
    Ycentrepattern = re.compile(" Beam centre in Y            \[pixel\]")
    oscpattern = re.compile(" Oscillation")
    overloadpattern = re.compile(" Overload")
    thetapattern = re.compile(" 2-Theta")
    imginfolist = ""
    while True:
        return_code = imginfo_process.poll()
        if return_code is not None:
            with open ('./imginfo.tmp', 'rt') as imginfo:
                for line in imginfo:                 
                    if (imginfopattern.search(line) != None):
                        decider = True
                    if  decider == True: 
                        #print(line)
                        if re.search("\w", line) != None:
                            imginfolist = imginfolist + line
                        if (distpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSDIST-', val[1])
                        if (wlpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSWL-', val[1])
                        if (Xsizepattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSXSIZE-', val[1])
                        if (Ysizepattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSYSIZE-', val[1])
                        if (Xnumpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSXNUM-', val[1])
                        if (Ynumpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSYNUM-', val[1])
                        if (Xcentrepattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSBEAMX-', val[1])
                        if (Ycentrepattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSBEAMY-', val[1])
                        if (oscpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSOSC-', val[1])
                        if (overloadpattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGSOVERLOAD-', val[1])
                        if (thetapattern.search(line) != None):
                            val = re.split('= ', (line.rstrip('\n')))
                            window.write_event_value('-IMGSETTINGS2THETA-', val[1])               
            imginfo.close
            os.remove("./imginfo.tmp")
            window['-IMGINFO-'].print(imginfolist)
            #window['-IMGINFO-'].print(" ---------------------------------------------------------------------------")
            #window['-IMGINFO-'].print("")
            #window['-IMGINFO-'].print(" done.")
            break 

# helper function to extract parameters from XDS.INP file       
def values_from_xds(xds_inp):
    distpattern = re.compile("DETECTOR_DISTANCE")
    wlpattern = re.compile("X-RAY_WAVELENGTH")
    Xsizepattern = re.compile("QX")
    Ysizepattern = re.compile("QY")
    Xnumpattern = re.compile("NX")
    Ynumpattern = re.compile("NY")
    Xcentrepattern = re.compile("ORGX")
    Ycentrepattern = re.compile("ORGY")
    oscpattern = re.compile("OSCILLATION_RANGE")
    overloadpattern = re.compile("OVERLOAD")
    xds_pattern1 = re.compile("^\s*!")
    xds_pattern2 = re.compile("\s*!")
    print('')
    print('Reading values from XDS.INP file:')
    print(xds_inp)
    while True:
        with open (xds_inp, 'rt') as xdsinp:
            for line in xdsinp:
                if xds_pattern1.search(line) == None:
                    line = re.sub(" ?= *", "=", line)
                    if xds_pattern2.search(line) != None:
                        x = re.split(xds_pattern2, line)
                        line = x[0]
                    if (distpattern.search(line) != None):
                        val = str(abs(float(re.findall(r'(?<=DETECTOR_DISTANCE=)[^\s]*',line)[0])))
                        print('Detector distance =',val)
                        window.write_event_value('-IMGSETTINGSDIST-', val)
                    if (wlpattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=X-RAY_WAVELENGTH=)[^\s]*',line)[0]))
                        print('Wavelength =',val)
                        window.write_event_value('-IMGSETTINGSWL-', val)
                    if (Xsizepattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=QX=)[^\s]*',line)[0]))
                        print('Pixelsize in X =',val)
                        window.write_event_value('-IMGSETTINGSXSIZE-', val)
                    if (Ysizepattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=QY=)[^\s]*',line)[0]))
                        print('Pixelsize in Y =',val)
                        window.write_event_value('-IMGSETTINGSYSIZE-', val)
                    if (Xnumpattern.search(line) != None):
                        val = str(round(float(re.findall(r'(?<=NX=)[^\s]*',line)[0]))) 
                        window.write_event_value('-IMGSETTINGSXNUM-', val)
                        print('Pixels in X =',val)
                    if (Ynumpattern.search(line) != None):
                        val = str(round(float(re.findall(r'(?<=NY=)[^\s]*',line)[0])))
                        print('Pixels in Y =',val)
                        window.write_event_value('-IMGSETTINGSYNUM-', val)
                    if (Xcentrepattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=ORGX=)[^\s]*',line)[0]))
                        print('Beam position in X =',val)
                        window.write_event_value('-IMGSETTINGSBEAMX-', val)
                    if (Ycentrepattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=ORGY=)[^\s]*',line)[0]))
                        print('Beam position in Y =',val) 
                        window.write_event_value('-IMGSETTINGSBEAMY-', val)
                    if (oscpattern.search(line) != None):
                        val = str(float(re.findall(r'(?<=OSCILLATION_RANGE=)[^\s]*',line)[0]))
                        print('Oscillation range =',val)
                        window.write_event_value('-IMGSETTINGSOSC-', val)
                    if (overloadpattern.search(line) != None):
                        val = str(round(float(re.findall(r'(?<=OVERLOAD=)[^\s]*',line)[0])))
                        print('Overload value =',val)
                        window.write_event_value('-IMGSETTINGSOVERLOAD-', val)            
        xdsinp.close
        break




    

##############################
###MAIN PROGRAM STARTS HERE###
##############################



# first thing: check if you have write access in the current folder
current_path = os.getcwd()
if os.access(current_path, os.W_OK) == False:
    print('')
    print("-----WARNING!-----")
    print("AutoGUI has to be started from a folder where you have permissions to write data!")
    print('')
    sys.exit("Exiting.")

# second thing: check if global config-file is available and read values
if os.path.exists(config_path) == True:
    cfg_inpath = re.compile("inpath = ")
    cfg_outpath = re.compile("outpath = ")
    cfg_adxvpath = re.compile("adxvpath = ")
    cfg_browser = re.compile("browser = ")
    cfg_pdfviewer = re.compile("pdfviewer = ")
    cfg_nprocs = re.compile("nprocs = ")
    cfg_maxprocs = re.compile("maxprocs = ")
    cfg_inhouse_pars = re.compile("inhouse_pars = ")
    cfg_inhouse_detector = re.compile("inhouse_detector = ")
    cfg_inhouse_message = re.compile("inhouse_message = ")
    cfg_display_inhouse_message = re.compile("display_inhouse_message = ")
    cfg_preplist = re.compile("preplist = ")
    cfg_prepclassic = re.compile("prepfolder_classic = ")
    cfg_prepbatch = re.compile("prepfolder_batch = ")
    cfg_dark = re.compile("dark_theme = ")   
    with open (config_path, 'rt') as config:
        for line in config:
            line = line.strip()
            if cfg_inpath.search(line) != None:
                inpath = (re.split(cfg_inpath, line))[-1]
            if cfg_outpath.search(line) != None:
                outpath = (re.split(cfg_outpath, line))[-1]
            if cfg_adxvpath.search(line) != None:
                adxvpath = (re.split(cfg_adxvpath, line))[-1]  
            if cfg_browser.search(line) != None:
                browser = (re.split(cfg_browser, line))[-1]
            if cfg_pdfviewer.search(line) != None:
                pdfviewer = (re.split(cfg_pdfviewer, line))[-1]
            if cfg_nprocs.search(line) != None:
                nprocs = (re.split(cfg_nprocs, line))[-1]
            if cfg_maxprocs.search(line) != None:
                maxprocs = (re.split(cfg_maxprocs, line))[-1]
            if cfg_inhouse_pars.search(line) != None:
                inhouse_pars = (re.split(cfg_inhouse_pars, line))[-1]
            if cfg_inhouse_detector.search(line) != None:
                inhouse_detector = (re.split(cfg_inhouse_detector, line))[-1]
            if cfg_inhouse_message.search(line) != None:
                inhouse_message = re.sub('<br>', '\n', ((re.split(cfg_inhouse_message, line))[-1]))
            if cfg_display_inhouse_message.search(line) != None:
                display_inhouse_message = (re.split(cfg_display_inhouse_message, line))[-1]
                if (display_inhouse_message == "Y" or display_inhouse_message == "y" or display_inhouse_message == "YES" or display_inhouse_message == "yes" or display_inhouse_message == "Yes"):
                    display_inhouse_message = True
                else:
                    display_inhouse_message = False
            if cfg_preplist.search(line) != None:
                preplist = (re.split(cfg_preplist, line))[-1]
            if cfg_dark.search(line) != None:
                dark_theme = (re.split(cfg_dark, line))[-1]
                if dark_theme == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    dark_theme = True
                else:
                    dark_theme = False
            if cfg_prepclassic.search(line) != None:
                prepfolder_classic = (re.split(cfg_prepclassic, line))[-1]
                if prepfolder_classic == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    prepfolder_classic = True
                else:
                    prepfolder_classic = False
            if cfg_prepbatch.search(line) != None:
                prepfolder_batch = (re.split(cfg_prepbatch, line))[-1]
                if prepfolder_batch == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    prepfolder_batch = True
                else:
                    prepfolder_batch = False          
    config.close()
else:
    print('')
    print('Global configuration file not found.')
    print('Falling back to default configuration.')
    print('')

# third thing: check if personal config-file is available and read values
if os.path.exists(personal_config) == True:
    print("Personal config file found.")
    cfg_inpath = re.compile("inpath = ")
    cfg_outpath = re.compile("outpath = ")
    cfg_preplist = re.compile("preplist = ") 
    cfg_prepclassic = re.compile("prepfolder_classic = ")
    cfg_prepbatch = re.compile("prepfolder_batch = ")
    cfg_dark = re.compile("dark_theme = ")  
    cfg_highlight = re.compile("theme_highlight_color = ")
    with open (personal_config, 'rt') as config:
        for line in config:
            line = line.strip() 
            if cfg_dark.search(line) != None:
                dark_theme = (re.split(cfg_dark, line))[-1]
                if dark_theme == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    dark_theme = True
                else:
                    dark_theme = False
            if cfg_prepclassic.search(line) != None:
                prepfolder_classic = (re.split(cfg_prepclassic, line))[-1]
                if prepfolder_classic == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    prepfolder_classic = True
                else:
                    prepfolder_classic = False
            if cfg_prepbatch.search(line) != None:
                prepfolder_batch = (re.split(cfg_prepbatch, line))[-1]
                if prepfolder_batch == ("True" or "true" or "TRUE" or "y" or "Y" or "yes" or "Yes" or "YES"):
                    prepfolder_batch = True
                else:
                    prepfolder_batch = False
            if cfg_inpath.search(line) != None:
                inpath = (re.split(cfg_inpath, line))[-1]
            if cfg_outpath.search(line) != None:
                outpath = (re.split(cfg_outpath, line))[-1]
            if cfg_preplist.search(line) != None:
                preplist = (re.split(cfg_preplist, line))[-1]  
            if cfg_highlight.search(line) != None:
                theme_highlight_color = (re.split(cfg_highlight, line))[-1]                                               
    config.close()
else:
    print('')
    print('Personal configuration file not found.')
    print('Falling back to default parameters.')
    print('')    
outpath = os.path.expanduser(outpath)    

# fourth thing: retrieve supported macros of current autoproc version
m_pattern = re.compile("(\A \w)")
m2_pattern = re.compile("( : )")
check_macro_command = "process -M list > ./mlist.tmp"
check_macro_process = subprocess.Popen(check_macro_command, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
while True:
    return_code = check_macro_process.poll()
    if return_code is not None:
        with open ('./mlist.tmp', 'rt') as mlist:
            for line in mlist:
                if (m_pattern.search(line) != None) and (m2_pattern.search(line) != None):
                    macro = (''.join((line.split(":"))[0])).strip()
                    #print(macro)
                    m_list.append(macro.rstrip('\n'))
        os.remove('./mlist.tmp')            
        break   


## GUI THEME DEFINITIONS


if dark_theme == True:
    # Definition of dark GUI theme
    theme_color = theme_highlight_color                    # theme highlight color
    theme_color1 =  dark_theme_color                       # theme background color
    theme_color2 = 'white'                                 # theme text color
    theme_color3 = '#2b2a32'                               # theme button and input text color
else:
    # Definition of light GUI theme
    theme_color = theme_highlight_color                   # theme highlight color
    theme_color1 = light_theme_color                      # theme background color
    theme_color2 = 'black'                                # theme text color
    theme_color3 = 'white'                                # theme button and input text color

Color_Theme = {'BACKGROUND': theme_color1,
               'TEXT': theme_color2,
               'INPUT': theme_color,
               'TEXT_INPUT': theme_color3,
               'SCROLL': theme_color,
               'BUTTON': (theme_color3, theme_color),
               'PROGRESS': (theme_color, '#D0D0D0'),
               'BORDER': 0,
               'SLIDER_DEPTH': 0,
               'PROGRESS_DEPTH': 0}

blink_color1 = theme_color
blink_color2 = theme_color1

# Add your dictionary to the PySimpleGUI themes
sg.theme_add_new('AutoTheme', Color_Theme)

# Set PySimpleGui Theme and define options
sg.theme('AutoTheme')
sg.set_options(font = 'Helvetica 10', titlebar_background_color = theme_color1, titlebar_text_color = theme_color2, titlebar_icon = ag_icon, icon = ag_icon)


# gui definition

image_inp_col = [[sg.Text('Select your raw data (image) folder:',size=(30,1), font = 'Arial 12')],
                 [sg.InputText(default_text="Folder with diffraction images",key='-IMGS-',size=(44,2)), sg.Button(button_text = "Browse", tooltip = 'Browse', key = '-DATABROWSE-')]]

h5_inp_col = [[sg.Text('Select master.h5 file:',size=(60,1), font = 'Arial 12')],
              [sg.InputText(default_text="Path to HDF5 master file for EIGER data",key='-HDF5-',size=(44,2)), sg.Button(button_text = "Browse", tooltip = 'Browse', key = '-EIGERBROWSE-')]]

output_col = [[sg.Text('Select output folder:',size=(60,1), font = 'Arial 12')],
              [sg.InputText(default_text="Folder for data processing",key='-OUTF-',size=(44,2)),sg.Button(button_text = "Set", tooltip = 'Sets current folder as output folder', key = '-SETCURRENT-', enable_events = True), sg.FolderBrowse(initial_folder = outpath, button_text = "Browse", tooltip = 'Browse', target = ('-OUTF-')),]]

check_col = [[sg.Checkbox('Prepare folder', key='-PREP-', default = prepfolder_classic, tooltip = 'Make default sub-folders for MR, refinement, etc.',size = (None,1)), sg.Checkbox('Link auto-processed beamline data', key='-LINK-', tooltip = 'Make link to beamline auto-processing data, if available', size = (None,1), default = True), sg.Checkbox('Link images', key='-LINKIMG-', tooltip = 'Make a folder with links to the diffraction images', size = (None,1))]]

subdir_col = [[sg.Checkbox('Make sub-directory:', enable_events=True, key='-MKSUB-', size = (None,1), tooltip = 'Create new subdirectory for output files'),sg.Input(key='-SUBFOL-', size=(35,1), disabled = True, tooltip = 'Name of subdirectory.\nCan create a whole sub-path by separating folders using "/".')]]
      
spg_column = [[sg.Checkbox('Set space group and/or cell manually', default = False, key='-SGMAN-', enable_events=True, disabled = False, tooltip = 'Provide cell parameters and/or space group.')],
              [sg.Text("Space group:", size =(11,1)), sg.InputText('', size=(22,1), key ='-SPG-', disabled = True, tooltip='e.g. P212121')],
              [sg.Text("Cell:", size =(11,1)), sg.InputText('', size=(22,1), key ='-CELL-', disabled = True, tooltip='e.g. 140.1 70.5 80.4 90 142.3 90' )]]
              
reso_column = [[sg.Checkbox('Set resolution limits manually', key = '-RESLIM-', enable_events = True, tooltip = 'If not set, resolution limits will be determined outomatically.')],
               [sg.Text('low:'), sg.InputText(default_text = '100', size=(5,1), key ='-LOWR-', disabled = True), sg.Text('high:'), sg.InputText(default_text = '1.0', size=(5,1), key='-HIGHR-', disabled = True), sg.Text('Å')]]

mtz_column = [[sg.Checkbox('Reference', default = False, key='-SGREF-', enable_events=True, disabled = False, tooltip = "Uses freeR-flag, space group and cell from given MTZ file"),
               sg.Checkbox('FreeR-flag', default = False, key = '-FREECOPY-', enable_events = True, disabled = False, tooltip = "Copies freeR-flag from given MTZ file")],
              [sg.InputText('', size=(25,1), key ='-REF-', disabled = True), sg.Button('Browse', key = '-REFBROWSE-', disabled = True)]]
    
anomalous_column = [[sg.Col([[sg.Radio("Auto", 'ANOM', key = '-ANOMAUTO-', size = (4, None), default = True, enable_events = True, tooltip = 'Rely on autoPROC\'s defaults for detection and handling of potential anomalous signal.\n(Friedel\'s Law = ???)'),
                        sg.Radio("Yes", 'ANOM', key = '-ANOMYES-', size = (4, None), enable_events = True, tooltip = 'Make autoPROC assume anomalous signal, even if it is weak.\n(Friedel\'s Law = False)'),
                        sg.Radio("No", 'ANOM', key = '-ANOMNO-', size = (4, None), enable_events = True, tooltip = 'Ignore indications of anomalous signal, even if detected.\n(Friedel\'s Law = True)')],
                        [sg.Checkbox('Expect very strong signal', key = '-ANOMLARGE-', enable_events = True, default = False, disabled = True, tooltip = 'Apply special settings for very strong anomalous signal.')]], element_justification = 'left', justification = 'left')]]

cutoff_column = [[sg.Combo(("CC(1/2)>=0.3 (default)", "I/sig(I)>=2.0, CC(1/2)>=0.3, Rpim<=0.6 (old default)", "Custom values for I/sig(I), CC(1/2), Rpim",),
                  default_value = 'CC(1/2)>=0.3 (default)', key = '-CUTSEL-', size=(50,5), readonly = True, change_submits = True, enable_events = True,
                  tooltip = "Default = Use autoPROC's default cutoff criteria (recommended, now based mainly on CC(1/2))\nOld default = Automatic cutoff determination as used before Nov. 22 (I/sig(I) >= 2 (mainly), Rpim <= 0.6, CC(1/2) >= 0.3)\nCustom = Provide your own cutoff criteria for I/sig(I), CC(1/2) and/or Rpim")],
                 [sg.Col([[sg.Text('I/sig(I) >=', justification = 'right'),
                  sg.InputText('0.0', size = (4, None), key = '-ISIGIVAL-', disabled = True)]], justification = "left", element_justification = "left", size = (120, None)),
                 sg.Col([[sg.Text('CC(1/2) >=', justification = 'right'),
                  sg.InputText('0.3', size = (4, None), key = '-CCHALFVAL-', disabled = True)]], justification = "left", element_justification = "left", size = (120, None)),
                 sg.Col([[sg.Text('Rpim <=', justification = 'right'),
                  sg.InputText('99.9', size = (4, None), key = '-RPIMVAL-', disabled = True)]], justification = "left", element_justification = "left", size = (120, None))]]
                 
                        

macro_column = [[sg.Checkbox('Run with macro', key = '-ENABLEMACRO-', enable_events = True, disabled = False, tooltip = 'Use a macro from autoPROC\'s list.\nCan\'t be combined with custom parameters.')],
                [sg.Combo(m_list, size=(25,1), key = '-MACRO-', disabled = True, enable_events = True, change_submits = True, default_value = '---Select macro---', tooltip = 'Select macro'), sg.Button('Macro details',key = '-LISTMACROS-',disabled = True, tooltip = 'Show list of macros with explanations')],
                [sg.Text('Macros not available if custom parameters are set!', key = '-MACROWARNING-', text_color = theme_color1)]]

custom_column = [[sg.Checkbox('Set parameters', key = '-CUSTPAR-', tooltip = 'Your own macro.\nCan\'t be used together with pre-defined macros.', enable_events = True, disabled = False, size =(25, None)),sg.Button('Edit', key = '-EDPAR-', disabled = True)]]

extra_column = [[sg.Checkbox("Supply additional arguments:", key = '-PARSON-', enable_events=True, default = False,
                    tooltip = 'Everything in this line is added to the command line as is.\nParameters are usualy given in the format variable="value"\nPlease separate multiple parameters by spaces.\ne.g. beam="1532 1543" symm="P21"\nCheck autoPROC documentation for usage by clicking on "Help"'),
                 sg.InputText(default_text='', key = '-EXTRAPARS-', size = (65, None), disabled = True,
                    tooltip = 'Everything in this line is added to the command line as is.\nParameters are usualy given in the format variable="value"\nPlease separate multiple parameters by spaces.\ne.g. beam="1532 1543" symm="P21"\nCheck autoPROC documentation for usage by clicking on "Help"'),
                 sg.Text('(Help)', text_color = theme_color, font = "Courier 6 bold", key='-WEB-', enable_events=True, tooltip='Click here to open autoPROC parameter list in browser.'),]]

cleanup_column = [[sg.Checkbox("Clean up output files", key = '-CLEANUP-', enable_events=True, default = True,
                    tooltip = 'Disk usage will be reduced by deleting output files that are unlikely to be required\nAll files required for the HTML-log and all .log and .LP files will be preserved.')]]

image_column = [[sg.Checkbox('Customize image range', key = '-SWEEPSET-',enable_events = True, disabled = False, tooltip = 'If not set, all images will be used.'), sg.Button('Define', key = '-SWEEPRANGE-',enable_events = True, disabled = True, tooltip = 'Detect sweeps & define sets of images to process'),
                    sg.Checkbox('Exclude bad images', key = '-BADIMGS-', tooltip = 'Should autoPROC automatically exlude bad images?\n(Default behavior = yes)', default = True, enable_events = True, disabled = False)]]

processor_column = [[sg.Text('Use',  justification = 'right', size =(4,1)),sg.InputText(nprocs, size =(3,1), key = '-NPROC-', tooltip = '8 should be sufficient!'),sg.Text('processors',  justification = 'left', size =(11,1))]]

imginfo_column = [[sg.Col(
                   [[sg.Multiline(size=(60,20), key='-IMGINFO-', autoscroll = False, no_scrollbar = True, do_not_clear = False, font ="Courier 8", write_only = True, tooltip = "Displays the header of your dataset's first image\nas read by imginfo")]]
                   ,size = (375,280))]]

imgsettings_column = [[sg.Col(      
                       [[sg.Text('Beam centre from:'),sg.Combo((beamcentreactions_eiger),
                       default_value = beamcentremode, key = '-BEAMCENTREMODE-', size=(40,5), readonly = True, change_submits = True, enable_events = True, tooltip = 'In most cases, the beam centre form the header should be fine.\nIf X and Y axes might be swapped and/or inverted, "try possible transformations".\nGuessing the beamcenter based on circular features in the image will most likely fail.\nBetter specify the beam centre manually or set it in the diffraction image.')],
                       [sg.Text('', font = 'Arial 6')],
                       [sg.Text('', size = (2,1)),sg.Text('Beam X:',size=(12,1)),sg.InputText(default_text= beamcentrex,key='-BEAMX-',size=(8,1), disabled = True),sg.Text('px',size=(5,1)),
                        sg.Text('', size = (2,1)),sg.Text('Beam Y:',size=(12,1)),sg.InputText(default_text= beamcentrey,key='-BEAMY-',size=(8,1), disabled = True),sg.Text('px')],
                       [sg.Text('', font = 'Arial 6')],
                       [sg.Checkbox('Distance:',size=(12,1),key = '-DISTBOX-', default = False, enable_events = True),sg.InputText(default_text= distance,key='-DIST-',size=(8,1), disabled = True),sg.Text('mm',size=(5,1)),
                        sg.Checkbox(text= 'Wavelength:', key = '-WLBOX-',size=(12,1), default = False, enable_events = True),sg.InputText(default_text= wavelength,key='-WAVEL-',size=(8,1),disabled = True),sg.Text('Å')],
                       [sg.Checkbox('Oscillation:',size=(12,1),key = '-OSCBOX-', default = False, enable_events = True),sg.InputText(default_text= oscillation,key='-OSC-',size=(8,1), disabled = True),sg.Text('°',size=(5,1)),
                        sg.Checkbox(text= 'Overload:', key = '-OVERLOADBOX-',size=(12,1), default = False, enable_events = True),sg.InputText(default_text= overload,key='-OVERLOAD-',size=(8,1),disabled = True),sg.Text('')], 
                       [sg.Checkbox('Pixel size X:',size=(12,1), key = '-PIXELSIZEBOX-', default = False, enable_events = True),sg.InputText(default_text= pixelsizex,key='-XPIXELSIZE-',size=(8,1), disabled = True),sg.Text('mm',size=(5,1)),
                        sg.Text('', size = (2,1)),sg.Text('Pixel size Y:',size=(12,1)),sg.InputText(default_text= pixelsizey,key='-YPIXELSIZE-',size=(8,1), disabled = True),sg.Text('mm')],
                       [sg.Checkbox('No. X-pixels:',size=(12,1), key = '-PIXELNUMBOX-', default = False, enable_events = True),sg.InputText(default_text= nopixelx,key='-XPIXELS-',size=(8,1), disabled = True),sg.Text('',size=(5,1)),
                        sg.Text('', size = (2,1)),sg.Text('No. Y-pixels:',size=(12,1)),sg.InputText(default_text= nopixely,key='-YPIXELS-',size=(8,1), disabled = True),sg.Text('')],
                       [sg.Col([[]], size = (None, 10))],
                       [sg.Col([[sg.Button('Reset to header values', highlight_colors = (theme_color, theme_color), key = '-IMGHEADERVALS-', size = (27, 1), disabled = True, tooltip = 'Reload the values from the header of the first image'), sg.Input(key='-XDSINP-', visible=False, enable_events=True), sg.FileBrowse('Use values from XDS.INP file', key = '-XDSINPLOAD-', size = (27, 1), disabled = True, tooltip = 'Fill above table with values provided in a "XDS.INP" file\n(probably from beamline processing)', file_types = (('XDS input file', ('*.INP', '*.INP*')),))]], justification = "center")]])]]
                
options_tab_1 = [[sg.Frame(layout=[
                 [sg.Column(output_col,size = (495,70)), sg.Column(image_inp_col, key = '-INP1-', visible = False ,size = (405,70)), sg.Column(h5_inp_col, key = '-INP2-', visible = True ,size = (405,70))],
                 ],title='Required minimum input',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                 [sg.Frame(layout=[
                 [sg.Column(subdir_col, key='-COL3-', visible=True ,size = (405,30)), sg.Column(check_col ,size = (495,30))]],title='Common options',title_color=theme_color, relief=sg.RELIEF_GROOVE)],  
                 [sg.Frame(layout=[[
                    sg.Column([[sg.Multiline(size=(147,14), key='-OUTPUT-', font = "Courier 8", reroute_stdout = reroute_out, echo_stdout_stderr = echo_out, write_only = True, autoscroll = True)]],size = (930, None))]], title='Console',title_color=theme_color, relief=sg.RELIEF_GROOVE)]]  

options_tab_2 = [[sg.Frame(layout=[      
                  [sg.Frame(layout=[[sg.Column(cutoff_column, size = (375, 70))]],  
                    title='High resolution cutoff criteria',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                   sg.Frame(layout=[[sg.Column(reso_column, size = (246, 70))]],
                    title='Resolution limits',title_color=theme_color, relief=sg.RELIEF_GROOVE),    
                   sg.Frame(layout=[[sg.Column(anomalous_column, size = (255, 70))]],
                    title='Anomalous data?',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                   [sg.Frame(layout=[[sg.Column(spg_column, size = (270, 100))]], title='Space group and cell',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                    sg.Frame(layout=[[sg.Column(mtz_column, size = (270, 100))]], title='Provide MTZ for:',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                    sg.Frame(layout=[[sg.Column(macro_column, size = (336, 100))]], title='Macros',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                   [sg.Frame(layout=[[sg.Column(processor_column, size = (154, 45))]],title='Parallel threads',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                    sg.Frame(layout=[[sg.Column(image_column, size = (430, 45))]],title='Image range',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                    sg.Frame(layout=[[sg.Column(custom_column, size = (286, 45))]],title='Custom parameters',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                   [sg.Frame(layout=[[sg.Column(extra_column, size = (720, 45))]],title='Append arguments to command line',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                    sg.Frame(layout=[[sg.Column(cleanup_column, size = (210, 45))]],title='Reduce size on disk',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                    ],title= None,title_color=theme_color, relief=None, border_width = 0, pad = (0,0,0,0))]]

options_tab_3 = [[sg.Frame(layout=[
                [sg.Frame(layout=[[sg.Button('Click to draw on image', highlight_colors = (theme_color, theme_color), key = '-IMAGEEDIT-', tooltip = "Displays the first diffraction image of your dataset\nand provides tools to adjust the beam center and apply different types of masks\ne.g. for masking the beam stop shadow, dead pixels and even Dectris panel gaps.", disabled = True, size = (140, 1))]],title='Masking and beam position adjustment',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                  [sg.Frame(layout=[[sg.Column(imginfo_column, size = (390, 280))]],title='Image header',title_color=theme_color, relief=sg.RELIEF_GROOVE),
                  sg.Frame(layout=[[sg.Column(imgsettings_column, size = (500, 280))]],title='Experimental parameters',title_color=theme_color, relief=sg.RELIEF_GROOVE)],
                  ],title= None,title_color=theme_color, relief=None, border_width = 0, pad = (0,0,0,0))]]                  


section_debug = [[sg.Frame(layout=[
                    [sg.Column([[sg.Multiline(size=(147,8), key='-ERROR-', font = "Courier 8", reroute_stderr = reroute_out, write_only = True, autoscroll = True)]],size = (905, 120))]], title='Error console',title_color=theme_color, relief=sg.RELIEF_GROOVE)]]  

                                                                     
layout = [[sg.Frame(layout= [
                   [sg.Col([[sg.Text("\u2691", text_color = theme_color, font = 'Courier, 20', size = (2, None), justification = 'left', key = '-STATICON-', tooltip = "Program status.\nAs long as it is blinking, it is still doing something.\n\n>>If it blinks, we can kill it.<<\n     - Dutch.", visible = True),
                             sg.Text('Select mode: ', font = 'Arial 12'), sg.Combo(("Synchrotron: EIGER", "Synchrotron: EIGER (mini-cbf conversion)", "Synchrotron: PILATUS", inhouse_detector, "Others: Image plates, CCDs, ...", "Electron diffraction"),
           default_value = 'Synchrotron: EIGER', key = '-DETSEL-', size=(41,6), readonly = True, change_submits = True, enable_events = True, tooltip = 'Use EIGER with mini-cbf conversion only if normal EIGER data processing does not work!')]], size = (465, 45)),
           sg.Frame(layout = [[sg.Col([[sg.Text(welcome, font = 'Arial 12', justification = 'left', size =(42, None), background_color = None, text_color =theme_color, key = '-ABOUT-', enable_events = True, tooltip = 'About'),sg.Button('', key ='-LOGOBUTTON-', image_data=ag_icon, image_subsample = 2, border_width = 0, button_color=(sg.theme_background_color(),sg.theme_background_color()), enable_events = True, tooltip = 'About')]], size =(435,45))]],title= None,title_color=theme_color, relief=sg.RELIEF_GROOVE, element_justification = "center", vertical_alignment='center')], 
          [sg.TabGroup([[sg.Tab('Basics', options_tab_1, key = '-TAB1-'), sg.Tab('Processing options', options_tab_2, key = '-TAB2-'), sg.Tab('Images & experiment', options_tab_3, key = '-TAB3-')]],
            title_color = theme_color1, tab_background_color = theme_color, selected_background_color = theme_color1, selected_title_color = theme_color2, font = 'Arial 12', border_width = 0, size = (930, 400),
            enable_events = True, key = '-TABGROUP-')],
          [sg.Frame(layout = [  
          [sg.Col([[sg.ProgressBar(BAR_MAX, orientation='horizontal', size=(92,20), key='-PROG-', visible = True)]],size = (925, 30))],     
          [sg.Col([[sg.Button('Run',key ='-RUN-', disabled = False, button_color ='white on green', tooltip = 'GoGoGo'), sg.Button('Quit', button_color = 'yellow on red', tooltip = 'Bail out!')]], size = (150, 40), vertical_alignment ="top", justification ="left"),
           sg.Col([[sg.Text('', key =('-TMSG-'), size = (15,1), justification = "left", text_color = theme_color, tooltip = 'Is it still doing something?'), sg.Text('', key =('-TIME-'), size = (8,1), justification = "left",text_color = theme_color, tooltip = 'time for a coffee...'), sg.Text(progword, key='-PW-', size = (51,1), justification = "right", text_color = theme_color, tooltip = 'Processing status\n\nStatus and progress-bar updates will not be shown\nif the dataset consists of more than one scan / sweep')]],
                    size = (592, 40),vertical_alignment ="bottom", justification ="center"), sg.Col([[ sg.Button('Check images in Adxv', tooltip = 'Launches external diffraction image viewer')]],
                    size = (170,40), vertical_alignment ="top", justification = "right", element_justification = "right")],
          [sg.Col([[sg.Button('Show live-processing in browser', tooltip = 'self refreshing version of AutoPROC\'s HTML output', disabled = False, key = '-LOGBROWSER-'),sg.Button('Abort processing', button_color = 'yellow on red', tooltip = 'Mayday!!! Mayday!!!'),
           sg.Col([[sg.Col([[sg.Combo(("Display log (new window)", "HTML processing log", "PDF report (isotropic)", "PDF report (anisotropic)"), default_value = "---Results---",
                    key = '-RESMEN-', size=(24,6), readonly = True, change_submits = True, enable_events = True, font = "Arial 12")]], size = (403, 40), justification ="left", vertical_alignment = "bottom"),
                    sg.Button('Re-run POINTLESS', key = '-PTLESS-', tooltip = 'Send finalized data to POINTLESS. Useful for missed screw axes from in-house data.')]], key='-RESBUTS-', visible= False, justification = "left", size = (562, 40))]],key='-COL4-', visible= False),
          sg.Col([[sg.Text('')]], size = (None,40), key='-COLX4-', visible= True)],
          [sg.Col([[sg.HorizontalSeparator(color = '#D0D0D0')],
                   [sg.StatusBar(' \u2691  Ready.', text_color = theme_color, background_color= theme_color1, key = '-STAT-', size = (132,1))]], size = (925, 35))]]
           ,title= None,title_color=theme_color, relief=None, border_width = 0, pad = (0,0,0,0))],
          [collapse(section_debug, '-DEBUG-')],
          [sg.Text('', font = 'Courier 1')] 
         ], title = None, relief = None, border_width = 0, pad = (0,0,0,0))]]

# create window
window = sg.Window(win_title, layout, no_titlebar=False, grab_anywhere=False, resizable=True, size = (963,685), finalize=True, location = (300, 100))

# leave message if in debug mode
if debug == True:
    window['-OUTPUT-'].print('***DEBUG MODE***')
    window['-OUTPUT-'].print('')
    window['-OUTPUT-'].print('No output in this window!')
    window['-OUTPUT-'].print('All output will be on the console.')
    window['-OUTPUT-'].print("All output will be also written to 'autogui_debug.log'")
    window['-OUTPUT-'].print('')
    window['-OUTPUT-'].print('***DEBUG MODE***')

#do stuff
while True:
    event, values = window.read()

    # set current directory as output
    if event == '-SETCURRENT-':
        window['-OUTF-'].update(os.getcwd())

    # select browsing folder for data
    if event == '-DATABROWSE-':
        homedir = '~/'
        currentdir = outpath
        if os.path.exists(values['-IMGS-']) == True:
            currentdir = values['-IMGS-']
            currentdirdisabled = False
        else:
            currentdirdisabled = True
        layout_databrowse = [[sg.Text('Select browsing origin:'), sg.Input(key='-DATABROWSEPATH-', visible=False, enable_events=True),],
                             [sg.FolderBrowse(initial_folder = inpath, size = (20, 1), button_text = 'Data directory', tooltip = 'Browse data directory', target = '-DATABROWSEPATH-')],
                             [sg.FolderBrowse(initial_folder = currentdir, size = (20, 1), button_text = 'Current directory', tooltip = 'Browse current data directory', target = '-DATABROWSEPATH-', disabled = currentdirdisabled)],
                             [sg.FolderBrowse(initial_folder = outpath, size = (20, 1), button_text = 'Working directory', tooltip = 'Browse working directory', target = '-DATABROWSEPATH-')],
                             [sg.FolderBrowse(initial_folder = homedir, size = (20, 1), button_text = 'Home directory', tooltip = 'Browse home directory', target = '-DATABROWSEPATH-')]]
        window_databrowse = sg.Window('Data:', layout_databrowse, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_databrowse, values_databrowse = window_databrowse.read()
            if event_databrowse == '-DATABROWSEPATH-':
                window['-IMGS-'].update(values_databrowse['-DATABROWSEPATH-'])
                findimgpath = values_databrowse['-DATABROWSEPATH-']
                show_eiger = False
                window_databrowse.close()
                layout_databrowse = None
                window_databrowse = None
                gc.collect()
                break
            if event_databrowse == sg.WIN_CLOSED:
                window_databrowse.close()
                layout_databrowse = None
                window_databrowse = None
                gc.collect()                
                break
        if os.path.exists(findimgpath) == True:
            if re.search(" ", findimgpath) != None:
                print('')
                print('Problem found in:', findimgpath)
                print('Input path must not contain any white space characters!')
                status = '  Input path must not contain any white space characters!'
                window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')
            else:   
                status = ' \u2691  Ready.'
                window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
                numfoundsweeps = show_sets(show_eiger, findimgpath)
                #print("\nSweeps found:", str(numfoundsweeps))
                beamcentremode = "header"
                beamcentrex = "n/a"
                beamcentrey = "n/a"
                distance = "n/a"
                wavelength = "n/a"
                oscillation = "n/a"
                overload = "n/a"
                pixelsizex = "n/a"
                pixelsizey = "n/a"
                nopixelx = "n/a"
                nopixely = "n/a"
                extrapars = ""
                headertwotheta = 0
                untrusted_rectangles = []
                untrusted_ellipses = []
                untrusted_rectangle_coords = []
                untrusted_ellipse_coords = []
                untrusted_quad_coords = []
                untrusted_quads = []
                dectris_gap_coords = []
                dectris_gaps = []
                modified_beamcenter =""
                img_hit_list = []
                ds_numimgs = ''
                xdsupdate = False
                

    # select browsing folder for EIGER Data
    if event == '-EIGERBROWSE-':
        homedir = '~/'
        currentdir = "/".join((values['-HDF5-']).split("/")[:-1])
        if os.path.exists(values['-HDF5-']) == True:
            currentdirdisabled = False
        else:
            currentdirdisabled = True
            currentdir = outpath
        layout_eigerbrowse = [[sg.Text('Select browsing origin:'), sg.Input(key='-EIGERBROWSEPATH-', visible=False, enable_events=True),],
                             [sg.FileBrowse(initial_folder = inpath, size = (20, 1), button_text = 'Data directory', tooltip = 'Browse data directory', target = '-EIGERBROWSEPATH-', file_types = (('HDF5 master-file', '*.h5'),))],
                             [sg.FileBrowse(initial_folder = currentdir, size = (20, 1), button_text = 'Current directory', tooltip = 'Browse current data directory', target = '-EIGERBROWSEPATH-', disabled = currentdirdisabled, file_types = (('HDF5 master-file', '*.h5'),))],   
                             [sg.FileBrowse(initial_folder = outpath, size = (20, 1), button_text = 'Working directory', tooltip = 'Browse working directory', target = '-EIGERBROWSEPATH-', file_types = (('HDF5 master-file', '*.h5'),))],
                             [sg.FileBrowse(initial_folder = homedir, size = (20, 1), button_text = 'Home directory', tooltip = 'Browse home directory', target = '-EIGERBROWSEPATH-', file_types = (('HDF5 master-file', '*.h5'),))]]
        window_eigerbrowse = sg.Window('Master.h5:', layout_eigerbrowse, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_eigerbrowse, values_eigerbrowse = window_eigerbrowse.read()
            if event_eigerbrowse == '-EIGERBROWSEPATH-':
                eigermaster = re.sub ('data_.*.h5', 'master.h5', values_eigerbrowse['-EIGERBROWSEPATH-'])
                if os.path.exists(eigermaster):
                    window['-HDF5-'].update(eigermaster)
                    findimgpath = "/".join(eigermaster.split("/")[:-1])
                    show_eiger = True
                    window_eigerbrowse.close()
                    layout_eigerbrowse = None
                    window_eigerbrowse = None
                    gc.collect()
                    break
                else: 
                    sg.popup('Please provide a valid HDF5 master file!')
                    window_eigerbrowse.close()
                    layout_eigerbrowse = None
                    window_eigerbrowse = None
                    gc.collect()
                    break
            if event_eigerbrowse == sg.WIN_CLOSED:
                window_eigerbrowse.close()
                layout_eigerbrowse = None
                window_eigerbrowse = None
                gc.collect()                
                break
        if os.path.exists(findimgpath) == True:
            if re.search(" ", findimgpath) != None:
                print('')
                print('Problem found in:', findimgpath)
                print('Input path must not contain any white space characters!')
                status = '  Input path must not contain any white space characters!'
                window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')
            else:    
                status = ' \u2691  Ready.'
                window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
                numfoundsweeps = show_sets(show_eiger, findimgpath)
                #print("\nSweeps found:", str(numfoundsweeps))
                beamcentremode = "header"
                beamcentrex = "n/a"
                beamcentrey = "n/a"
                distance = "n/a"
                wavelength = "n/a"
                oscillation = "n/a"
                overload = "n/a"
                pixelsizex = "n/a"
                pixelsizey = "n/a"
                nopixelx = "n/a"
                nopixely = "n/a"
                extrapars = ""
                headertwotheta = 0
                untrusted_rectangles = []
                untrusted_ellipses = []
                untrusted_rectangle_coords = []
                untrusted_ellipse_coords = []
                untrusted_quad_coords = []
                untrusted_quads = []
                dectris_gap_coords = []
                dectris_gaps = []
                modified_beamcenter =""
                img_hit_list = []
                ds_numimgs = ''
                xdsupdate = False
                

    # detector selection
    if event == '-DETSEL-':
        if values['-DETSEL-'] == "Synchrotron: EIGER (mini-cbf conversion)":
            window['-INP1-'].update(visible = False)
            window['-INP2-'].update(visible = True)
            window['-BEAMCENTREMODE-'].update(value = beamcentremode, values = beamcentreactions)
            EIGER = True
            h52cbf = True
            param_extra = ''
            # warn for duration of mini-cbf conversion
            layout_cbf = [[sg.Text('Attention!', justification = "center", font = "Arial 12", text_color = "red")],
                   [sg.Text('Use the EIGER mini-cbf conversion mode only if direct processing of HDF5 files does not work!')],
                   [sg.Text('Conversion of .h5 to .cbf may take longer than the actual data processing!')],
                   [sg.Checkbox('Keep mini-cbf files after closing program?', key = '-KEEPCBF-', default = keepcbfs, enable_events=True, disabled = False, tooltip = "If checked, mini-cbf files won't be deleted if program is closed.\nWarning! These files take quite some disk space.")],        
                   [sg.Button('Got it', highlight_colors = (theme_color, theme_color))]]           
            window_cbf = sg.Window('Attention', layout_cbf, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                event_cbf, values_cbf = window_cbf.read()
                if event_cbf == '-KEEPCBF-':
                    if values_cbf['-KEEPCBF-'] == True:
                        tmpcbffolder = 'cbfs'
                        keepcbfs = True
                    else:
                        tmpcbffolder = 'tempcbfs'
                        keepcbfs = False
                if event_cbf == sg.WIN_CLOSED or event_cbf == 'Got it':
                    window_cbf.close()
                    layout_cbf = None
                    window_cbf = None
                    gc.collect()
                    break
        elif values['-DETSEL-'] == "Synchrotron: EIGER":
            window['-INP1-'].update(visible = False)
            window['-INP2-'].update(visible = True)
            window['-BEAMCENTREMODE-'].update(value = beamcentremode, values = beamcentreactions_eiger)
            EIGER = True
            h52cbf = False
            param_extra = ''
        elif values['-DETSEL-'] == inhouse_detector:
            # set parameters for being able to process SFPR inhouse data
            param_extra = inhouse_pars
            EIGER = False
            h52cbf = False
            window['-BEAMCENTREMODE-'].update(value = beamcentremode, values = beamcentreactions) 
            window['-INP1-'].update(visible = True)
            window['-INP2-'].update(visible = False)
            # display message for using inhouse detector
            if display_inhouse_message == True:
                layoutx = [[sg.Text('Attention!', justification = "center", font = "Arial 12", text_color = "red")],
                                   [sg.Text(inhouse_message)],
                                   [sg.Button('Got it', highlight_colors = (theme_color, theme_color))]]           
                windowx = sg.Window('Attention', layoutx, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
                while True:
                    eventx, valuesx = windowx.read()
                    if eventx == sg.WIN_CLOSED or eventx == 'Got it':
                        windowx.close()
                        layoutx = None
                        windowx = None
                        gc.collect()
                        break
        elif values['-DETSEL-'] == "Electron diffraction":
            # set parameters for being able to process MicroED data
            param_extra = microED_pars
            EIGER = False
            h52cbf = False
            window['-BEAMCENTREMODE-'].update(value = beamcentremode, values = beamcentreactions)
            window['-INP1-'].update(visible = True)
            window['-INP2-'].update(visible = False)
            window['-ENABLEMACRO-'].update(value = True, disabled = False)
            window['-MACRO-'].update(value = 'SmallMolecules', disabled=False)
            window['-LISTMACROS-'].update(disabled=False)
            window['-EDPAR-'].update(disabled=True)
            window['-CUSTPAR-'].update(value = False, disabled=True, background_color = theme_color1)
            window['-NPROC-'].update(value = '1')
            # message for microED
            layoutmed = [[sg.Text('Attention!', justification = "center", font = "Arial 12", text_color = "red")],
                               [sg.Text('This mode is intended for processing of electron diffraction datasets (3DED/microED).')],
                               [sg.Text('Small molecule mode will be activated in "Macro" settings by default.')],
                               [sg.Text('Number of processors will be set to 1.')],
                               [sg.Button('Got it', highlight_colors = (theme_color, theme_color))]]           
            windowmed = sg.Window('Attention', layoutmed, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                eventmed, valuesmed = windowmed.read()
                if eventmed == sg.WIN_CLOSED or eventmed == 'Got it':
                    windowmed.close()
                    layoutmed = None
                    windowmed = None
                    gc.collect()
                    break         
        else:
            param_extra = ''       
            EIGER = False
            h52cbf = False
            window['-BEAMCENTREMODE-'].update(value = beamcentremode, values = beamcentreactions)
            window['-INP1-'].update(visible = True)
            window['-INP2-'].update(visible = False)   

# enable/disable fields
    if event == '-MKSUB-':
        disable_sub = not disable_sub
        window['-SUBFOL-'].update(disabled=disable_sub)
    if event == '-RESLIM-':
        disable_res = not disable_res
        window['-LOWR-'].update(disabled=disable_res)
        window['-HIGHR-'].update(disabled=disable_res)
    if event == '-FREECOPY-' and values['-FREECOPY-'] == True:
        window['-REF-'].update(disabled=False)
        window['-SGREF-'].update(disabled=True)
        window['-SGREF-'].update(value=False)
        window['-REFBROWSE-'].update(disabled=False)
    if event == '-FREECOPY-' and values['-FREECOPY-'] == False:
        window['-REF-'].update(disabled=True)
        window['-SGREF-'].update(disabled=False)
        window['-SGREF-'].update(value=False)
        window['-REFBROWSE-'].update(disabled=True)    
    if event == '-SGMAN-' and values['-SGMAN-'] == True:
        disable_spg = False
        disable_ref = True
        window['-SPG-'].update(disabled=disable_spg)
        window['-CELL-'].update(disabled=disable_spg)
        if values['-SGREF-'] == True:
            window['-REF-'].update(disabled=disable_ref)
            window['-REFBROWSE-'].update(disabled=disable_ref)
            window['-SGREF-'].update(value = False)
        window['-SGREF-'].update(disabled = True)
        window['-FREECOPY-'].update(disabled = False) 
    if event == '-SGMAN-' and values['-SGMAN-'] == False:
        window['-SGREF-'].update(disabled = False)
        window['-SPG-'].update(disabled=True)
        window['-CELL-'].update(disabled=True)
    if event == '-SGREF-' and values['-SGREF-'] == True:
        window['-FREECOPY-'].update(disabled = True)
        window['-FREECOPY-'].update(value = False)
        window['-SPG-'].update(value = "", disabled = True)
        window['-CELL-'].update(value = "", disabled = True)
        window['-REF-'].update(disabled = False)
        window['-REFBROWSE-'].update(disabled = False)
        window['-SGMAN-'].update(value = False, disabled = True)
    if event == '-SGREF-' and values['-SGREF-'] == False:
        window['-FREECOPY-'].update(disabled = False)
        window['-FREECOPY-'].update(value = False) 
        window['-SGMAN-'].update(disabled = False)
        window['-REF-'].update(disabled = True)
        window['-REFBROWSE-'].update(disabled = True)
    if event == '-ENABLEMACRO-' and values['-ENABLEMACRO-'] == True :
        window['-CUSTPAR-']. update(disabled = True, value = False)
        window['-MACRO-'].update(disabled=False)
        window['-LISTMACROS-'].update(disabled=False)       
        custpars = ''
    if event == '-ENABLEMACRO-' and values['-ENABLEMACRO-'] == False :
        window['-MACRO-'].update(disabled=True)
        window['-LISTMACROS-'].update(disabled=True)
        window['-CUSTPAR-'].update(disabled = False)
    if event == '-SWEEPSET-' and values ['-SWEEPSET-'] == True:
        oldcntr = 0
        setsweeps = ''
        window['-SWEEPRANGE-'].update(disabled=False)
    if event == '-SWEEPSET-' and values ['-SWEEPSET-'] == False:
        oldcntr = 0
        setsweeps = ''
        window['-SWEEPRANGE-'].update(disabled=True)
        sweepcommands = ''
    if event == '-CUTSEL-':
        if values['-CUTSEL-'] == "CC(1/2)>=0.3 (default)":                             
            window['-ISIGIVAL-'].update('0.0', disabled=True)
            window['-CCHALFVAL-'].update('0.3', disabled=True)
            window['-RPIMVAL-'].update('99.9', disabled=True)
        if values['-CUTSEL-'] == "I/sig(I)>=2.0, CC(1/2)>=0.3, Rpim<=0.6 (old default)":
            window['-ISIGIVAL-'].update('2.0', disabled=True)
            window['-CCHALFVAL-'].update('0.3', disabled=True)
            window['-RPIMVAL-'].update('0.6', disabled=True)   
        if values['-CUTSEL-'] == "Custom values for I/sig(I), CC(1/2), Rpim":
            window['-ISIGIVAL-'].update(disabled=False)
            window['-CCHALFVAL-'].update(disabled=False)
            window['-RPIMVAL-'].update(disabled=False)
        
    if event == '-PARSON-' and values['-PARSON-'] == True:
        sg.popup('Everything added here will be appended to the command line "as is"!\n\nMake sure you know what you are doing!\n', title = "Caution!", location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        window['-EXTRAPARS-'].update(disabled=False)
    if event == '-PARSON-' and values['-PARSON-'] == False:   
        window['-EXTRAPARS-'].update(disabled=True)
    if event == '-ANOMYES-':   
        window['-ANOMLARGE-'].update(disabled=False)
    if event == '-ANOMNO-' or event == '-ANOMAUTO-':   
        window['-ANOMLARGE-'].update(False, disabled=True)

    if beamcentremode == "specified below":
        window['-BEAMX-'].update(disabled=False)
        window['-BEAMY-'].update(disabled=False)
        window['-BEAMX-'].update(value= beamcentrex)
        window['-BEAMX-'].update(value= beamcentrey)
    if distance != "n/a" and distance != "":
        window['-DISTBOX-'].update(value=True)
        window['-DIST-'].update(disabled=False)
        window['-DIST-'].update(value= distance)    
    if wavelength != "n/a" and wavelength != "":
        window['-WLBOX-'].update(value=True)
        window['-WAVEL-'].update(disabled=False)
        window['-WAVEL-'].update(value= wavelength)
    if oscillation != "n/a" and oscillation != "":
        window['-OSCBOX-'].update(value=True)
        window['-OSC-'].update(disabled=False)
        window['-OSC-'].update(value= oscillation)
    if overload != "n/a" and overload != "":
        window['-OVERLOADBOX-'].update(value=True)
        window['-OVERLOAD-'].update(disabled=False)
        window['-OVERLOAD-'].update(value= overload)
    if pixelsizex != "n/a" and pixelsizex != "" and pixelsizey != "n/a" and pixelsizey != "":    
        window['-PIXELSIZEBOX-'].update(value=True)
        window['-XPIXELSIZE-'].update(disabled=False)
        window['-YPIXELSIZE-'].update(disabled=False)
        window['-XPIXELSIZE-'].update(value= pixelsizex)
        window['-YPIXELSIZE-'].update(value= pixelsizey)
    if nopixelx != "n/a" and nopixelx != "" and nopixely != "n/a" and nopixely != "":    
        window['-PIXELNUMBOX-'].update(value=True)
        window['-XPIXELS-'].update(disabled=False)
        window['-YPIXELS-'].update(disabled=False)
        window['-XPIXELS-'].update(value= nopixelx)
        window['-YPIXELS-'].update(value= nopixely) 
    if event == '-BEAMCENTREMODE-' and values['-BEAMCENTREMODE-'] == "specified below":
        window['-BEAMX-'].update(disabled=False)
        window['-BEAMY-'].update(disabled=False)
    if event == '-BEAMCENTREMODE-' and values['-BEAMCENTREMODE-'] != "specified below":  
        window['-BEAMX-'].update(disabled=True)
        window['-BEAMY-'].update(disabled=True)
    if event == '-DISTBOX-' and values['-DISTBOX-'] == True:
        window['-DIST-'].update(disabled=False)
    if event == '-DISTBOX-' and values['-DISTBOX-'] == False:   
        window['-DIST-'].update(disabled=True)
    if event == '-WLBOX-' and values['-WLBOX-'] == True:
        window['-WAVEL-'].update(disabled=False)
    if event == '-WLBOX-' and values['-WLBOX-'] == False:   
        window['-WAVEL-'].update(disabled=True)
    if event == '-OSCBOX-' and values['-OSCBOX-'] == True:
        window['-OSC-'].update(disabled=False)
    if event == '-OSCBOX-' and values['-OSCBOX-'] == False:   
        window['-OSC-'].update(disabled=True)
    if event == '-OVERLOADBOX-' and values['-OVERLOADBOX-'] == True:
        window['-OVERLOAD-'].update(disabled=False)
    if event == '-OVERLOADBOX-' and values['-OVERLOADBOX-'] == False:   
        window['-OVERLOAD-'].update(disabled=True)     
    if event == '-PIXELSIZEBOX-' and values['-PIXELSIZEBOX-'] == True:
        window['-XPIXELSIZE-'].update(disabled=False)
        window['-YPIXELSIZE-'].update(disabled=False)
    if event == '-PIXELSIZEBOX-' and values['-PIXELSIZEBOX-'] == False:   
        window['-XPIXELSIZE-'].update(disabled=True)
        window['-YPIXELSIZE-'].update(disabled=True)
    if event == '-PIXELNUMBOX-' and values['-PIXELNUMBOX-'] == True:
        window['-XPIXELS-'].update(disabled=False)
        window['-YPIXELS-'].update(disabled=False)
    if event == '-PIXELNUMBOX-' and values['-PIXELNUMBOX-'] == False:   
        window['-XPIXELS-'].update(disabled=True)
        window['-YPIXELS-'].update(disabled=True)

    # Reference/FreeR MTZ browsing and extension
    if event == '-REFBROWSE-':
        refval = values['-REF-']
        layout_refbrowse = [[sg.Col([[sg.Text('Select MTZ for freeR-flags or as reference.', justification = 'center', font = "Arial 12")]], justification = 'center', element_justification = 'center')],
                            [sg.Input(refval, key='-REFBROWSEPATH-', visible=False, enable_events=True)],
                            [sg.Text('Do you want to extend the freeR-flags to high resolution\nand generate a reference MTZ suitable for any future dataset of this protein?\n(Recommended if you have not already done this)', justification = 'center')],
                            [sg.Col([[sg.Button('Yes', highlight_colors = (theme_color, theme_color), size = (8, 1), tooltip = 'Extend freeR-flags to high resolution'),
                              sg.FileBrowse(initial_folder = outpath, button_text = 'No', size = (8, 1), key ='-REFSELECT-', tooltip = 'Browse for reference / freeR MTZ.', target = '-REFBROWSEPATH-',file_types = (('Reference MTZ', ('*.mtz', '*.MTZ')),)),
                             sg.Button('Cancel', highlight_colors = (theme_color, theme_color), size = (8, 1))]], justification = 'center', element_justification = 'center')]]  
        window_refbrowse = sg.Window('Select MTZ', layout_refbrowse, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_refbrowse, values_refbrowse = window_refbrowse.read()
            if event_refbrowse == '-REFBROWSEPATH-':
                if re.search(" ", values_refbrowse['-REFBROWSEPATH-']) != None:
                    print('')
                    print('Problem found in:', values_refbrowse['-REFBROWSEPATH-'])
                    print('Path to MTZ must not contain any white space characters!')
                    status = '  Path to MTZ must not contain any white space characters!'
                    window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')
                else:    
                    window['-REF-'].update(value = values_refbrowse['-REFBROWSEPATH-'])
                    window_refbrowse.close()
                    layout_refbrowse = None
                    window_refbrowse = None
                    gc.collect()
                    status = ' \u2691  Ready.'
                    window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
                    break
            if event_refbrowse == sg.WIN_CLOSED or event_refbrowse == 'Cancel':
                window_refbrowse.close()
                layout_refbrowse = None
                window_refbrowse = None
                gc.collect()
                status = ' \u2691  Ready.'
                window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
                break
            if event_refbrowse == 'Yes':
                layout_makeref = [[sg.Text('Input MTZ:', size = (15, None)), sg.Input(refval, key='-MAKEREFINBROWSEPATH-', visible=True, size = (25, None), enable_events=True), sg.FileBrowse(initial_folder = outpath, button_text = 'Browse', tooltip = 'Browse for reference / freeR MTZ.', target = '-MAKEREFINBROWSEPATH-',file_types = (('Reference MTZ', ('*.mtz', '*.MTZ')),))],
                                  [sg.Text('Output folder:', size = (15, None)), sg.Input(key='-MAKEREFOUTBROWSEPATH-', visible=True, size = (25, None), enable_events=True), sg.FolderBrowse(initial_folder = outpath, button_text = 'Browse', tooltip = 'Select output directory', target = '-MAKEREFOUTBROWSEPATH-')],
                                  [sg.Text('Extend to:'), sg.Input('1.0', key='-REFRESO-', visible=True, size = (4, None)),sg.Text('Å', size = (4, None)), sg.Button('Run', highlight_colors = (theme_color, theme_color), size = (8, 1)), sg.Button('Cancel', highlight_colors = (theme_color, theme_color), size = (8, 1))]]
                window_makeref = sg.Window('Expand MTZ', layout_makeref, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
                while True:
                    event_makeref, values_makeref = window_makeref.read()
                    if event_makeref == sg.WIN_CLOSED or event_makeref == 'Cancel':
                        window_makeref.close()
                        layout_makeref = None
                        window_makeref = None
                        gc.collect()                
                        break
                    if event_makeref == 'Run':
                        if os.path.exists(values_makeref['-MAKEREFINBROWSEPATH-']) == False:
                            print('')
                            print("No valid input file!")
                        elif os.path.exists(values_makeref['-MAKEREFOUTBROWSEPATH-']) == False:
                            print('')
                            print("Output path does not exist!")
                        elif re.search(" ", values_makeref['-MAKEREFINBROWSEPATH-']) != None:
                            print('')
                            print('Problem found in:', values_makeref['-MAKEREFINBROWSEPATH-'])
                            print('Path to MTZ must not contain any white space characters!')
                            status = '  Path to MTZ must not contain any white space characters!'
                            window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')
                        else:
                            print('')
                            print("Preparing reference MTZ, this might take a moment...")
                            status = ' \u231b  Preparing reference MTZ, this might take a moment...'
                            window['-STAT-'].update(value = status, text_color = 'black', background_color = 'yellow')
                            time.sleep(0.2)
                            mtzfilein = values_makeref['-MAKEREFINBROWSEPATH-']
                            refmtzout = re.sub(".mtz", "_REFERENCE.mtz", mtzfilein)
                            #print(refmtzout)
                            refmtzout = refmtzout.rsplit('/', 1)[1]
                            #print(refmtzout)
                            refmtzout = os.path.join(values_makeref['-MAKEREFOUTBROWSEPATH-'],refmtzout)
                            #print(refmtzout)
                            set_reso = values_makeref['-REFRESO-']
                            refmtzexpand(mtzfilein, refmtzout, set_reso)
                    if event_makeref == '-REFMTZDONE-': 
                        print('Reference MTZ generated:', refmtzout)
                        print('')
                        window['-REF-'].update(value = refmtzout)
                        status = ' \u2691  Ready.'
                        window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)  
                        window_makeref.close()
                        layout_makeref = None
                        window_makeref = None
                        window_refbrowse.close()
                        gc.collect()                
                        break
            
 # show about section
    if event == '-ABOUT-' or event == '-LOGOBUTTON-':
        layout_about = [[sg.Text(win_title, justification = "left", font = "Arial 12", text_color = theme_color)],
                               [sg.Text('A simple interface to autoPROC (Global Phasing Ltd.)')],
                               [sg.HorizontalSeparator(color = None,)],
                               [sg.Text('\u00A9 Copyright 2025 Peer Lukat\nHelmholtz-Centre for Infection Research, Structure & Function of Proteins\npeer.lukat@helmholtz-hzi.de\nAutoGUI is released under the GNU General Public License Version 3 (or later).\nThere is (currently) no literature citation for it.')],
                               [sg.HorizontalSeparator(color = None,)],
                               [sg.Text('autoPROC is developed by Global Phasing Limited (UK)\nhttps://www.globalphasing.com')],
                               [sg.Text('For using autoPROC via AutoGUI, please cite:')],
                               [sg.Text('autoPROC:\nVonrhein, C., Flensburg, C., Keller, P., Sharff, A., Smart, O., Paciorek, W.,\nWomack, T. and Bricogne, G. (2011). Data processing and analysis with\nthe autoPROC toolbox. Acta Cryst. D67, 293-302.')],
                               [sg.Text('XDS/XSCALE:\nKabsch, W. (2010). XDS. Acta Cryst. D66, 125-132.')],
                               [sg.Text('POINTLESS:\nEvans, P.R. (2006). Scaling and assessment of data quality, Acta Cryst. D62, 72-82.')],
                               [sg.Text('CCP4:\nWinn, M.D., Ballard, C.C., Cowtan, K.D. Dodson, E.J., Emsley, P., Evans, P.R.,\nKeegan, R.M., Krissinel, E.B., Leslie, A.G.W., McCoy, A., McNicholas, S.J., Murshudov,\nG.N., Pannu, N.S., Potterton, E.A., Powell, H.R., Read, R.J., Vagin, A. and Wilson, K.S.\n(2011). Overview of the CCP4 suite and current developments, Acta. Cryst. D67, 235-242.')], 
                               [sg.Text('STARANISO:\nTickle, I.J., Flensburg, C., Keller, P., Paciorek, W., Sharff, A., Vonrhein, C.,\nand Bricogne, G. (2018-2021). STARANISO. Cambridge, United Kingdom: Global Phasing Ltd.')],
                               [sg.Text('AutoGUI is also using Adxv:\nArvai, A. Adxv - A Program to Display X-ray Diffraction Images,\nhttps://www.scripps.edu/tainer/arvai/adxv.html')],
                               [sg.HorizontalSeparator(color = None,)],
                               [sg.Button('Okay', highlight_colors = (theme_color, theme_color)), sg.Button('Changelog', button_color = (theme_color, theme_color1), mouseover_colors = (theme_color1, theme_color), highlight_colors = (theme_color, theme_color)), sg.Button('License information', button_color = (theme_color, theme_color1), mouseover_colors = (theme_color1, theme_color), highlight_colors = (theme_color, theme_color)),
                                sg.Text('Toggle error console', size = (35, None), justification = 'right', text_color = '#D0D0D0', tooltip = 'Developer only!'), sg.Checkbox('', tooltip = 'Developer only!', default = show_errors, key = '-ERRTOGGLE-', text_color = '#D0D0D0', enable_events = True)]] 
            
        window_about = sg.Window('About', layout_about, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_about, values_about = window_about.read()
            if event_about == '-ERRTOGGLE-' and values_about['-ERRTOGGLE-'] == True:
                window['-DEBUG-'].update(visible = True)
                fault_out = open(os.path.join(current_path, "autogui_classic_faults.log"), mode="w")
                faulthandler.enable(fault_out)
                show_errors = True
                #window['-ERROR-'].restore_stderr()     unfortunately there seems to be a bug in PySimpleGUI that this does not work
                #window['-OUTPUT-'].restore_stdout()    if stdout or stderr have been rerouted to a multiline element
            if event_about == '-ERRTOGGLE-' and values_about['-ERRTOGGLE-'] == False:
                window['-DEBUG-'].update(visible = False)
                faulthandler.disable()
                fault_out.close()
                show_errors = False
                os.remove(os.path.join(current_path, "autogui_classic_faults.log"))
                #window['-OUTPUT-'].reroute_stdout_to_here()    this works, but disabling rerouting does not work
                #window['-ERROR-'].reroute_stderr_to_here()     (see above)
            if event_about == sg.WIN_CLOSED or event_about == 'Okay':
                window_about.close()
                layout_about = None
                window_about = None
                gc.collect()
                break    
            if event_about == 'Changelog':
                layout_changes = [[sg.Multiline(size=(75,20), key='-CHANGELOG-', write_only = True, autoscroll = False, do_not_clear = True, text_color = theme_color, background_color = theme_color1)],
                                  [sg.Button('Okay', highlight_colors = (theme_color, theme_color))]]
                window_changes = sg.Window("What's new?", layout_changes, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
                if os.path.exists(changelog_path) == True:
                    f =  open(changelog_path, "r")
                    clog = f.read()
                    window_changes['-CHANGELOG-'].print(clog)
                    window_changes['-CHANGELOG-']. set_vscroll_position(0)
                    f.close()
                else:
                    window_changes['-CHANGELOG-'].print('')
                    window_changes['-CHANGELOG-'].print('autogui_changelog.txt not found!')
                    window_changes['-CHANGELOG-'].print('Sorry!')
                    window_changes['-CHANGELOG-'].print('')
                while True:
                    event_changes, values_changes = window_changes.read()    
                    if event_changes == sg.WIN_CLOSED or event_changes == 'Okay':
                        window_changes.close()
                        layout_changes = None
                        window_changes = None
                        gc.collect()
                        break
                    
            if event_about == 'License information':
                layout_license = [[sg.Multiline(size=(75,20), key='-LICENSE-', write_only = True, autoscroll = False, do_not_clear = True, text_color = theme_color2, background_color = theme_color1)],
                                  [sg.Button('Okay', highlight_colors = (theme_color, theme_color))]]
                window_license = sg.Window("GPL-3.0-or-later", layout_license, no_titlebar=False, alpha_channel=1, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
                
                if os.path.exists(license_path) == True:
                    f =  open(license_path, "r")
                    lic = f.read()
                    window_license['-LICENSE-'].print(lic)
                    window_license['-LICENSE-']. set_vscroll_position(0)
                    f.close()
                else:
                    window_license['-LICENSE-'].print('')
                    window_license['-LICENSE-'].print('COPYING not found!')
                    window_license['-LICENSE-'].print('Sorry!')
                    window_license['-LICENSE-'].print('')
                while True:
                    event_license, values_license = window_license.read()    
                    if event_license == sg.WIN_CLOSED or event_license == 'Okay':
                        window_license.close()
                        layout_license = None
                        window_license = None
                        gc.collect()
                        break        
    
    # open image  in Adxv
    if event == 'Check images in Adxv':
        if EIGER == True:
            h5 = values['-HDF5-']
            source = "/".join(h5.split("/")[:-1])
        else:    
            source = values['-IMGS-']
        if os.path.exists(source) == True:
            #print (adxvpath)
            adxv = adxvpath + ' -rings ' + source + "/"
            #print(adxv)
            run_adxv(adxv)
            print('')
            print('Started Adxv in', source)
        else:
            print('')
            print('Image folder does not exist.')
            

    # get image list and first image info to data field
    if event == '-DSNUMIMGS-':
       ds_numimgs = values['-DSNUMIMGS-'] 
    if event == '-IMAGESSET-':
        #print(values['-FIRSTIMAGESET-'])
        if EIGER == True:
            h5 = values['-HDF5-']
            source = "/".join(h5.split("/")[:-1])
        else:    
            source = values['-IMGS-']
        img_hit_list = values['-IMAGESSET-']
        if img_hit_list[0] != "" and os.path.exists(img_hit_list[0]) == True:
            if EIGER == True:
                info_image = values['-HDF5-']
            else:
                info_image = img_hit_list[0]
            ds_name = re.split ("_[^_]+$", info_image)[0]
            ds_name = ds_name.split('/')[-1]
            fieldupdate = True
            window['-IMGINFO-'].update(value = '')
            imginfo_function(info_image)
            window['-XDSINPLOAD-'].update(disabled = False)
            window['-IMGHEADERVALS-'].update(disabled = False)
            window['-IMAGEEDIT-'].update(disabled = False)  
        else:
            print('')
            print('Image folder does not exist.')


    if event == '-IMGHEADERVALS-':
        print('')
        print("Reset to header values (from first image)")
        fieldupdate = True
        xdsupdate = False
        window['-IMGINFO-'].update(value = '')
        imginfo_function(info_image)
        window['-PIXELNUMBOX-'].update(value=False)
        window['-XPIXELS-'].update(disabled=True)
        window['-YPIXELS-'].update(disabled=True)
        window['-PIXELSIZEBOX-'].update(value=False)
        window['-XPIXELSIZE-'].update(disabled=True)
        window['-YPIXELSIZE-'].update(disabled=True)
        window['-OVERLOADBOX-'].update(value=False)
        window['-OVERLOAD-'].update(disabled=True)
        window['-OSCBOX-'].update(value=False)
        window['-OSC-'].update(disabled=True)
        window['-WLBOX-'].update(value=False)
        window['-WAVEL-'].update(disabled=True)
        window['-DISTBOX-'].update(value=False)
        window['-DIST-'].update(disabled=True)
        window['-BEAMX-'].update(disabled=True)
        window['-BEAMY-'].update(disabled=True)
        window['-BEAMCENTREMODE-'].update(value = 'header')

    if event == '-XDSINP-':
        if os.path.exists(values['-XDSINP-']) == True:
            xds_inp = values['-XDSINP-']
            values_from_xds(xds_inp)
            print('')     
            print("Values updated from XDS.INP")
            xdsupdate = True
            window['-PIXELNUMBOX-'].update(value=False)
            window['-XPIXELS-'].update(disabled=True)
            window['-YPIXELS-'].update(disabled=True)
            window['-PIXELSIZEBOX-'].update(value=False)
            window['-XPIXELSIZE-'].update(disabled=True)
            window['-YPIXELSIZE-'].update(disabled=True)
            window['-OVERLOADBOX-'].update(value=False)
            window['-OVERLOAD-'].update(disabled=True)
            window['-OSCBOX-'].update(value=False)
            window['-OSC-'].update(disabled=True)
            window['-WLBOX-'].update(value=False)
            window['-WAVEL-'].update(disabled=True)
            window['-DISTBOX-'].update(value=False)
            window['-DIST-'].update(disabled=True)
            window['-BEAMX-'].update(disabled=True)
            window['-BEAMY-'].update(disabled=True)
            window['-BEAMCENTREMODE-'].update(value = 'header')
        else:
            print('')
            print('Invalid XDS.INP file')

    if event == '-IMGSETTINGSDIST-':
        headerdist = (values['-IMGSETTINGSDIST-'])
        if fieldupdate == True or xdsupdate == True:
            window['-DIST-'].update(value = headerdist)
            if xdsupdate == True:
                window['-DISTBOX-'].update(value=True)
                window['-DIST-'].update(disabled=False)     
    if event == '-IMGSETTINGSWL-':
        headerwl = (values['-IMGSETTINGSWL-'])
        if fieldupdate == True or xdsupdate == True:
            window['-WAVEL-'].update(value = headerwl)
            if xdsupdate == True:
                window['-WLBOX-'].update(value=True)
                window['-WAVEL-'].update(disabled=False) 
    if event == '-IMGSETTINGSXSIZE-':
        headerxsize =( values['-IMGSETTINGSXSIZE-'])
        if fieldupdate == True or xdsupdate == True:
            window['-XPIXELSIZE-'].update(value = headerxsize)
            if xdsupdate == True:
                window['-PIXELSIZEBOX-'].update(value=True)
                window['-XPIXELSIZE-'].update(disabled=False)
                window['-YPIXELSIZE-'].update(disabled=False) 
    if event == '-IMGSETTINGSYSIZE-':
        headerysize = (values['-IMGSETTINGSYSIZE-'])
        if fieldupdate == True or xdsupdate == True:
            window['-YPIXELSIZE-'].update(value = headerysize)
            if xdsupdate == True:
                window['-PIXELSIZEBOX-'].update(value=True)
                window['-YPIXELSIZE-'].update(disabled=False)
                window['-XPIXELSIZE-'].update(disabled=False) 
    if event == '-IMGSETTINGSXNUM-':
        headerxpixels = (values['-IMGSETTINGSXNUM-'])
        if fieldupdate == True or xdsupdate == True:
            window['-XPIXELS-'].update(value = headerxpixels)
            if xdsupdate == True:
                window['-PIXELNUMBOX-'].update(value=True)
                window['-XPIXELS-'].update(disabled=False)
                window['-YPIXELS-'].update(disabled=False) 
    if event == '-IMGSETTINGSYNUM-':
        headerypixels = (values['-IMGSETTINGSYNUM-'])
        if fieldupdate == True or xdsupdate == True:
            window['-YPIXELS-'].update(value = headerypixels)
            if xdsupdate == True:
                window['-PIXELNUMBOX-'].update(value=True)
                window['-YPIXELS-'].update(disabled=False)
                window['-XPIXELS-'].update(disabled=False) 
    if event == '-IMGSETTINGSBEAMX-':
        headerbeamx = (values['-IMGSETTINGSBEAMX-'])
        if fieldupdate == True or xdsupdate == True:
            window['-BEAMX-'].update(value = headerbeamx)
            if xdsupdate == True:
                window['-BEAMCENTREMODE-'].update(value = 'specified below') 
                window['-BEAMX-'].update(disabled=False)
                window['-BEAMY-'].update(disabled=False)
    if event == '-IMGSETTINGSBEAMY-':
        headerbeamy = (values['-IMGSETTINGSBEAMY-'])
        if fieldupdate == True or xdsupdate == True:
            window['-BEAMY-'].update(value = headerbeamy)
            if xdsupdate == True:
                window['-BEAMCENTREMODE-'].update(value = 'specified below') 
                window['-BEAMX-'].update(disabled=False)
                window['-BEAMY-'].update(disabled=False)
    if event == '-IMGSETTINGSOSC-':
        headerosc = (values['-IMGSETTINGSOSC-'])
        if fieldupdate == True or xdsupdate == True:
            window['-OSC-'].update(value = headerosc)
            if xdsupdate == True:
                window['-OSCBOX-'].update(value=True)
                window['-OSC-'].update(disabled=False)
    if event == '-IMGSETTINGSOVERLOAD-':
        headeroverload = (values['-IMGSETTINGSOVERLOAD-'])
        if fieldupdate == True or xdsupdate == True:
            window['-OVERLOAD-'].update(value = headeroverload)
            if xdsupdate == True:
                window['-OVERLOADBOX-'].update(value=True)
                window['-OVERLOAD-'].update(disabled=False)
    if event == '-IMGSETTINGS2THETA-':
        headertwotheta = float(values['-IMGSETTINGS2THETA-'])         
        #print("2-Theta:", str(headertwotheta))

    #######GRAPHING########
    # Graphing on diffraction image
    if event =='-IMAGEEDIT-' :
        print('')
        print(separator)
        print("Loading image, this might take a few seconds...")
        status = ' \u231b  Loading image, this might take a few seconds...'
        window['-STAT-'].update(value = status, text_color = 'black', background_color = 'yellow')
        #fieldupdate = False
        #window['-IMGINFO-'].update(value = '')
        #imginfo_function(img_hit_list[0])
        adxvimage = img_hit_list[0]
        adxvoptions ="" 
        #get image from adxv
        if (values['-OVERLOADBOX-'] == True) and (values['-OVERLOAD-'] != 'n/a' and values['-OVERLOAD-'] != ''):    
            adxvoptions = re.sub("\s+", " ", (adxvoptions + " -overload " + values['-OVERLOAD-']))
        if os.path.exists(adxvimage) == False:
            print("Image does not exist!")
        else:
            if adxvoptions == "":
                imgconv_command_1 = adxvpath + " -sa " + adxvimage + " out.jpg"
            else:
                imgconv_command_1 = adxvpath + " "+ adxvoptions + " -sa " + adxvimage + " out.jpg "
            print (imgconv_command_1)
            imgconv_command_2 = "magick out.jpg -resize 800x800 out.png" # needs ImageMagick
            #print (imgconv_command_2)
            imgconv_command_3 = "./out.jpg"
            #print (imgconv_command_3)
            conv_first_image = True
            imgconv_function(imgconv_command_1,imgconv_command_2,imgconv_command_3, conv_first_image)
    if event == '-IMGCONVDONE-':
        print("Image loaded.")
        print('')
        status = ' \u2691  Ready.'
        window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
        im = Image.open('out.png')
        diffractionimagesize = im.size
        # correct beam position offset due to 2-theta angle
        if headertwotheta != 0:     #calculates pixel shift of x-beam due to 2 theta not zero
            htemp = (float(headerdist)) * (1 - (math.cos(math.radians(abs(headertwotheta) * 0.5))))
            print("Distance:   ", str(headerdist), "mm")
            print("2-Theta:    ", str(headertwotheta), "°")
            print("Pixelsize:  ", str(float(headerxsize)))
            xoffset = (2 * math.sqrt((2 * float(headerdist) * htemp) - (pow(htemp,2))))/float(headerxsize)
            if headertwotheta < 0:
                xoffset = - xoffset
            print("X-Offset:   ", str(0 - round(xoffset)), "px")
        else:
            xoffset = 0
        # define beam position    
        if (values['-BEAMCENTREMODE-'] == 'specified below') and (values['-BEAMX-'] != 'n/a' and values['-BEAMX-'] != '') and (values['-BEAMY-'] != 'n/a' and values['-BEAMY-'] != ''):
            x_imgval = round(float(values['-BEAMX-']) - xoffset)
            y_imgval = round(float(values['-BEAMY-']))
        else:
            x_imgval = round(float(headerbeamx) - xoffset)
            y_imgval = round(float(headerbeamy))
        oldximgval = (x_imgval + xoffset)
        oldyimgval = y_imgval
        old_beamcenter = (oldximgval, oldyimgval)
        # set up cordinate system and variables
        if (values['-PIXELNUMBOX-'] == True) and (values['-XPIXELS-'] != 'n/a' and values['-XPIXELS-'] != '') and (values['-YPIXELS-'] != 'n/a' and values['-YPIXELS-'] != ''):   
            toprightx = (int(values['-XPIXELS-'])-1)
            bottomlefty = (int(values['-YPIXELS-'])-1)
        else:
            toprightx = int(headerxpixels)-1
            bottomlefty = int(headerypixels)-1
        circlecoord1set = False
        circlecoord2set = False
        circle2coord1set = False
        circle2coord2set = False
        rectanglecoord1set = False
        mycircle = None
        rectanglecoord1set = False
        qcoordset = 0
        modified_beamcenter = []
        untrusted_rectangles = []
        untrusted_ellipses = []
        untrusted_quads = []
        dectris_gaps = []
        resoringplots = []
        resoringnumbers = []
        iceringplots = []
        coorddisplay = []
        coorddisplaytext = []
        coorddisplaytextshadows = []
        coorddisplayshadows = [] 
        pointdisplay = []
        pointdisplayshadows = []
        image_index = '1'
        modified_beamcenter =""
        diffractionimagesize = im.size
        crosshairsize = (toprightx/50)/2               
        listvals_none= ["n/a"]
        listvals_beamcentre = ["Fit beamcentre from circle (3 clicks)", "Click to set beamcentre"]
        listvals_mask = ["Quadrilateral mask (4 clicks)", "Rectangular mask (2 clicks)", "Circular mask (3 clicks)", "Oval mask (2 clicks)", "Click on masks to delete"]                  
        old_untrusted_rectangle_coords = untrusted_rectangle_coords[:]
        old_untrusted_ellipse_coords = untrusted_ellipse_coords[:]
        old_untrusted_quad_coords = untrusted_quad_coords[:]
        old_dectris_gap_coords = dectris_gap_coords[:]
        if (values['-DISTBOX-'] == True) and (values['-DIST-'] != 'n/a' and values['-DIST-'] != ''):    
            graph_dist = values['-DIST-']
        else:    
            graph_dist = headerdist
        if (values['-WLBOX-'] == True) and (values['-WAVEL-'] != 'n/a' and values['-WAVEL-'] != ''):    
            graph_wl = values['-WAVEL-']
        else:   
            graph_wl = headerwl
        if (values['-PIXELSIZEBOX-'] == True) and (values['-XPIXELSIZE-'] != 'n/a' and values['-XPIXELSIZE-'] != '') and (values['-YPIXELSIZE-'] != 'n/a' and values['-YPIXELSIZE-'] != ''):    
            graph_xsize = values['-XPIXELSIZE-']
            graph_ysize = values['-YPIXELSIZE-']
        else:   
            graph_xsize = headerxsize 
            graph_ysize = headerysize 
        if (values['-PIXELNUMBOX-'] == True) and (values['-XPIXELS-'] != 'n/a' and values['-XPIXELS-'] != '') and (values['-YPIXELS-'] != 'n/a' and values['-YPIXELS-'] != ''):   
            graph_xpixels = values['-XPIXELS-']
            graph_ypixels = values['-YPIXELS-']
        else:    
            graph_xpixels = headerxpixels
            graph_ypixels = headerypixels 

        # window layout
        layout_imageview = [[sg.Frame(layout=[
                [sg.Text('Mode:'), sg.Combo(("Read coordinates", "Beamcentre", "Masking", "Define HPAD gaps"),
                default_value = "Read coordinates", key = '-FITMODE-', size=(25,4), readonly = True, change_submits = True, enable_events = True),                           
                sg.Text('    Action:'), sg.Combo((listvals_none),
                default_value = "n/a", key = '-FITWHAT-', size=(35,5), readonly = True, change_submits = True, enable_events = True),
                sg.Text('', size = (5, None)),sg.Text('X:'),sg.Text(str(x_imgval), key = '-XIMGVAL-', size = (8, None)), sg.Text('Y:'), sg.Text(str(y_imgval), key = '-YIMGVAL-', size = (8, None))],
                [sg.Button('<', key = '-PREVIMG-', highlight_colors = (theme_color, theme_color), tooltip = 'load previous image', size = (1, 1), enable_events = True),
                 sg.Button('>', key = '-NEXTIMG-', highlight_colors = (theme_color, theme_color), tooltip = 'load next image', size = (1, 1), enable_events = True),
                 sg.Input(image_index, key = '-GOTOIMGNO-', tooltip = 'image number to display', size = (6, None)), 
                 sg.Combo(("1 slab", "5 slabs", "10 slabs", "20 slabs"), default_value = "1 slab", key ="-SLABS-", size = (8,4), readonly = True, change_submits = True, enable_events = True, visible = EIGER),
                 sg.Button("Load image", key = '-GOTOIMG-', highlight_colors = (theme_color, theme_color), tooltip = 'load given image', enable_events = True),
                 sg.Text('', size = (2, 1)),
                 sg.Checkbox("Show resolution rings", key = '-SHOWRINGS-', default = False, enable_events = True), sg.Spin(values = ('1','2','3','4','5','6','7','8','9','10'), initial_value= "5", key='-NUMRINGS-',size=(4,1), text_color = 'black', enable_events = True, readonly = True),
                 sg.Checkbox("Mark regions of potential ice rings", key = '-ICERINGS-', default = False, enable_events = True, tooltip =' Ice ring regions according to Kumai, M. (1967)')],
                [sg.Frame(layout=[
                [sg.Graph(canvas_size = diffractionimagesize, graph_bottom_left = (0,bottomlefty), graph_top_right = (toprightx,0), enable_events = True, drag_submits = True, key = '-IMGAREA-')]
                ],title= 'Diffraction image', title_color=theme_color, relief=sg.RELIEF_GROOVE, element_justification = "left", vertical_alignment='center')],
                [sg.Button('Accept', highlight_colors = (theme_color, theme_color)), sg.Button('Cancel', highlight_colors = (theme_color, theme_color))]
                ], title= None, title_color=theme_color, relief= None, element_justification = "left", pad = (0,0), vertical_alignment='center')]]
               
        # draw stuff
        window_imageview = sg.Window('Fit beamcentre & mask regions', layout_imageview, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        diffractionimage = window_imageview['-IMGAREA-'].draw_image(filename = 'out.png', location = (0,0))
        imagebeamcentrex = window_imageview['-IMGAREA-'].draw_line(point_from =((x_imgval-crosshairsize), y_imgval ), point_to =((x_imgval+crosshairsize), y_imgval), color = 'blue', width = 2)
        imagebeamcentrey = window_imageview['-IMGAREA-'].draw_line(point_from =(x_imgval, (y_imgval-crosshairsize)), point_to =(x_imgval, (y_imgval+crosshairsize)), color = 'blue', width = 2)
        graphbbox = window_imageview['-IMGAREA-'].TKCanvas.bbox(diffractionimage)
        if dectris_gap_coords != []:
            for gap in dectris_gap_coords:
                gap = window_imageview['-IMGAREA-'].DrawRectangle((gap[0],gap[2]), (gap[1],gap[3]), fill_color = 'yellow', line_color = None, line_width = 0)
                dectris_gaps.append(gap)
        if untrusted_rectangle_coords != []:
            for rectangle in untrusted_rectangle_coords:
                untrusted_rectangle = window_imageview['-IMGAREA-'].DrawRectangle((rectangle[0],rectangle[2]), (rectangle[1],rectangle[3]), fill_color = None, line_color = 'red', line_width = 3)
                untrusted_rectangles.append(untrusted_rectangle)
        if untrusted_ellipse_coords != []:
            for ellipse in untrusted_ellipse_coords:
                untrusted_ellipse = window_imageview['-IMGAREA-'].draw_oval((ellipse[0], ellipse[2]), (ellipse[1], ellipse[3]), fill_color = None, line_color = 'red', line_width = 3)
                untrusted_ellipses.append(untrusted_ellipse)        
        if untrusted_quad_coords != []:
            for xds_coords in untrusted_quad_coords:
                quad_line_1 = window_imageview['-IMGAREA-'].draw_line(xds_coords[0], xds_coords[1], color = 'red', width = 3)
                quad_line_2 = window_imageview['-IMGAREA-'].draw_line(xds_coords[1], xds_coords[3], color = 'red', width = 3)
                quad_line_3 = window_imageview['-IMGAREA-'].draw_line(xds_coords[3], xds_coords[2], color = 'red', width = 3)
                quad_line_4 = window_imageview['-IMGAREA-'].draw_line(xds_coords[2], xds_coords[0], color = 'red', width = 3)
                untrusted_quad = [quad_line_1, quad_line_2, quad_line_3, quad_line_4]
                untrusted_quads.append(untrusted_quad)
        window_imageview['-IMGAREA-'].bring_figure_to_front(imagebeamcentrex)
        window_imageview['-IMGAREA-'].bring_figure_to_front(imagebeamcentrey)        

        if numfoundsweeps > 1:
            # warn for masking multi sweep DS
            layout_multi_mask = [[sg.Text('Attention!', justification = "center", font = "Arial 12", text_color = "red")],
                   [sg.Text('It seems that you are working with a multi-sweep dataset!\nApplying masks to individual sweeps is currently not supported!')],
                   [sg.Text('This means: If detector distance and/or 2Θ angle differ between the sweeps,\nmasks applied to shadows on the detector (e.g. beam stop) will be wrong for every sweep but the first.\nMasking of features on the detector (e.g. dead pixels) should be okay.')],
                   [sg.Text('Resolution-/ice-rings and beam centre will also be only correctly displayed for the first sweep of a multi-sweep dataset!')],
                   [sg.Button('Got it', highlight_colors = (theme_color, theme_color))]]           
            window_multi_mask = sg.Window('Attention', layout_multi_mask, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                event_multi_mask, values_multi_mask = window_multi_mask.read()
                if event_multi_mask == sg.WIN_CLOSED or event_multi_mask == 'Got it':
                    window_multi_mask.close()
                    window_multi_mask = None
                    layout_multi_mask = None
                    gc.collect()
                    break
              
        while True:
            event_imageview, values_imageview = window_imageview.read(timeout=100)

            # Move to other images
            if event_imageview == '-PREVIMG-' or event_imageview == '-NEXTIMG-' or event_imageview == '-GOTOIMG-':  
                if event_imageview == '-PREVIMG-':
                    if int(image_index) > 1:
                        image_index = str(int(image_index) - 1)
                    else:
                        image_index = '1'
                if event_imageview == '-NEXTIMG-':
                    if int(image_index) <= int(ds_numimgs):
                        image_index = str(int(image_index) + 1)
                    else:
                        image_index = str(ds_numimgs)
                if event_imageview == '-GOTOIMG-'or event_imageview == '-SLABS-':
                    if int(values_imageview['-GOTOIMGNO-']) <= int(ds_numimgs) and int(values_imageview['-GOTOIMGNO-']) >= 1:
                        image_index = str(values_imageview['-GOTOIMGNO-'])
                    elif int(values_imageview['-GOTOIMGNO-']) > int(ds_numimgs):
                        image_index = str(ds_numimgs)
                    elif int(values_imageview['-GOTOIMGNO-']) < 1:
                        image_index = '1'
                print('')
                print(separator)
                window_imageview['-GOTOIMGNO-'].update(value = image_index)
                print("Loading image, this might take a few seconds...")
                status = ' \u231b  Loading image, this might take a few seconds...'
                window['-STAT-'].update(value = status, text_color = 'black', background_color = 'yellow')
                window_imageview['-GOTOIMG-'].update(disabled = True)
                window_imageview['-PREVIMG-'].update(disabled = True)
                window_imageview['-NEXTIMG-'].update(disabled = True)
                if EIGER == True:
                    slab = 0
                    if values_imageview['-SLABS-'] == "10 slabs":
                        nslabs = 10
                    elif values_imageview['-SLABS-'] == "5 slabs":
                        nslabs = 5
                    elif values_imageview['-SLABS-'] == "20 slabs":
                        nslabs = 20
                    else:
                        nslabs = 1           
                    container = 0
                    slab_counter = int(image_index)
                    while (slab_counter) > 1000:
                        container = container + 1
                        slab_counter = slab_counter - 1000
                        #print(str(slab_counter))
                    if slab_counter > nslabs:
                        slab_counter = slab_counter - (nslabs-1)   
                    slab = str(slab_counter)
                    #print(slab)
                    adxvimage = img_hit_list[int(container)]
                    adxvoptions ="-slab " + slab + " -slabs " + str(nslabs)
                    if nslabs > 1:
                        print('Opening container:', img_hit_list[int(container)], '\nSlabs:', slab, '-', (str(slab_counter + (nslabs-1))))
                    else:         
                        print('Opening container:', img_hit_list[int(container)], '\nSlab:', slab)
                    print('')
                else:    
                    adxvimage = img_hit_list[int(image_index)-1]
                    adxvoptions =""
                    print('Opening image:', img_hit_list[int(image_index)-1])
                    print('')
                window_imageview['-IMGAREA-'].DeleteFigure(diffractionimage)
                waitbox = window_imageview['-IMGAREA-'].DrawRectangle((0,bottomlefty),(toprightx,0), fill_color = theme_color, line_color = theme_color , line_width = 1)
                waitmessage = window_imageview['-IMGAREA-'].DrawText('\u231b  Loading image, this might take a few seconds...',(float(toprightx)/2,float(bottomlefty)/2), font=('Arial 14 bold'), color= theme_color1)
                window_imageview['-IMGAREA-'].bring_figure_to_front(waitbox)
                window_imageview['-IMGAREA-'].bring_figure_to_front(waitmessage)
                window_imageview.refresh() 
                #get image from adxv
                if (values['-OVERLOADBOX-'] == True) and (values['-OVERLOAD-'] != 'n/a' and values['-OVERLOAD-'] != ''):    
                    adxvoptions = re.sub("\s+", " ", (adxvoptions + " -overload " + values['-OVERLOAD-']))
                if os.path.exists(adxvimage) == False:
                    print("Image does not exist!")
                else:
                    if adxvoptions == "":
                        imgconv_command_1 = adxvpath + " -sa " + adxvimage + " out.jpg"
                    else:
                        imgconv_command_1 = adxvpath + " " + adxvoptions + " -sa " + adxvimage + " out.jpg "
                    #print (imgconv_command_1)
                    imgconv_command_2 = "magick out.jpg -resize 800x800 out.png" # needs ImageMagick
                    imgconv_command_3 = "./out.jpg"
                    conv_first_image = False
                    imgconv_function(imgconv_command_1,imgconv_command_2,imgconv_command_3, conv_first_image)
            if event_imageview == '-IMGCONVDONE-':
                window_imageview['-IMGAREA-'].DeleteFigure(diffractionimage)
                time.sleep(1)
                print("Image loaded.")
                print('')
                status = ' \u2691  Ready.'
                window['-STAT-'].update(value = status, text_color = theme_color, background_color = theme_color1)
                image_window_open = True
                im = Image.open('out.png')
                diffractionimage = window_imageview['-IMGAREA-'].draw_image(filename = 'out.png', location = (0,0))
                window_imageview['-IMGAREA-'].send_figure_to_back(diffractionimage)
                window_imageview['-IMGAREA-'].DeleteFigure(waitmessage)
                window_imageview['-IMGAREA-'].DeleteFigure(waitbox)
                window_imageview['-GOTOIMG-'].update(disabled = False)
                window_imageview['-PREVIMG-'].update(disabled = False)
                window_imageview['-NEXTIMG-'].update(disabled = False)
  

            #Cancel and remove stored masks if chosen
            if event_imageview == sg.WIN_CLOSED or event_imageview == 'Cancel':
                window_imageview.close()
                layout_imageview = None
                window_imageview = None
                gc.collect()
                untrusted_rectangles = []
                untrusted_ellipses = []
                untrusted_quads = []
                dectris_gaps = []
                modified_beamcenter =""
                os.remove("./out.png")
                
                layout_cancelimg = [[sg.Text("Also delete all existing overlays (masks/gaps)?", justification = "center")],
                                   [sg.Button('Yes', highlight_colors = (theme_color, theme_color)),sg.Button('No', highlight_colors = (theme_color, theme_color))]]
    
                window_cancelimg = sg.Window('Delete overlays?', layout_cancelimg, no_titlebar=False, grab_anywhere=False, finalize = True)
                while True:
                    event_cancelimg, values_cancelimg = window_cancelimg.read(timeout=100)
                    if event_cancelimg == 'Yes':
                        untrusted_rectangle_coords = []
                        untrusted_ellipse_coords = []
                        untrusted_quad_coords = []
                        dectris_gap_coords = []
                        print('')
                        print("Masking cancelled.")
                        print("All masks / overlays deleted.")
                        print(separator)
                        print('')
                        window_cancelimg.close()
                        layout_cancelimg = None
                        window_cancelimg = None
                        gc.collect()
                        break
                    if event_cancelimg == 'No' or event_cancelimg == sg.WIN_CLOSED:
                        untrusted_rectangle_coords = old_untrusted_rectangle_coords
                        untrusted_ellipse_coords = old_untrusted_ellipse_coords
                        untrusted_quad_coords = old_untrusted_quad_coords
                        dectris_gap_coords = old_dectris_gap_coords
                        print('')
                        print("Masking cancelled.")
                        print(separator)
                        print('')
                        window_cancelimg.close()
                        layout_cancelimg = None
                        window_cancelimg = None
                        gc.collect()
                        break
                break

            #Update settings from image
            if event_imageview == 'Accept':
                window_imageview.close()
                layout_imageview = None
                window_imageview = None
                gc.collect()
                os.remove("./out.png")
                print('')
                print("Updated settings from image")
                print(separator)
                print('')
                if modified_beamcenter != "" and modified_beamcenter != old_beamcenter:
                    window['-BEAMCENTREMODE-'].update(value = "specified below" )
                    window['-BEAMX-'].update(value = modified_beamcenter[0])
                    window['-BEAMY-'].update(value = modified_beamcenter[1])
                    window['-BEAMX-'].update(disabled=False)
                    window['-BEAMY-'].update(disabled=False)
                break
        
            if event_imageview == '-FITMODE-' and values_imageview['-FITMODE-'] == "Beamcentre":
                window_imageview['-FITWHAT-'].update(value = "Fit beamcentre from circle (3 clicks)", values = listvals_beamcentre)

            if event_imageview == '-FITMODE-' and values_imageview['-FITMODE-'] == "Masking":
                window_imageview['-FITWHAT-'].update( value = "Quadrilateral mask (4 clicks)", values = listvals_mask)
                
            if event_imageview == '-FITMODE-' and values_imageview['-FITMODE-'] == "Read coordinates":
                window_imageview['-FITWHAT-'].update(value = "n/a", values = listvals_none)    

            # default: read coordinates on click
            if values_imageview['-FITMODE-'] == "Read coordinates":            
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                rectanglecoord1set = False
                qcoordset = 0
                shadowpixeloffset = 1
                shadowxcoords = int((toprightx / graphbbox[2])*shadowpixeloffset)
                shadowycoords = int((bottomlefty / graphbbox[3])*shadowpixeloffset) 
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    if headertwotheta != 0:
                        resotext = "X: " + str(imgcoord[0]) + " Y: " + str(imgcoord[1]) 
                    else:
                        resoradius = math.sqrt((pow((x_imgval - imgcoord[0]),2)) + (pow((y_imgval - imgcoord[1]),2)))
                        twothetaangle = math.atan((float(resoradius)*float(graph_ysize))/float(graph_dist))
                        if twothetaangle == 0:
                            twothetaangle = 0.00001
                        reso = (float(graph_wl)/(math.sin(0.5*twothetaangle)))*0.5
                        resotext = "X: " + str(imgcoord[0]) + " Y: " + str(imgcoord[1]) + "\n2Θ: " + str("%.1f" % round(math.degrees(twothetaangle), 1)) + "°\ndmin: " + str("%.2f" % round(reso, 2)) + " Å"
                    dotsize = int((toprightx / graphbbox[2])* 4)
                    anchor_y = "n"
                    anchor_x = "w"
                    if imgcoord[0] > (0.5*toprightx):
                        anchor_x = "e"
                    if imgcoord[1] > (0.5*bottomlefty):
                        anchor_y = "s"
                    textbox_anchor = anchor_y + anchor_x    
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='green3')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    coordresonumber = window_imageview['-IMGAREA-'].DrawText(resotext,(imgcoord[0],imgcoord[1]), font=('Arial 10 bold'), color='green3')
                    coordresonumber_shadow = window_imageview['-IMGAREA-'].DrawText(resotext,(imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), font=('Arial 10 bold'), color='black') 
                    window_imageview['-IMGAREA-'].TKCanvas.itemconfig(coordresonumber, anchor = textbox_anchor)
                    window_imageview['-IMGAREA-'].TKCanvas.itemconfig(coordresonumber_shadow, anchor = textbox_anchor) 
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordresonumber)
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    coorddisplayshadows.append(coordmarker_shadow)
                    coorddisplay.append(coordmarker)
                    coorddisplaytext.append(coordresonumber)
                    coorddisplaytextshadows.append(coordresonumber_shadow)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    time.sleep(0.2)

            # deletes coordinate display after timeout
            if event_imageview == '-COORDTIMESUP-':
                if len(coorddisplay) > 0:
                    window_imageview['-IMGAREA-'].DeleteFigure(coorddisplay[0])
                    coorddisplay.pop(0) 
                    window_imageview['-IMGAREA-'].DeleteFigure(coorddisplayshadows[0])
                    coorddisplayshadows.pop(0)
                    window_imageview['-IMGAREA-'].DeleteFigure(coorddisplaytext[0])
                    coorddisplaytext.pop(0)
                    window_imageview['-IMGAREA-'].DeleteFigure(coorddisplaytextshadows[0])
                    coorddisplaytextshadows.pop(0)   
                if mycircle != None:
                    window_imageview['-IMGAREA-'].DeleteFigure(mycircle)
                    mycircle = None
                if len(pointdisplay) > 0:
                    window_imageview['-IMGAREA-'].DeleteFigure(pointdisplay[0])
                    pointdisplay.pop(0)
                    window_imageview['-IMGAREA-'].DeleteFigure(pointdisplayshadows[0])
                    pointdisplayshadows.pop(0)     
                    
            # draw resolution rings
            if (event_imageview == '-SHOWRINGS-' and values_imageview['-SHOWRINGS-'] == True) or (event_imageview == '-NUMRINGS-' and values_imageview['-SHOWRINGS-'] == True) :
                for resoringplot in resoringplots:
                    window_imageview['-IMGAREA-'].DeleteFigure(resoringplot)
                for resonumber in resoringnumbers:
                    window_imageview['-IMGAREA-'].DeleteFigure(resonumber)     
                resorings = int(values_imageview['-NUMRINGS-'])
                resospacing = int(0.5 * float(graph_ypixels)/(resorings))
                resoringplots = []
                resoringnumbers = []
                resoradius = resospacing
                if (modified_beamcenter != []) and (modified_beamcenter != '') :
                    ringcentre = (modified_beamcenter[0], modified_beamcenter[1])
                else:
                    ringcentre = (old_beamcenter[0], old_beamcenter[1])
                if headertwotheta != 0:
                    ringcentre = (ringcentre[0] - xoffset, ringcentre[1])
                    while (2*resoradius)  <= int(graph_ypixels):
                        twothetaangle = math.atan((float(resoradius)*float(graph_ysize))/float(graph_dist))
                        reso = (float(graph_wl)/(math.sin(0.5*twothetaangle)))*0.5
                        resotext = str("%.2f" % round(reso, 2)) + " Å"
                        positive_angle = twothetaangle + math.radians(float(headertwotheta))
                        negative_angle = twothetaangle - math.radians(float(headertwotheta))
                        positive_a = ((float(graph_dist) * (math.tan(positive_angle)))/(float(graph_xsize))) - xoffset
                        negative_a = ((float(graph_dist) * (math.tan(negative_angle)))/(float(graph_xsize))) + xoffset
                        ellipsis_xy1 = [ringcentre[0] - positive_a, ringcentre[1] - resoradius]
                        ellipsis_xy2 = [ringcentre[0] + negative_a, ringcentre[1] + resoradius]
                        resocoords = [int(ringcentre[0]),int(ringcentre[1] - (resoradius - (float(graph_ypixels)/50)))]
                        resoringplot = window_imageview['-IMGAREA-'].DrawOval((ellipsis_xy1[0],ellipsis_xy1[1]), (ellipsis_xy2[0], ellipsis_xy2[1]), fill_color=None, line_color='blue')
                        window_imageview['-IMGAREA-'].TKCanvas.itemconfig(resoringplot, dash = "2 2")
                        resonumber = window_imageview['-IMGAREA-'].DrawText(resotext,(resocoords[0],resocoords[1]), color='blue')
                        resoringplots.append(resoringplot)
                        resoringnumbers.append(resonumber)
                        resoradius = resoradius + resospacing
                else:     
                    while (2*resoradius)  <= int(graph_ypixels):
                        twothetaangle = math.atan((float(resoradius)*float(graph_ysize))/float(graph_dist))
                        reso = (float(graph_wl)/(math.sin(0.5*twothetaangle)))*0.5
                        resotext = str("%.2f" % round(reso, 2)) + " Å"
                        resocoords = [int(ringcentre[0]),int(ringcentre[1] - (resoradius - (float(graph_ypixels)/50)))]
                        resoringplot = window_imageview['-IMGAREA-'].DrawCircle((ringcentre[0],ringcentre[1]), resoradius, fill_color=None,line_color='blue')
                        window_imageview['-IMGAREA-'].TKCanvas.itemconfig(resoringplot, dash = "2 4") 
                        resonumber = window_imageview['-IMGAREA-'].DrawText(resotext,(resocoords[0],resocoords[1]), color='blue')
                        resoringplots.append(resoringplot)
                        resoringnumbers.append(resonumber)
                        resoradius = resoradius + resospacing    
            if event_imageview == '-SHOWRINGS-' and values_imageview['-SHOWRINGS-'] == False:
                for resoringplot in resoringplots:
                    window_imageview['-IMGAREA-'].DeleteFigure(resoringplot)
                for resonumber in resoringnumbers:
                    window_imageview['-IMGAREA-'].DeleteFigure(resonumber)     

             # draw ice rings
            if (event_imageview == '-ICERINGS-' and values_imageview['-ICERINGS-'] == True):
                for iceringplot in iceringplots:
                    window_imageview['-IMGAREA-'].DeleteFigure(iceringplot)    
                iceringplots = []
                if (modified_beamcenter != []) and (modified_beamcenter != '') :
                    ringcentre = (modified_beamcenter[0], modified_beamcenter[1])
                else:
                    ringcentre = (old_beamcenter[0], old_beamcenter[1])
                if headertwotheta != 0:
                    ringcentre = (ringcentre[0] - xoffset, ringcentre[1])
                    for iceringrange in iceringranges:
                        twothetaangle = 2*(math.asin((float(graph_wl)/(2*float(iceringrange)))))
                        iceresoradius = (float(graph_dist)*math.tan(twothetaangle))/float(graph_ysize)
                        positive_angle = twothetaangle + math.radians(float(headertwotheta))
                        negative_angle = twothetaangle - math.radians(float(headertwotheta))
                        positive_a = ((float(graph_dist) * (math.tan(positive_angle)))/(float(graph_xsize))) - xoffset
                        negative_a = ((float(graph_dist) * (math.tan(negative_angle)))/(float(graph_xsize))) + xoffset
                        ellipsis_xy1 = [ringcentre[0] - positive_a, ringcentre[1] - iceresoradius]
                        ellipsis_xy2 = [ringcentre[0] + negative_a, ringcentre[1] + iceresoradius]
                        iceringplot = window_imageview['-IMGAREA-'].DrawOval((ellipsis_xy1[0],ellipsis_xy1[1]), (ellipsis_xy2[0], ellipsis_xy2[1]), fill_color=None, line_color='cyan')
                        window_imageview['-IMGAREA-'].TKCanvas.itemconfig(iceringplot, dash = "2 2")
                        iceringplots.append(iceringplot)
                else:     
                    for iceringrange in iceringranges: 
                        twothetaangle = 2*(math.asin((float(graph_wl)/(2*float(iceringrange)))))
                        iceresoradius = (float(graph_dist)*math.tan(twothetaangle))/float(graph_ysize)
                        iceringplot = window_imageview['-IMGAREA-'].DrawCircle((ringcentre[0],ringcentre[1]), iceresoradius, fill_color=None,line_color='cyan')
                        window_imageview['-IMGAREA-'].TKCanvas.itemconfig(iceringplot, dash = "2 4") 
                        iceringplots.append(iceringplot)   
            if event_imageview == '-ICERINGS-' and values_imageview['-ICERINGS-'] == False:
                for iceringplot in iceringplots:
                    window_imageview['-IMGAREA-'].DeleteFigure(iceringplot)

            # Fit beamcentre by clicking          
            if values_imageview['-FITWHAT-'] == "Click to set beamcentre":
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                rectanglecoord1set = False
                qcoordset = 0
                if event_imageview == '-IMGAREA-+UP':    
                    imgcoord = values_imageview['-IMGAREA-']
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    crosshairoffsetx = (imgcoord[0] - x_imgval)
                    crosshairoffsety = (imgcoord[1] - y_imgval)
                    window_imageview['-IMGAREA-'].MoveFigure(imagebeamcentrex, crosshairoffsetx, crosshairoffsety)
                    window_imageview['-IMGAREA-'].MoveFigure(imagebeamcentrey, crosshairoffsetx, crosshairoffsety)
                    x_imgval = imgcoord[0]
                    y_imgval = imgcoord[1]
                    modified_beamcenter = [round(x_imgval + xoffset), round(y_imgval)]

            # Fit beamcentre from 3-click circle       
            if values_imageview['-FITWHAT-'] == "Fit beamcentre from circle (3 clicks)":
                rectanglecoord1set = False
                circle2coord1set = False
                circle2coord2set = False
                qcoordset = 0
                shadowpixeloffset = 1
                shadowxcoords = int((toprightx / graphbbox[2])*shadowpixeloffset)
                shadowycoords = int((bottomlefty / graphbbox[3])*shadowpixeloffset) 
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    dotsize = int((toprightx / graphbbox[2])* 4)  
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='orange')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    pointdisplayshadows.append(coordmarker_shadow)
                    pointdisplay.append(coordmarker)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    if circlecoord1set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        circle_x1 = imgcoord[0]
                        circle_y1 = imgcoord[1]
                        circlecoord1set = True
                        #print(circlecoord1set)
                        #print(imgcoord)
                    elif circlecoord1set == True and circlecoord2set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if imgcoord[0] != circle_x1 or imgcoord[1] != circle_y1:
                            circle_x2 = imgcoord[0]
                            circle_y2 = imgcoord[1]
                            circlecoord2set = True
                        #print(circlecoord1set)
                        #print(imgcoord)        
                    elif circlecoord1set == True and circlecoord2set == True:
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if (imgcoord[0] != circle_x1 and imgcoord[0] != circle_x2) or (imgcoord[1] != circle_y1 and imgcoord[1] != circle_y2):
                            circle_x3 = imgcoord[0]
                            circle_y3 = imgcoord[1]
                            circlediv = 2*(circle_x1 * (circle_y2 - circle_y3) + circle_x2 * (circle_y3 - circle_y1) + circle_x3 * (circle_y1 - circle_y2))
                            circlexcenter = (1/circlediv)*((pow(circle_x1,2) + pow(circle_y1,2))*(circle_y2 - circle_y3) + (pow(circle_x2,2) + pow(circle_y2,2))*(circle_y3 - circle_y1)  + (pow(circle_x3,2) + pow(circle_y3,2))*(circle_y1 - circle_y2))
                            circleycenter = (1/circlediv)*((pow(circle_x1,2) + pow(circle_y1,2))*(circle_x3 - circle_x2) + (pow(circle_x2,2) + pow(circle_y2,2))*(circle_x1 - circle_x3)  + (pow(circle_x3,2) + pow(circle_y3,2))*(circle_x2 - circle_x1))
                            circlea = math.sqrt(pow((circle_x1 - circle_x2),2) + pow((circle_y1 - circle_y2),2))
                            circleb = math.sqrt(pow((circle_x1 - circle_x3),2) + pow((circle_y1 - circle_y3),2))
                            circlec = math.sqrt(pow((circle_x2 - circle_x3),2) + pow((circle_y2 - circle_y3),2))
                            circleradius = circlea * circleb * circlec /(math.sqrt((circlea + circleb + circlec)*(circleb + circlec - circlea)*(circlec + circlea - circleb)*(circlea + circleb - circlec)))
                            mycircle = window_imageview['-IMGAREA-'].draw_circle(center_location = (circlexcenter, circleycenter), radius = circleradius, fill_color = None, line_color = 'blue', line_width = 2)
                            print ("Beamcentre: ", round(circlexcenter), round(circleycenter), "px")
                            coordel_timeout = 1
                            coordel_timer(coordel_timeout)
                            #print(round(circleradius))
                            crosshairoffsetx = (circlexcenter - x_imgval)
                            crosshairoffsety = (circleycenter - y_imgval)
                            window_imageview['-IMGAREA-'].MoveFigure(imagebeamcentrex, crosshairoffsetx, crosshairoffsety)
                            window_imageview['-IMGAREA-'].MoveFigure(imagebeamcentrey, crosshairoffsetx, crosshairoffsety)
                            #time.sleep(1)
                            x_imgval = circlexcenter
                            y_imgval = circleycenter
                            modified_beamcenter = [round(x_imgval + xoffset), round(y_imgval)]               
                            circlecoord1set = False
                            circlecoord2set = False
                    #print(imgcoord)

            # Rectangular mask (=untrusted_rectangle for XDS)              
            if values_imageview['-FITWHAT-'] == "Rectangular mask (2 clicks)":
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                qcoordset = 0
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    dotsize = int((toprightx / graphbbox[2])* 4)  
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='orange')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    pointdisplayshadows.append(coordmarker_shadow)
                    pointdisplay.append(coordmarker)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    if rectanglecoord1set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        rect_x1 = imgcoord[0]
                        rect_y1 = imgcoord[1]
                        rectanglecoord1set = True
                        #print(rectanglecoord1set)
                        #print(imgcoord)
                    elif rectanglecoord1set == True: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        #print(imgcoord)
                        if rect_x1 != imgcoord[0] or rect_y1 != imgcoord[1]:
                            rect_x2 = imgcoord[0]
                            rect_y2 = imgcoord[1]
                            untrusted_rectangle = window_imageview['-IMGAREA-'].DrawRectangle((rect_x1,rect_y1), (rect_x2,rect_y2), fill_color = None, line_color = 'red', line_width = 3)
                            rectanglecoord1set = False
                            untrusted_rectangles.append(untrusted_rectangle)
                            xds_coords = [rect_x1, rect_x2, rect_y1, rect_y2]
                            untrusted_rectangle_coords.append(xds_coords)
                        
            # Oval mask (=untrusted_ellipse for XDS)              
            if values_imageview['-FITWHAT-'] == "Oval mask (2 clicks)":
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                qcoordset = 0
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    dotsize = int((toprightx / graphbbox[2])* 4)  
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='orange')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    pointdisplayshadows.append(coordmarker_shadow)
                    pointdisplay.append(coordmarker)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    if rectanglecoord1set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        rect_x1 = imgcoord[0]
                        rect_y1 = imgcoord[1]
                        rectanglecoord1set = True
                        #print(rectanglecoord1set)
                        #print(imgcoord)
                    elif rectanglecoord1set == True: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        #print(imgcoord)
                        if rect_x1 != imgcoord[0] or rect_y1 != imgcoord[1]:
                            rect_x2 = imgcoord[0]
                            rect_y2 = imgcoord[1]
                            untrusted_ellipse = window_imageview['-IMGAREA-'].draw_oval((rect_x1,rect_y1), (rect_x2,rect_y2), fill_color = None, line_color = 'red', line_width = 3)
                            rectanglecoord1set = False
                            untrusted_ellipses.append(untrusted_ellipse)
                            xds_coords = [rect_x1, rect_x2, rect_y1, rect_y2]
                            untrusted_ellipse_coords.append(xds_coords)
                        
            # Circular mask (=untrusted_ellipse for XDS)            
            if values_imageview['-FITWHAT-'] == "Circular mask (3 clicks)":
                rectanglecoord1set = False
                circlecoord1set = False
                circlecoord2set = False
                qcoordset = 0
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    dotsize = int((toprightx / graphbbox[2])* 4)  
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='orange')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    pointdisplayshadows.append(coordmarker_shadow)
                    pointdisplay.append(coordmarker)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    if circle2coord1set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        circle_x1 = imgcoord[0]
                        circle_y1 = imgcoord[1]
                        circle2coord1set = True
                        #print(imgcoord)
                    elif circle2coord1set == True and circle2coord2set == False: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if imgcoord[0] != circle_x1 or imgcoord[1] != circle_y1:
                            circle_x2 = imgcoord[0]
                            circle_y2 = imgcoord[1]
                            circle2coord2set = True
                        #print(imgcoord)        
                    elif circle2coord1set == True and circle2coord2set == True:
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if (imgcoord[0] != circle_x1 and imgcoord[0] != circle_x2) or (imgcoord[1] != circle_y1 and imgcoord[1] != circle_y2):
                            circle_x3 = imgcoord[0]
                            circle_y3 = imgcoord[1]
                            circlediv = 2*(circle_x1 * (circle_y2 - circle_y3) + circle_x2 * (circle_y3 - circle_y1) + circle_x3 * (circle_y1 - circle_y2))
                            circlexcenter = (1/circlediv)*((pow(circle_x1,2) + pow(circle_y1,2))*(circle_y2 - circle_y3) + (pow(circle_x2,2) + pow(circle_y2,2))*(circle_y3 - circle_y1)  + (pow(circle_x3,2) + pow(circle_y3,2))*(circle_y1 - circle_y2))
                            circleycenter = (1/circlediv)*((pow(circle_x1,2) + pow(circle_y1,2))*(circle_x3 - circle_x2) + (pow(circle_x2,2) + pow(circle_y2,2))*(circle_x1 - circle_x3)  + (pow(circle_x3,2) + pow(circle_y3,2))*(circle_x2 - circle_x1))
                            circlea = math.sqrt(pow((circle_x1 - circle_x2),2) + pow((circle_y1 - circle_y2),2))
                            circleb = math.sqrt(pow((circle_x1 - circle_x3),2) + pow((circle_y1 - circle_y3),2))
                            circlec = math.sqrt(pow((circle_x2 - circle_x3),2) + pow((circle_y2 - circle_y3),2))
                            circleradius = circlea * circleb * circlec /(math.sqrt((circlea + circleb + circlec)*(circleb + circlec - circlea)*(circlec + circlea - circleb)*(circlea + circleb - circlec)))
                            rect_x1 = round(circlexcenter - circleradius)
                            rect_y1 = round(circleycenter - circleradius)
                            rect_x2 = round(circlexcenter + circleradius)
                            rect_y2 = round(circleycenter + circleradius)
                            untrusted_ellipse = window_imageview['-IMGAREA-'].draw_oval((rect_x1, rect_y1), (rect_x2, rect_y2), fill_color = None, line_color = 'red', line_width = 3)
                            untrusted_ellipses.append(untrusted_ellipse)
                            xds_coords = [rect_x1, rect_x2, rect_y1, rect_y2]
                            untrusted_ellipse_coords.append(xds_coords)              
                            circle2coord1set = False
                            circle2coord2set = False
                        #print(imgcoord)
                        
            # Define untrusted_quadrialateral for XDS            
            if values_imageview['-FITWHAT-'] == "Quadrilateral mask (4 clicks)":
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                if event_imageview == '-IMGAREA-+UP':
                    imgcoord = values_imageview['-IMGAREA-']
                    #print(imgcoord)
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    dotsize = int((toprightx / graphbbox[2])* 4)  
                    coordmarker = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0],imgcoord[1]), dotsize, color='orange')
                    coordmarker_shadow = window_imageview['-IMGAREA-'].DrawPoint((imgcoord[0] + shadowxcoords,imgcoord[1] + shadowycoords), dotsize, color='black')
                    window_imageview['-IMGAREA-'].bring_figure_to_front(coordmarker) 
                    pointdisplayshadows.append(coordmarker_shadow)
                    pointdisplay.append(coordmarker)
                    coordel_timeout = 5
                    coordel_timer(coordel_timeout)
                    if qcoordset == 0: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        q_x1 = imgcoord[0]
                        q_y1 = imgcoord[1]
                        qcoordset = 1
                        #print(qcoordset)
                        #print(imgcoord)
                    elif qcoordset == 1: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if q_x1 != imgcoord[0] or q_y1 != imgcoord[1]:
                            q_x2 = imgcoord[0]
                            q_y2 = imgcoord[1]
                            qcoordset = 2
                            #print(qcoordset)
                            #print(imgcoord)
                    elif qcoordset == 2: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if q_x2 != imgcoord[0] or q_y2 != imgcoord[1]:
                            q_x3 = imgcoord[0]
                            q_y3 = imgcoord[1]
                            qcoordset = 3
                            #print(qcoordset)
                            #print(imgcoord)
                    elif qcoordset == 3: 
                        imgcoord = values_imageview['-IMGAREA-']
                        window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                        window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                        if q_x3 != imgcoord[0] or q_y3 != imgcoord[1]:
                            q_x4 = imgcoord[0]
                            q_y4 = imgcoord[1]
                            qcoordset = 4
                            #print(qcoordset)
                            #print(imgcoord)
                            def coordsort(n):
                                return abs(math.fsum(n))
                            xds_coords = [(q_x1, q_y1), (q_x2, q_y2), (q_x3, q_y3), (q_x4, q_y4)]
                            xds_coords.sort(key = coordsort)
                            untrusted_quad_coords.append(xds_coords)
                            quad_line_1 = window_imageview['-IMGAREA-'].draw_line(xds_coords[0], xds_coords[1], color = 'red', width = 3)
                            quad_line_2 = window_imageview['-IMGAREA-'].draw_line(xds_coords[1], xds_coords[3], color = 'red', width = 3)
                            quad_line_3 = window_imageview['-IMGAREA-'].draw_line(xds_coords[3], xds_coords[2], color = 'red', width = 3)
                            quad_line_4 = window_imageview['-IMGAREA-'].draw_line(xds_coords[2], xds_coords[0], color = 'red', width = 3)
                            untrusted_quad = [quad_line_1, quad_line_2, quad_line_3, quad_line_4]
                            untrusted_quads.append(untrusted_quad)
                            qcoordset = 0
                        
            # Delete masked areas        
            if values_imageview['-FITWHAT-'] == "Click on masks to delete":
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                rectanglecoord1set = False
                qcoordset = 0
                if event_imageview == '-IMGAREA-+UP': 
                    imgcoord = values_imageview['-IMGAREA-']
                    window_imageview['-XIMGVAL-'].update(value = imgcoord[0])
                    window_imageview['-YIMGVAL-'].update(value = imgcoord[1])
                    untrusted_clicked = window_imageview['-IMGAREA-'].get_figures_at_location(imgcoord)
                    for untrusted in untrusted_clicked:
                        if untrusted in untrusted_ellipses:
                            untrusted_index = untrusted_ellipses.index(untrusted)
                            untrusted_ellipses.pop(untrusted_index)
                            untrusted_ellipse_coords.pop(untrusted_index)
                            window_imageview['-IMGAREA-'].delete_figure(untrusted)
                        if untrusted in untrusted_rectangles:
                            untrusted_index = untrusted_rectangles.index(untrusted)
                            untrusted_rectangles.pop(untrusted_index)
                            untrusted_rectangle_coords.pop(untrusted_index)
                            window_imageview['-IMGAREA-'].delete_figure(untrusted)
                        for untrusted_quad in untrusted_quads:
                            if untrusted in untrusted_quad:
                                untrusted_index = untrusted_quads.index(untrusted_quad)
                                untrusted_quads.pop(untrusted_index)
                                untrusted_quad_coords.pop(untrusted_index)
                                for line in untrusted_quad:
                                    window_imageview['-IMGAREA-'].delete_figure(line)
                                    
            # Define Gaps for Pilatus/Eiger Detectors (group of untrusted_rectangles for XDS) 
            if event_imageview == '-FITMODE-' and values_imageview['-FITMODE-'] == "Define HPAD gaps":
                dectris_gap_coords = []
                dectris_gaps = []
                window_imageview['-FITWHAT-'].update(value = "n/a", values = listvals_none)  
                circlecoord1set = False
                circlecoord2set = False
                circle2coord1set = False
                circle2coord2set = False
                rectanglecoord1set = False
                qcoordset = 0
                numofgaps = []
                sizeofgaps = []
                gscale = []
                goffset = []
                for x in range (26):
                    numofgaps.append(x)
                for x in range (61):
                    sizeofgaps.append(x)
                for x in range (-100, 101):
                    x = x * 0.1
                    #x = ("%.1f" % x)
                    x = "{:+.1f}".format(x)
                    gscale.append(x)
                #gscale.append("{:+.1f}".format(10))
                for x in range (-50, 51):
                    x = x * 0.1
                    #x = ("%.1f" % x)
                    x = "{:+.1f}".format(x)
                    goffset.append(x) 
                layout_gaps = [[sg.Frame(layout=[
                [sg.Text('Usually, this should not be necessary!', text_color = 'red', justification = "center")],    
                [sg.Text('', size = (12, 1)), sg.Text('X', size = (8, 1)), sg.Text('Y', size = (8, 1))],
                [sg.Text('No. of gaps:', size = (12, 1)), 
                 sg.Spin(values = numofgaps, initial_value= "0",key='-XGAPS-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Number of module gaps in X direction"),
                 sg.Spin(values = numofgaps, initial_value= "0",key='-YGAPS-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Number of module gaps in Y direction")],
                [sg.Text('Scale:', size = (12, 1)), 
                 sg.Spin(values = gscale, initial_value= "+0.0",key='-XGAPSCALE-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Enlarge (+) or decrease (-) distances between gaps in X"),
                 sg.Spin(values = gscale, initial_value= "+0.0",key='-YGAPSCALE-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Enlarge (+) or decrease (-) distances between gaps in Y"),sg.Text("%")],
                 [sg.Text('Offset:', size = (12, 1)), 
                  sg.Spin(values = goffset, initial_value= "+0.0",key='-XGAPOFFSET-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Shift gap positions along in X"),
                  sg.Spin(values = goffset, initial_value= "+0.0",key='-YGAPOFFSET-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Shift gap positions along in X"),sg.Text("%")],
                 [sg.Text('Width:', size = (12, 1)), 
                  sg.Spin(values = sizeofgaps, initial_value= "0",key='-XGAPSIZE-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Width of X gaps"),
                  sg.Spin(values = sizeofgaps, initial_value= "0",key='-YGAPSIZE-',size=(6,1), text_color = 'black', enable_events = True, readonly = True, tooltip = "Width of Y gaps"),sg.Text("px")],
                [sg.Text('')],  
                [sg.Button('Accept', highlight_colors = (theme_color, theme_color)), sg.Button('Cancel', highlight_colors = (theme_color, theme_color))]],title= None, title_color=theme_color, relief= None, element_justification = "left", pad = (0,0), vertical_alignment='center')]]                        

                window_gaps = sg.Window('Define gap mask', layout_gaps, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))

                while True:
                    event_gaps, values_gaps = window_gaps.read(timeout=100)

                    # cancel gap definition
                    if event_gaps == sg.WIN_CLOSED or event_gaps== 'Cancel':
                        window_gaps.close()
                        layout_gaps = None
                        window_gaps = None
                        gc.collect()
                        for gap in dectris_gaps:
                            window_imageview['-IMGAREA-'].delete_figure(gap) 
                        dectris_gap_coords = []
                        dectris_gaps = []
                        break

                    # accept gap definitions
                    if event_gaps == 'Accept':
                        window_gaps.close()
                        layout_gaps = None
                        window_gaps = None
                        gc.collect()
                        break

                    # set up gap definitions
                    if event_gaps != 'Cancel' and event_gaps != 'Accept':
                        for gap in dectris_gaps:
                            window_imageview['-IMGAREA-'].delete_figure(gap) 
                        dectris_gap_coords = []
                        dectris_gaps = []
                        xgaps = int(values_gaps['-XGAPS-'])
                        x_scale = float((float(values_gaps['-XGAPSCALE-'])/100) + 1)
                        if xgaps > 0:
                            xgapfrac = toprightx / (xgaps + 1)
                            xgappos = xgapfrac
                            xgappos_corr = (((xgapfrac/ toprightx) * (x_scale * toprightx)) - (0.5 * (x_scale -1) * toprightx)) + ((float(values_gaps['-XGAPOFFSET-'])/100)*toprightx)
                            xgapcoordoffset = 0.5 * int(values_gaps['-XGAPSIZE-'])
                            i = 0
                            while i < xgaps:
                                xgapcoord1 = (int(xgappos_corr - xgapcoordoffset), 0)
                                xgapcoord2 = (int(xgappos_corr + xgapcoordoffset), bottomlefty)
                                xgappos = xgappos + xgapfrac
                                xgappos_corr = (((xgappos / toprightx) * (x_scale * toprightx)) - (0.5 * (x_scale - 1) * toprightx))+ ((float(values_gaps['-XGAPOFFSET-'])/100)*toprightx)
                                xgap = window_imageview['-IMGAREA-'].DrawRectangle((xgapcoord1), (xgapcoord2), fill_color = 'yellow', line_color = None, line_width = 0)
                                dectris_gaps.append(xgap)
                                gap_coords = [xgapcoord1[0], xgapcoord2[0], xgapcoord1[1], xgapcoord2[1]]
                                dectris_gap_coords.append(gap_coords)
                                i+=1
                        ygaps = int(values_gaps['-YGAPS-'])
                        y_scale = float((float(values_gaps['-YGAPSCALE-'])/100) + 1)
                        if ygaps > 0:
                            ygapfrac = (bottomlefty / (ygaps + 1))
                            ygappos = ygapfrac
                            ygappos_corr = (((ygapfrac/ bottomlefty) * (y_scale * bottomlefty)) - (0.5 * (y_scale-1) * bottomlefty)) + ((float(values_gaps['-YGAPOFFSET-'])/100)*bottomlefty)
                            ygapcoordoffset = 0.5 * int(values_gaps['-YGAPSIZE-'])
                            i = 0
                            while i < ygaps:
                                ygapcoord1 = (0,int(ygappos_corr - ygapcoordoffset))
                                ygapcoord2 = (toprightx, int(ygappos_corr + ygapcoordoffset))
                                ygappos = (ygappos + ygapfrac)
                                ygappos_corr = (((ygappos/ bottomlefty) * (y_scale * bottomlefty)) - (0.5 * (y_scale-1) * bottomlefty)) + ((float(values_gaps['-YGAPOFFSET-'])/100)*bottomlefty)
                                ygap = window_imageview['-IMGAREA-'].DrawRectangle((ygapcoord1), (ygapcoord2), fill_color = 'yellow', line_color = None, line_width = 0)
                                dectris_gaps.append(ygap)
                                gap_coords = [ygapcoord1[0], ygapcoord2[0], ygapcoord1[1], ygapcoord2[1]]
                                dectris_gap_coords.append(gap_coords)
                                i+=1
                        for figure in (untrusted_rectangles or untrusted_ellipses or untrusted_quads):
                            window_imageview['-IMGAREA-'].bring_figure_to_front(figure)
                        window_imageview['-IMGAREA-'].bring_figure_to_front(imagebeamcentrex)
                        window_imageview['-IMGAREA-'].bring_figure_to_front(imagebeamcentrey) 

### END OF GRAPHING SECTION


    # sweep definition
    if event == '-SWEEPRANGE-':
        if EIGER == True:
            h5 = values['-HDF5-']
            imgpath = "/".join(h5.split("/")[:-1])
        else:    
            imgpath = values['-IMGS-']

        if os.path.exists(imgpath) == False:
            print('')
            print('Image folder does not exist.')
        else:    
            
            #retrieve sweeps by parsing hits from find_file in helper function    
            if oldcntr == 0:
                sweeps = []
                hits = []
                hits = find_sweeps(imgpath, EIGER)
                hitno = 0
                cntr = 0
                for hit in hits:
                    hitno += 1
                    hit = " ".join(hit.split(":"))
                    hit = " ".join(hit.split(" - "))
                    hit = " ".join(hit.split())
                    hit = str(hitno) + " " + hit
                    sweep = hit.split(" ")
                    sweeps.append(sweep)
                    #print(hit)
                
            # split sweeps into parameter lists          
            # only continue if there are datasets found at all
            if len(sweeps[0]) < 5:
                print('')
                print("No images found!")
            else:
                print('')
                print("Found", len(sweeps),"sweeps")
                sweeptitle="Found "+ str(len(sweeps)) +" sweeps"
                print("")
                if oldcntr == 0:
                    IDs = []
                    PATHs = []
                    TEMPLATEs = []
                    STARTs = []
                    ENDs = []
                    for sweep in sweeps:
                        print("Id:", sweep[0])
                        IDs.append(sweep[0])
                        print("Path:", sweep[1])
                        PATHs.append(sweep[1])
                        print("Template:", sweep[2])
                        TEMPLATEs.append(sweep[2])
                        print("Start:", sweep[3])
                        STARTs.append(sweep[3])
                        print("End:", sweep[4])
                        ENDs.append(sweep[4])
                        print("")
                Id = IDs[0]
                Template = TEMPLATEs[0]
                Start = STARTs[0]
                End = ENDs[0]
                if oldcntr == 0:
                    setsweeps = ''
                    
                # definiton of sweep selection window    
                layout_sweeps = [[sg.Col([[sg.Text('Select Sweep:')], [sg.Combo((IDs),
                          key = '-SWEEPSEL-', enable_events = True, size = (10,1), readonly = True, default_value = "1")]], size = (100,70)),
                          sg.Col([[sg.Text('Template:')], [sg.InputText(Template, size=(40,1), key = '-TEMPLATE-', disabled = False)]], size = (300,70)),
                          sg.Col([[sg.Text('Start:')], [sg.InputText(Start, size=(6,1), key = '-START-', disabled = False)]], size = (60,70)),
                          sg.Col([[sg.Text('End:')], [sg.InputText(End, size=(6,1), key = '-END-', disabled = False)]], size = (343,70)),
                          sg.Col([[sg.Text('')],[sg.Button("+", size = (1,1), tooltip = "Add image range"), sg.Button("-", size = (1,1), tooltip = " Remove last image range"), sg.Button("Clear", tooltip = "Clear list of image ranges")]], size = (155,70))], 
                         [sg.Multiline(size=(140,10), key='-SWEEPS-', autoscroll = True, do_not_clear = True, font="Courier 9", default_text = setsweeps)],
                         [sg.Submit(), sg.Cancel()]]

                window_sweeps = sg.Window(sweeptitle, layout_sweeps, no_titlebar=False, grab_anywhere=False, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))        

                while True:
                    event_sw, values_sw = window_sweeps.read()
                    if event_sw == '-SWEEPSEL-':
                        listindex = int(''.join(values_sw['-SWEEPSEL-'])) - 1
                        #print(listindex)
                        Template = TEMPLATEs[listindex]
                        Start = STARTs[listindex]
                        End = ENDs[listindex]
                        window_sweeps['-TEMPLATE-'].update(value = Template)
                        window_sweeps['-START-'].update(value = Start)
                        window_sweeps['-END-'].update(value = End)
                        
                    # add sweep definition to list
                    if event_sw == '+':
                        cntr = cntr +1
                        if int(values_sw ['-START-']) < int(Start):
                            setstart = Start
                        elif int(values_sw ['-START-']) > int(End):
                            setstart = End
                        else:
                            setstart = values_sw ['-START-']
                        if int(values_sw ['-END-']) < int(Start):
                            setend = Start
                        elif int(values_sw ['-END-']) > int(End):
                            setend = End
                        else:
                            setend = values_sw ['-END-']    
                        window_sweeps['-SWEEPS-'].print('#', cntr, PATHs[listindex], values_sw['-TEMPLATE-'], str(int(setstart)), str(int(setend)))

                    # clear sweep definition list    
                    if event_sw == 'Clear':
                        window_sweeps['-SWEEPS-'].update(value = '')
                        cntr = 0

                    # remove last sweep from list    
                    if event_sw == '-':
                        try:
                            window_sweeps['-SWEEPS-'].update(value = '')
                            tempsweeps = (values_sw['-SWEEPS-']).splitlines()
                            if(len(tempsweeps)) > 1:
                                tempsweeps.pop()
                                tempsweeps.pop()     
                            for line in tempsweeps:
                                window_sweeps['-SWEEPS-'].print(line)
                            if cntr > 0:
                                cntr = cntr - 1
                        except:
                            print('Not possible!')
                            print('') 

                    # set sweep definitions        
                    if event_sw == 'Submit':
                        tempsweeps = (values_sw['-SWEEPS-']).splitlines()
                        tempsweeps.pop()
                        setsweeps = "\n".join(tempsweeps) + '\n'
                        sweepcommands = ",".join(values_sw['-SWEEPS-'].split())
                        sweepcommands = " -Id sweep_".join(sweepcommands.split(",#,"))
                        sweepcommands = "-Id sweep_".join(sweepcommands.split("#,"))
                        #print(sweepcommands)
                        oldcntr = cntr
                        window_sweeps.close()
                        layout_sweeps = None
                        window_sweeps = None
                        gc.collect()
                        break

                    # close sweep definition window    
                    if event_sw == sg.WIN_CLOSED or event_sw == 'Cancel':
                        window_sweeps.close()
                        layout_sweeps = None
                        window_sweeps = None
                        gc.collect()                        
                        break
                    
    # Open help for extra parameters                
    if event == '-WEB-':
        silent = True
        utility_command = browser + " http://www.globalphasing.com/autoproc/manual/autoPROC4.html#intro"
        utility_function(utility_command, silent)
        time.sleep(1)
        utility_command = browser + " http://www.globalphasing.com/autoproc/manual/appendix1.html"
        utility_function(utility_command, silent)
                
    # Advanced (Macro) Section now in new Window
    if (event == '-CUSTPAR-' and values['-CUSTPAR-'] == True) or (event == '-EDPAR-'):
        disable_macro = not disable_macro
        window['-ENABLEMACRO-'].update(value = False, disabled = True)
        window['-MACRO-'].update(disabled=True)
        window['-LISTMACROS-'].update(disabled=True)
        window['-MACROWARNING-'].update(text_color = 'red')
        
        layout3 = [[sg.Frame(layout=[
                    [sg.Text('Specify input parameters as macro', font = 'Arial 12')],
                    [sg.Text('See also http://www.globalphasing.com/autoproc/manual/appendix1.html', text_color = "blue", font = "Courier 10 underline", key='-WEB-', enable_events=True, tooltip='Click here to open browser.')],
                    [sg.Multiline(size=(130,30), key='-PARDAT-', autoscroll = True, do_not_clear = False, font="Courier 9", default_text = custpars)],
                    [sg.Button('Load default template', enable_events=True, key='-DEFTEMP-'), sg.Input(key='-PARFILE-', visible=False, enable_events=True), sg.FileBrowse('Load from file', file_types = (('Parameter file', '*.*'),)),
                     sg.Input(key='-XDSINP-', visible=False, enable_events=True), sg.FileBrowse('Parameters from XDS.INP', file_types = (('XDS input file', ('*.INP', '*.INP*')),)), sg.Button('Save to file'), sg.Button('Clear'),
                     sg.Button('Accept',enable_events=True, key='-SETPAR-', button_color ="white on green"),sg.Button('Cancel',enable_events=True, key='-CANCELPAR-', button_color = "white on red") ]],
                     title='par.dat',title_color=theme_color, relief=sg.RELIEF_GROOVE)]]
            
        window3 = sg.Window('Advanced Processing parameters', layout3, no_titlebar=False, grab_anywhere=False, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event3, values3 = window3.read()

            # open autoPROC parameter list in browser
            if event3 == '-WEB-':
                silent = True
                utility_command = browser + " http://www.globalphasing.com/autoproc/manual/autoPROC4.html#intro"
                utility_function(utility_command, silent)
                time.sleep(1)
                utility_command = browser + " http://www.globalphasing.com/autoproc/manual/appendix1.html"
                utility_function(utility_command, silent)

            # load default template for advanced options
            if event3 == '-DEFTEMP-':
                def_temp()

            # clear custom macro element
            if event3 == 'Clear':
                window3['-PARDAT-'].update(value = '')   

            # load advanced options from parameter-file
            if event3 == '-PARFILE-':
                if os.path.exists(values3['-PARFILE-']) == True:
                    parfile = values3['-PARFILE-']
                    read_param(parfile)

            # extract parameters from XDS.INP file
            if event3 == '-XDSINP-':
                if os.path.exists(values3['-XDSINP-']) == True:
                    xds_inp = values3['-XDSINP-']
                    extract_xds(xds_inp)
                    
            # cancel macro generation an disable custom macro        
            if event3 == '-CANCELPAR-' or event3 == sg.WIN_CLOSED:
                custpars = ''
                disable_macro = not disable_macro
                window['-ENABLEMACRO-'].update(disabled=False)
                window['-CUSTPAR-'].update(value = False)
                window['-MACRO-'].update(disabled=True)
                window['-LISTMACROS-'].update(disabled=True)
                window['-EDPAR-'].update(disabled=True)
                window['-CUSTPAR-'].update(background_color = theme_color1)
                window['-MACROWARNING-'].update(text_color = theme_color1)
                print('')
                print("Custom parameters cleared.")
                window3.close()
                layout3 = None
                window3 = None
                gc.collect()
                break
            #set custom macro
            if event3 == '-SETPAR-':
                custpars = values3['-PARDAT-']
                print('')
                print("Custom parameters set.")
                window['-CUSTPAR-'].update(background_color ="green")
                window['-EDPAR-'].update(disabled=False)
                window3.close()
                layout3 = None
                window3 = None
                gc.collect()                
                break

            # save custom macro to file
            if event3 == 'Save to file':
                layout_export = [[sg.Text('Export macro (a.k.a. parameter file) to:')],
                                [sg.InputText(default_text="Folder to save macro",key='-EXPORTPATH-',size=(36,1)), sg.FolderBrowse(initial_folder = outpath, button_text ='Browse', tooltip = 'Export macro', target = '-EXPORTPATH-', size = (5,1))],
                [sg.Text('Filename:'), sg.InputText(default_text='my_macro',key='-EXPORTNAME-',size=(17,1)), sg.Button("Save"), sg.Button("Cancel")]] 

                window_export = sg.Window('Save custom macro', layout_export, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))

                while True:
                    event_export, values_export = window_export.read()
                    if event_export == sg.WIN_CLOSED or event_export == 'Cancel':
                        window_export.close()
                        layout_export = None
                        window_export = None
                        gc.collect()
                        break
                    if event_export =='Save':
                        filetoexport = os.path.join(values_export['-EXPORTPATH-'],(values_export['-EXPORTNAME-'] + '.dat'))
                        if os.path.exists(values_export['-EXPORTPATH-']) == False:
                            sg.Popup("ERROR: Invalid path!")
                        elif os.path.exists(filetoexport) == True:
                            sg.Popup("ERROR: File already exists!")
                        else:
                            exportfile = open(filetoexport, "w")
                            lines = (values3['-PARDAT-']).split("\n")
                            for line in lines:
                                #print(line)
                                line = line + '\n'
                                exportfile.write(line)  
                            exportfile.close() 
                            save_macro_message = "Saved custom macro / parameter file to:\n" + filetoexport
                            sg.Popup(save_macro_message)
                            window_export.close()
                            layout_export = None
                            window_export = None
                            gc.collect()
                            break   

    # unset custom macro
    if event == '-CUSTPAR-' and values['-CUSTPAR-'] == False:
        window['-ENABLEMACRO-'].update(disabled=False)
        window['-MACRO-'].update(disabled=True)
        window['-LISTMACROS-'].update(disabled=True)
        window['-CUSTPAR-'].update(background_color ="red")
        window['-EDPAR-'].update(disabled=True)
        window['-MACROWARNING-'].update(text_color = theme_color1)
        custpars = ''
        print('')
        print("Custom parameters cleared.")
        time.sleep(0.5)
        window['-CUSTPAR-'].update(background_color = theme_color1)       
                    

    # show list of macros in new window
    if event == '-LISTMACROS-':
        m_list_par = "list"
        list_function(m_list_par)
        layout4 = [[sg.Text('Available macros', font = 'Arial 12')],
                       [sg.Multiline(size=(120,30), key='-MLIST-', autoscroll = True, do_not_clear = True, font ="Courier 9", write_only = True)],
                       [sg.Button('Close'),sg.Button('Show detailed macro parameters', key = '-M_DETAILS-')]]
            
        window4 = sg.Window('Macros', layout4, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event4, values4 = window4.read()
            if event4 == sg.WIN_CLOSED or event4 == 'Close':
                window4.close()
                layout4 = None
                window4 = None
                gc.collect()
                break
            if event4 == '-MACROLIST-':
                listing = values4['-MACROLIST-']
                window4['-MLIST-'].print(listing)
            if event4 == '-M_DETAILS-':
                window4['-MLIST-'].update(value = '')
                m_list_par = "show"
                list_function(m_list_par)
                if event4 == '-MACROLIST-': 
                    listing = values4['-MACROLIST-']
                    window4['-MLIST-'].print(listing)    
                
        
    # open log in webbrowser
    if (event == '-LOGBROWSER-') or ((event == '-RESMEN-') and (values['-RESMEN-'] == "HTML processing log")) :
        page = os.path.join(dumppath, 'autogui_log.html')
        if  os.path.exists(page) == True:
            utility_command = browser + " autogui_log.html"
            silent = True
            utility_function(utility_command, silent)
            print('')
            print('Processing log in webbrowser refreshes every 30 sec.')
        else:
            print('')
            print('nothing here yet')


    # show log-txt in new window
    if (event == '-RESMEN-') and (values['-RESMEN-'] == "Display log (new window)") :
        if watch == True:
            print('Still running, nothing there yet.')
        else:
            logtitle = 'Data processing log from run ' + str(runnumber) + ' in ' + folder
            layout2 = [[sg.Text(logtitle, font = 'Arial 12')],
                       [sg.Multiline(size=(160,30), key='-LOG-', autoscroll = True, do_not_clear = True, font ="Courier 9")],
                       [sg.Button('Close')]]
            
            window2 = sg.Window('Processing log', layout2, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            log_read(filename)
            while True:
                event2, values2 = window2.read()
                if event2 == sg.WIN_CLOSED or event2 == 'Close':
                    window2.close()
                    layout2 = None
                    window2 = None
                    gc.collect()
                    break

    # enable/disable data saving mode
    if (event == '-CLEANUP-') and (values['-CLEANUP-'] == True):
        datasaving = True
    if (event == '-CLEANUP-') and (values['-CLEANUP-'] == False):
        layout_datasaving = [[sg.Text('Do you really want to disable cleanup?', justification = "center", font = "Arial 12", text_color = "red")],
               [sg.Text('Cleaning up files that are almost certainly not required can reduce disk usage by up to 80 %!')],
               [sg.Text('')],              
               [sg.Text('Files required for display of the HTML and any .log or .LP files will be preserved in any case.\nFiles that may be required for PDB deposition or manual data processing or analyses\nwill be in any case be preserved in the "useful_files" subfolder.\nThis includes the final XDS.INP, XDS_ASCII.HKL, INTEGRATE_HKL, CORRECT.LP,\naimless.log and pdb/cif files with remark200 sections.')],
               [sg.Text('')],
               [sg.Text('Please disable cleanup only if you have a very good reason!',font = "Arial 12", text_color = "red")],                       
               [sg.Button('Leave it on', highlight_colors = (theme_color, theme_color)), sg.Button('Disable', highlight_colors = (theme_color, theme_color))]]           
        window_datasaving = sg.Window('Attention', layout_datasaving, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event_datasaving, values_datasaving = window_datasaving.read()
            if event_datasaving == 'Disable':
                datasaving = False
                window_datasaving.close()
                layout_datasaving = None
                window_datasaving = None
                gc.collect()
                break
            if event_datasaving == sg.WIN_CLOSED or event_datasaving == 'Leave it on':
                datasaving = True
                window['-CLEANUP-'].update(value = True)
                window_datasaving.close()
                layout_datasaving = None
                window_datasaving = None
                gc.collect()
                break
    
    # start data processing thread (but only if processes have not been killed before)
    if event == '-THREADON-':
        progress_bar(dumppath, BAR_MAX, numfoundsweeps)
        time.sleep(0.5)                  
        if killflag == False:
            proc_date = (time.strftime("%d %b %Y", time.localtime()))
            csv_entry.append(proc_date)
            csv_entry.append(ds_name)
            window['-LOGBROWSER-'].update(disabled = False)
            autoproc_function(bash_command)
            status = '  \u231b  Job no. ' + str(runnumber) + ' in ' + folder + ' is running.'
            window['-STAT-'].update(value = status, text_color = 'black', background_color = '#FFCB34')
            window['-STATICON-'].update(value = "\u231b", text_color = theme_color)
            time.sleep(0.5)              
            blinkfile = (dumppath + '/output-files/noblink.txt')
            if os.path.exists(blinkfile) == True:
                os.remove(blinkfile)
            blink_color1 = theme_color
            blink_color2 = '#FFCB34'
            blink_function(dumppath, blink_color1, blink_color2)
        else:
            window.write_event_value('-THREADOFF-', '') 

    # receive signal that processing has finished and finalize job    
    if event == '-THREADOFF-':
        time.sleep(0.5)
        watch = False
        filename = "log.txt"
        filename = os.path.join(dumppath, filename)
        print('')
        print(separator)
        print('Processing done.')
        print(separator)
        print('')
        print('')
        refresh = False
        HTML_log(runnumber, dumppath, refresh)
        window['-RESBUTS-'].update(visible = True)
        window['-RUN-'].update(disabled = False)
        window['-RUN-'].update(button_color ="white on green")        
        # copy mtz files
        time.sleep(0.5)
        isofile = dumppath + "/output-files/truncate-unique.mtz"
        isoout = dumppath + "/isotropic.mtz"
        anisofile = dumppath + "/output-files/staraniso_alldata-unique.mtz"
        anisoout = dumppath + "/anisotropic.mtz"
        if  os.path.exists(isofile) == True:
            iso_command ="cp "+ isofile + " " + isoout
            os.system(iso_command)
            time.sleep(1)              
            print('')
            print("Isotropically scaled MTZ (truncate-unique.mtz) copied to:")
            print(isoout)
        if  os.path.exists(anisofile) == True:
            aniso_command ="cp "+ anisofile + " " + anisoout
            os.system(aniso_command)
            time.sleep(1)              
            print('')
            print("Scaled MTZ from STARANISO (staraniso_alldata-unique.mtz) copied to:")
            print(anisoout)
        # copy pdf reports and mmcif files
        stufffolder = dumppath + "/useful_files/"
        if  os.path.exists(stufffolder) == False:
            makestufffolder = "mkdir " + stufffolder
            os.system(makestufffolder)
        isoreport = dumppath + "/output-files/report.pdf"
        anisoreport = dumppath + "/output-files/report_staraniso.pdf"
        isorepout = dumppath + "/isotropic_report.pdf"
        anisorepout = dumppath + "/anisotropic_report.pdf"
        isocif = dumppath + "/output-files/Data_2_autoPROC_TRUNCATE_all.cif"
        anisocif = dumppath + "/output-files/Data_1_autoPROC_STARANISO_all.cif"
        isocifout = dumppath + "/useful_files/isotropic_mmCIF_for_PDB.cif"
        anisocifout = dumppath + "/useful_files/anisotropic_mmCIF_for_PDB.cif"
        if  os.path.exists(isoreport) == True:
            isorep_command ="cp "+ isoreport + " " + isorepout
            os.system(isorep_command)
            print("PDF report for isotropic data:")
            print(isorepout)
        if  os.path.exists(anisoreport) == True:
            anisorep_command ="cp "+ anisoreport + " " + anisorepout
            os.system(anisorep_command)
            print('')
            print("PDF report for anisotropic data from STARANISO:")
            print(anisorepout)
        if  os.path.exists(isocif) == True:
            isocif_command ="cp "+ isocif + " " + isocifout
            os.system(isocif_command)              
            print('')
            print("mmCIF for PDB deposition of isotropic data\n(has to combined with mmCIF from refinement with BUSTER):")
            print(isocifout)
        if  os.path.exists(anisocif) == True:
            anisocif_command ="cp "+ anisocif + " " + anisocifout
            os.system(anisocif_command)
            print('')
            print("mmCIF for PDB deposition of anisotropic data from STARANISO\n(has to combined with mmCIF from refinement with BUSTER):")
            print(anisocifout)
        for useful_file in useful_files_to_copy:
            filetocopy = dumppath + "/output-files/" + useful_file
            if  os.path.exists(filetocopy) == True:
                cp_command = "cp " + filetocopy + " " + dumppath + "/useful_files/"
                os.system(cp_command)
                print(useful_file, 'has been copied to the "useful_files" subfolder')
            
        # set statusbar and timer    
        if killflag == False:
            if  os.path.exists(isofile) == True:
                status = ' \u2714  Job no. ' + str(runnumber) + ' in ' + folder + ' has finished.'
                window['-STAT-'].update(value = status, text_color = 'white', background_color = 'green')
                blinkfile = (dumppath + '/output-files/noblink.txt')
                f = open(blinkfile, "w")
                f.write ('Processing is done!')
                f.close()
                time.sleep(0.1)
                stopfile = (dumppath + '/output-files/stopped.txt')
                f = open(stopfile, "w")
                f.write ('Processing is done!')
                f.close()
                time.sleep(0.2)
                window['-STATICON-'].update(value = "\u2714", text_color = 'darkgreen')
                window['-TIME-'].update(text_color = "green")
                window['-TMSG-'].update(value = "Finished after : ", text_color = "green")
                success = True
                finish_popup(runnumber, dumppath, folder, cutmod, success)
            else:
                status = '  \u26a0  Job no. ' + str(runnumber) + ' in ' + folder + ' has failed!'
                window['-STAT-'].update(value = status, text_color = 'yellow', background_color = 'red') 
                blinkfile = (dumppath + '/output-files/noblink.txt')
                f = open(blinkfile, "w")
                f.write ('Processing is done!')
                f.close()
                time.sleep(0.1)
                stopfile = (dumppath + '/output-files/stopped.txt')
                f = open(stopfile, "w")
                f.write ('Processing is done!')
                f.close()
                window['-TIME-'].update(text_color = "red")
                window['-TMSG-'].update(value = "Failed after : ", text_color = "red")
                window['-STATICON-'].update(value = "\u26a0", text_color = 'red')
                success = False
                finish_popup(runnumber, dumppath, folder, cutmod, success)

        # clean up your shit
        if datasaving == True:
            time.sleep(0.1)
            cleanup_command = "find " + dumppath + "/output-files/ " + cleanup_args
            os.system(cleanup_command)
            print('')
            print('Output files have been cleaned up.')         


    # run pointless
    if event == '-PTLESS-':
        if os.path.exists(isoout) == False:
            print("")
            print("Processing did not finish properly, nothing there to check!")
        else:
            layout_ptless = [[sg.Multiline(size=(75,20), key='-POINTLESS-', write_only = True, autoscroll = True, do_not_clear = True, font="Courier 9")],
                            [sg.Col([[sg.Button('Dismiss', highlight_colors = (theme_color, theme_color)),sg.Text("Running Pointless, please wait!", text_color = "blue", justification ="center", key ='-PL_STAT-', size = (64, None))]], size =(545,60))]]

            window_ptless = sg.Window("POINTLESS says:", layout_ptless, no_titlebar=False, grab_anywhere=False, finalize = True, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
            while True:
                pointless_function()
                event_pl, values_pl = window_ptless.read()
                if event_pl == sg.WIN_CLOSED or event_pl == 'Dismiss':
                    window_ptless.close()
                    layout_ptless = None
                    window_ptless = None
                    gc.collect()
                    break 
            
    # open PDF reports
    if (event == '-RESMEN-') and (values['-RESMEN-'] == "PDF report (isotropic)") :
        if  os.path.exists(isorepout) == True:
            utility_command = pdfviewer + " " + isorepout
            silent = True
            utility_function(utility_command, silent)
            print('')
            print('Opening PDF report (isotropic)')
        else:
            print('')
            print('PDF report not found!')

    if (event == '-RESMEN-') and (values['-RESMEN-'] == "PDF report (anisotropic)") :
        if  os.path.exists(anisorepout) == True:
            utility_command = pdfviewer + " " + anisorepout
            silent = True
            utility_function(utility_command, silent)
            print('')
            print('Opening PDF report (anisotropic)')
        else:
            print('')
            print('PDF report not found!')            
        
    # kill running processes and close windows on cancel
    if event == 'Quit':
        try: 
            win_cur_loc_x = window.current_location()[0] + 200
            win_cur_loc_y = window.current_location()[1] + 50
        except:
            win_cur_loc_x = 300
            win_cur_loc_y = 100    
        layout5 = [[sg.Text("Quit and kill all processes?", justification = "center")],
                [sg.Button(' Yes ', highlight_colors = (theme_color, theme_color)), sg.Button(' No ', highlight_colors = (theme_color, theme_color))]]
        window5 = sg.Window('Sure?', layout5, no_titlebar=False, grab_anywhere=False, location = (win_cur_loc_x, win_cur_loc_y))
        while True:
            event5, values5 = window5.read()
            if event5 == sg.WIN_CLOSED or event5 == ' No ':
                window5.close()
                layout5 = None
                window5 = None
                gc.collect()
                break
            if (event5 == ' Yes '):
                #remove folders with temporary cbfs
                if h52cbf == True and keepcbfs == False:
                    print('')
                    for tmpcbffolder in cbflist:
                        shutil.rmtree(tmpcbffolder)
                        print("Removing temporary folder with mini-cbf files:", tmpcbffolder)
                        #time.sleep(0.5)
                    print('')
                    time.sleep(0.5)
                pid=os.getpid()
                including_parent = True
                window5.close()
                layout5 = None
                window5 = None                 
                window.close()
                layout = None
                window = None
                gc.collect()
                print('bye!')
                killtree(pid, including_parent)
                break
    if event == sg.WIN_CLOSED:
        #remove folders with temporary cbfs
        if h52cbf == True and keepcbfs == False:
            print('')
            for tmpcbffolder in cbflist:
                shutil.rmtree(tmpcbffolder)
                print("Removing temporary folder with mini-cbf files:", tmpcbffolder)
                #time.sleep(0.5)
            print('')
            time.sleep(0.5)
        pid=os.getpid()
        including_parent = True               
        window.close()
        layout = None
        window = None
        gc.collect()
        print('bye!')
        killtree(pid, including_parent)
        break  
              
    # kill processing only on abort
    if event == 'Abort processing' and watch == True:
        layout6 = [[sg.Text("Abort current job?", justification = "center")],
                   [sg.Button(' Yes ', highlight_colors = (theme_color, theme_color)), sg.Button(' No ', highlight_colors = (theme_color, theme_color))]]
        window6 = sg.Window('Sure?', layout6, no_titlebar=False, grab_anywhere=False, location = (window.current_location()[0] + 200, window.current_location()[1] + 50 ))
        while True:
            event6, values6 = window6.read()
            if event6 == sg.WIN_CLOSED or event6 == ' No ':
                window6.close()
                layout6 = None
                window6 = None
                gc.collect() 
                break
            if event6 == ' Yes ':
                window6.close()
                pid=os.getpid()
                including_parent = False
                killtree(pid, including_parent)              
                status = '  \u2620  Job no. ' + str(runnumber) + ' in ' + folder + ' was aborted.'
                window['-STAT-'].update(value = status, text_color = 'yellow', background_color = 'red')
                blinkfile = (dumppath + '/output-files/noblink.txt')
                f = open(blinkfile, "w")
                f.write ('Processing is done!')
                f.close()                
                stopfile = (dumppath + '/output-files/stopped.txt')
                f = open(stopfile, "w")
                f.write ('Processing is done!')
                f.close()
                time.sleep(0.1)
                window['-TIME-'].update(text_color = "red")
                window['-TMSG-'].update(value = "Aborted after : ", text_color = "red")
                window['-STATICON-'].update(value = "\u2620", text_color = 'red')
                print('')
                print('Killed by death!')
                print('') 
                killflag = True
                window['-RUN-'].update(disabled = False)
                layout6 = None
                window6 = None
                gc.collect()
                break

    if event == 'Abort processing' and watch == False:
        print('')
        print('There is nothing running that could be killed.')    

    # prevent new run before old one has finished
    if event == '-RUN-'and watch == True:
        print('')
        print('Still running, please be patient!')

    # Thread event listeners
    if event == '-STATUSUPDATE-':
        status = values['-STATUSUPDATE-']
        window['-STAT-'].update(value = status)
        time.sleep(0.02)
    if event == '-PROGRESSUPDATE-':
        progword = values['-PROGRESSUPDATE-']
        window['-PW-'].update(value = progword)
        time.sleep(0.02)
    if event == '-BARUPDATE-':
        b = values['-BARUPDATE-']
        window['-PROG-'].update(b)
        time.sleep(0.02) 
    if event == '-TIMEUPDATE-':
        timetext = values['-TIMEUPDATE-']
        window['-TIME-'].update(value = timetext)
        time.sleep(0.02)
    if event == '-BLINKUPDATE-':
        blinkcolor = values['-BLINKUPDATE-']
        window['-STATICON-'].update(text_color = blinkcolor)
        time.sleep(0.02)
    if event == '-AUTOPROCLINE-':
        print(values['-AUTOPROCLINE-'])
        time.sleep(0.02)
    if event == '-UTILITYLINE-':
        print(values['-UTILITYLINE-'])
        time.sleep(0.02)    
    if event == '-CONVERSIONLINE-':
        print(values['-CONVERSIONLINE-'])
        time.sleep(0.02)  
        
    # Start run
    if event == '-RUN-'and watch == False:
        window['-TAB1-'].select()
        print('Starting...')
        window['-RESBUTS-'].update(visible = False)
        killflag = False
        window['-OUTPUT-'].update(value = '')
        window['-STATICON-'].update(value = "\u2691", text_color = theme_color)
        if EIGER == True:
            h5 = values['-HDF5-']
            source = "/".join(h5.split("/")[:-1])
            param_h5 = "-h5 " + h5
            param_I =''
        else:    
            source = values['-IMGS-']
            param_I = "-I " + source
            param_h5 =''
            
        folder = values['-OUTF-']
        subdir = values['-SUBFOL-']
        if re.search("\s", subdir) != None:
            subdir = re.sub(" ", "_", subdir)
            print('')
            print('Whitespaces in subfolder(s) have been replaced by "_"')
            print('')

        if os.path.exists(folder) == False:
            print('')
            print('Output: No such directory.')
            status = '  Output: Directory does not exist!'
            window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')

        elif os.path.exists(source) == False:
            print('')
            print('Input: Source not found.')
            status = '  Input: Source not found!'
            window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')

        elif re.search(" ", source) != None:
            print('')
            print('Problem found in:', source)
            print('Input path must not contain any white space characters!')
            status = '  Input path must not contain any white space characters!'
            window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')

        elif re.search(" ", folder) != None:
            print('')
            print('Problem found in:', folder)
            print('Output path must not contain any white space characters!')
            status = '  Output path must not contain any white space characters!'
            window['-STAT-'].update(value = status, text_color = 'red', background_color = '#D0D0D0')     

        else:
            window['-RUN-'].update(disabled = True)
            window['-RUN-'].update(button_color ="white on grey")
            if values['-MKSUB-'] == True:
                folder = os.path.join(folder, subdir)
                if os.path.exists(folder) == True:
                    print('')
                    print('Subdirectory already exists!')
                else:
                    os.makedirs(folder)

            os.chdir(folder)
            showpath = subprocess.Popen("pwd", stdout=subprocess.PIPE, universal_newlines=True, shell=True)
            output = showpath.stdout.readline()
            print('')
            print(separator)
            print('Processing started.')
            print('')
            print('Current path is:', output.strip())

            #folder preparation
            if values['-PREP-'] == True:
                path = os.path.join(folder, checkprep[0])
                print(checkprep[0])
                if os.path.exists(path) == True:
                    print('')
                    print('Folders existing, skipping preparation.')
                    prepcommands = ''
                else:
                    #make subdirectories
                    status = '  Preparing folders for Job no. ' + str(runnumber) + ' in ' + folder
                    window['-STAT-'].update(value = status, text_color = 'white', background_color = 'blue')
                    prepcommands = "mkdir ./"+"; mkdir ./".join(preplist.split())
                    print ('')
                    print('Dataset folder prepared.')
                    print('')
            else:
                prepcommands = ''
                
            # linking files
            if values['-LINKIMG-'] == True:
                path = os.path.join(folder, "images")
                if os.path.exists(path) == True:
                    print('')
                    print('Image folder existing, skipping link creation.')
                    imglinkcommands = ''
                else:
                    #link stuff
                    imglinkcommands = "mkdir ./images; ln -s "+ source + "/* ./images/"
                    print('')
                    print('Links to images created.')
                    print('')
            else:
                imglinkcommands = ''
                
            # get DESY's autoprocessing results, if available
            if values['-LINK-'] == True:
                path = os.path.join(folder, "beamline_processed")
                if os.path.exists(path) == True:
                    print('')
                    print('Folder with auto-processing data existing, skipping link creation.')
                    proclinkcommands = ''
                else:
                    print('')
                    print('Checking for DESY P11 auto-processing results...')
                    desyprocfolder = source.replace("raw", "processed", 1)                       # DESY-style filetree
                    if (os.path.exists(desyprocfolder) == True) and (desyprocfolder != source):
                        print('')
                        print('DESY P11 style file-tree found!')
                        print('Linking beamline auto-processing results to ./beamline_processed.')
                        print('')
                        proclinkcommands = "mkdir ./beamline_processed; ln -s " + desyprocfolder + "/* ./beamline_processed/"
                    else:
                        print('')
                        print('Checking for SLS/BESSY II/ESRF auto-processing results...')
                        proclinkcommands = "mkdir ./beamline_processed"
                        blprocfolders = []
                        for thing in os.scandir(source):                                           # BESSY and SLS have auto-processing results usually in subfolders within image folder              
                            if thing.is_dir():
                                blprocfolders.append(thing.path)
                                #print(thing.path)
                        if len(blprocfolders) != 0:
                            print('')
                            print('Auto-processing results found!')
                            print('Linking beamline auto-processing results to ./beamline_processed.')
                            print('')
                            for blprocfolder in blprocfolders:
                                proclinkcommands = proclinkcommands + "; ln -s " + blprocfolder + " ./beamline_processed/"
                            #print(proclinkcommands)
                        else:
                            print('')
                            print('Checking for ESRF auto-processing results...')
                            esrfprocfolder = source.replace("RAW_DATA", "PROCESSED_DATA", 1)                       # ESRF-style filetree
                            if (os.path.exists(esrfprocfolder) == True) and (esrfprocfolder != source):
                                print('')
                                print('ESRF style file-tree found.')
                                print('Linking beamline auto-processing results to ./beamline_processed.')
                                print('')
                                proclinkcommands = "mkdir ./beamline_processed; ln -s " + esrfprocfolder + "/* ./beamline_processed/"
                            else:
                                proclinkcommands = ''
                                print('')
                                print('No auto-processing results found')
                                print('')
            else:
                proclinkcommands = ''
                
            # assemble utility command and carry out operation
            utility_command = prepcommands + "; " + imglinkcommands + "; " + proclinkcommands +"; ls -ltrogh; du -sh"
            utility_command = re.sub(r"^(; )+", "",(utility_command))
            utility_command = re.sub(r"(; )+", "; ",(utility_command))                         
            if utility_command != "ls -ltrogh; du -sh":
                status = '  Linking files for Job no. ' + str(runnumber) + ' in ' + folder
                window['-STAT-'].update(value = status, text_color = 'white', background_color = 'blue')
            #print(utility_command)
            silent = False    
            utility_function(utility_command, silent)
            time.sleep(1)                 
                
            # check for existing runs and set new run-number
            while True:
                runpath = 'autoproc/autoproc_' + str(runnumber)
                dumppath = os.path.join(folder, runpath)
                if os.path.exists(dumppath):
                    runnumber += 1
                else:
                    os.makedirs(dumppath)
                    os.chdir(dumppath)
                    print('')
                    print('Processing run number for this dataset: ', runnumber)
                    print ('Output will be found in: ./' + runpath)
                    print('')
                    break
                
            #display buttons for log options
            vFlag = True
            hFlag = False
            window['-COL4-'].update(visible = vFlag)
            window['-COLX4-'].update(visible = hFlag)
            refresh = True
            HTML_log(runnumber, dumppath, refresh)

            # set parameters
            if EIGER == True and h52cbf == True:
                cbffolder = os.path.join(folder, tmpcbffolder)
                param_I = "-I " + cbffolder   

            param_d = "-d " + dumppath + "/output-files"
            if values['-RESLIM-'] == True:
                param_R = "-R " + values['-LOWR-'] + ' ' + values['-HIGHR-']
            else:
                param_R =''
            
            if values['-FREECOPY-'] == True:
                if os.path.exists(values['-REF-']) == True:
                    param_free = "-free " + values['-REF-']
                else:
                    print('')
                    print('MTZ with freeR-flag not found!')
                    status = '  MTZ with freeR-flag not found!'
                    window['-STAT-'].update(value = status, text_color = 'white', background_color = 'orange')
            else:
                param_free = ''
                
            if values['-ANOMYES-'] == True:
                param_Ano = "-ANO"
                if values['-ANOMLARGE-'] == True:
                    param_Ano = "-ANO ExpectLargeHeavyAtomSignal=\"yes\" ExpectLargeHeavyAtomSignalScaleAndMerge=\"yes\""
            elif values['-ANOMNO-'] == True:
                param_Ano = "-noANO"         
            else: param_Ano = ''
            
            if values['-SGREF-'] == True:
                if os.path.exists(values['-REF-']) == True:
                    param_ref = "-ref " + values['-REF-']
                else:
                    print('')
                    print('Reference MTZ not found!')
                    status = '  Reference MTZ not found!'
                    window['-STAT-'].update(value = status, text_color = 'white', background_color = 'orange')
            else:
                param_ref =''
            
            if values['-SGMAN-'] == True and (values['-SPG-'] != ''):
                param_symm = "symm=" + '\"' + values['-SPG-'] + '\"'
            else:
                param_symm = ''
                
            if values['-SGMAN-'] == True and (values['-CELL-'] != ''):       
                param_cell = "cell=" + '\"' + values['-CELL-'] + '\"'
            else:
                param_cell = ''
            
            if (values['-ENABLEMACRO-'] == True) and (values['-MACRO-'] != '') and (values['-MACRO-'] != '---Select macro---'):
                param_M = "-M " + values['-MACRO-']
            if (values['-CUSTPAR-'] == True) and (custpars != ''):
                pardat = dumppath + "/par.dat"
                save_param(pardat, custpars)
                param_M = "-M " + pardat
            if (values['-CUSTPAR-'] == False) and (values['-ENABLEMACRO-'] ==False):
                param_M = ''
                custpars = ''
                
            if values['-NPROC-'] != '':
                if int(values['-NPROC-']) > int(maxprocs):
                    param_nthreads = "-nthreads " + maxprocs
                    print('')
                    print('The maximum number of allowed processors is:', maxprocs)
                    print('The number of threads has thus been decreased.')
                    print('')
                else:    
                    param_nthreads = "-nthreads " + values['-NPROC-']
                    print('')
                    print('The number of threads has been set to:', values['-NPROC-'])
                    print('')
            else:
                param_nthreads = nprocs

            if values['-SWEEPSET-'] == True:
                param_sweeps = sweepcommands
            else:
                param_sweeps = ''

            if param_sweeps != '':
                param_h5 = ''

            if h52cbf == True:
                param_h5 = ''                

            if values['-BADIMGS-'] == False:
                param_bad_imgs = 'autoPROC_AnalyseForPoorImageRanges=no'
            else:
                param_bad_imgs = ''


            if values['-CUTSEL-'] == "CC(1/2)>=0.3 (default)":    
                param_cut = ''
                cutmod = False
            elif values['-CUTSEL-'] == "I/sig(I)>=2.0, CC(1/2)>=0.3, Rpim<=0.6 (old default)":
                param_cut = 'ScaleAnaISigmaCut_123="0.1:0.1 0.5:0.5 0.5:1.0 1.0:2.0" ScaleAnaRpimallCut_123="99.9999:99.9999 0.9:0.9 0.8:0.8 0.6:0.6" ScaleAnaCChalfCut_123="-1.0:-1.0 0.0:0.0 0.1:0.1 0.3:0.3"'
                # as used until autoPROCVersion20220608
                cutmod = True      
            else:
                param_cut = 'ScaleAnaRmergeCut_123="99.9999:99.9999" ScaleAnaRpimallCut_123="99.9999:99.9999 0.9:0.9 0.8:0.8 '+ values['-RPIMVAL-'] + ':' + values['-RPIMVAL-'] +'" ScaleAnaRmeasallCut_123="99.9999:99.9999" ScaleAnaISigmaCut_123="0.1:0.1 0.5:0.5 0.5:1.0 1.0:' + values['-ISIGIVAL-'] +'" ScaleAnaCompletenessCut_123="0.0:0.0" ScaleAnaCChalfCut_123="-1.0:-1.0 0.0:0.0 0.1:0.1 '+ values['-CCHALFVAL-'] + ':' + values['-CCHALFVAL-'] +'"'
                cutmod = [values['-ISIGIVAL-'], values['-CCHALFVAL-'], values['-RPIMVAL-']]    

            if values['-DETSEL-'] == "In-house: PILATUS 300K":
                param_extra = inhouse_pars
            elif values['-DETSEL-'] == "Electron diffraction":
                param_extra = microED_pars
            else:
                param_extra = ''

            if datasaving == True:
                param_footprint = 'AutoProcSmallFootprint="yes"'
            else:
                param_footprint = ''

            if (values['-PARSON-'] == True) and (values['-EXTRAPARS-'] != ''):    
                param_appended = values['-EXTRAPARS-']
            else:   
                param_appended = ''       

            if values['-BEAMCENTREMODE-'] == 'header':
                beamcentremode = "header"
                beamcentrex = "n/a"
                beamcentrey = "n/a"
            elif values['-BEAMCENTREMODE-'] == 'try possible transformations':
                beamcentremode = "try possible transformations"
                beamcentrex = "n/a"
                beamcentrey = "n/a"
            elif values['-BEAMCENTREMODE-'] == 'guess':
                beamcentremode = "guess"
                beamcentrex = "n/a"
                beamcentrey = "n/a"
            elif (values['-BEAMCENTREMODE-'] == 'specified below') and (values['-BEAMX-'] != 'n/a' and values['-BEAMX-'] != '') and (values['-BEAMY-'] != 'n/a' and values['-BEAMY-'] != ''):
                beamcentremode = "specified below"
                beamcentrex = values['-BEAMX-']
                beamcentrey = values['-BEAMY-']
            else:
                beamcentrex = "n/a"
                beamcentrey = "n/a" 
            if (values['-DISTBOX-'] == True) and (values['-DIST-'] != 'n/a' and values['-DIST-'] != ''):    
                distance = values['-DIST-']
            else:    
                distance = "n/a"     
            if (values['-WLBOX-'] == True) and (values['-WAVEL-'] != 'n/a' and values['-WAVEL-'] != ''):    
                wavelength = values['-WAVEL-']
            else:   
                wavelength = "n/a"   
            if (values['-OSCBOX-'] == True) and (values['-OSC-'] != 'n/a' and values['-OSC-'] != ''):    
                oscillation = values['-OSC-']
            else:    
                oscillation = "n/a"  
            if (values['-OVERLOADBOX-'] == True) and (values['-OVERLOAD-'] != 'n/a' and values['-OVERLOAD-'] != ''):    
                overload = values['-OVERLOAD-']
            else:    
                overload = "n/a"
            if (values['-PIXELSIZEBOX-'] == True) and (values['-XPIXELSIZE-'] != 'n/a' and values['-XPIXELSIZE-'] != '') and (values['-YPIXELSIZE-'] != 'n/a' and values['-YPIXELSIZE-'] != ''):    
                pixelsizex = values['-XPIXELSIZE-']
                pixelsizey = values['-YPIXELSIZE-']
            else:   
                pixelsizex = "n/a"
                pixelsizey = "n/a"
            if (values['-PIXELNUMBOX-'] == True) and (values['-XPIXELS-'] != 'n/a' and values['-XPIXELS-'] != '') and (values['-YPIXELS-'] != 'n/a' and values['-YPIXELS-'] != ''):   
                nopixelx = values['-XPIXELS-']
                nopixely = values['-YPIXELS-']
            else:    
                nopixelx = "n/a"
                nopixely = "n/a" 

            raw_parameters =([beamcentremode, beamcentrex, beamcentrey, distance, wavelength, oscillation, overload, pixelsizex, pixelsizey, nopixelx, nopixely, extrapars]) 
            exp_parameters = []
            for parameter in raw_parameters:
                parameter = parameter.strip()
                if parameter != 'header' and parameter != '' and parameter != 'n/a':
                    exp_parameters.append(parameter)
            #print(str(len(exp_parameters)), "parameters set")
            #for parameter in exp_parameters:
                #print(parameter)
            if beamcentremode == "try possible transformations":
                beam_par = 'BeamCentreFrom="getbeam:init"'
            elif beamcentremode == "guess":
                beam_par ='BeamCentreFrom="getbeam:refined"'       
            elif beamcentremode == "specified below" and beamcentrex != "" and beamcentrex != "n/a" and beamcentrey != "" and beamcentrey != "n/a":
                beam_par = 'beam="' + beamcentrex + ' ' + beamcentrey + '"'
            else:
                beam_par = ""
            if distance != "n/a" and distance != "":
                dist_par = 'autoPROC_XdsKeyword_DETECTOR_DISTANCE="' + distance + '"'
            else:
                dist_par = ""
            if wavelength != "n/a" and wavelength != "":
                wavel_par = 'autoPROC_XdsKeyword_X-RAY_WAVELENGTH="' + wavelength + '"'
            else:
                wavel_par = ""
            if oscillation != "n/a" and oscillation != "":
                osc_par = 'autoPROC_XdsKeyword_OSCILLATION_RANGE="' + oscillation + '"'
            else:
                osc_par = ""
            if overload != "n/a" and overload != "":
                overload_par = 'autoPROC_XdsKeyword_OVERLOAD="' + overload + '"'
            else:
                overload_par = ""    
            if pixelsizex != "" and pixelsizex != "n/a" and pixelsizey != "" and pixelsizey != "n/a":
                pixsize_par = 'autoPROC_XdsKeyword_QX="' + pixelsizex + '" ' + 'autoPROC_XdsKeyword_QY="' + pixelsizey + '"'
            else:
                pixsize_par = ""
            if nopixelx != "" and nopixelx != "n/a" and nopixely != "" and nopixely != "n/a":
                pixnum_par = 'autoPROC_XdsKeyword_NX="' + nopixelx + '" ' + 'autoPROC_XdsKeyword_NY="' + nopixely + '"'
            else:
                pixnum_par = ""
            param_exp = re.sub("\s+", " ", (" " + (' '.join([beam_par, dist_par, wavel_par, osc_par, overload_par, pixsize_par, pixnum_par]))))    
            param_exp = re.sub(r"^\s+", "", param_exp)
            print(param_exp)
            print('')
            param_untrusted = ''
            for untrusted_rectangle in untrusted_rectangle_coords:
                untrusted_string = ('autoPROC_XdsKeyword_UNTRUSTED_RECTANGLE="' + str(untrusted_rectangle[0]) + ' ' + str(untrusted_rectangle[1]) + ' ' + str(untrusted_rectangle[2]) + ' ' + str(untrusted_rectangle[3]) + '"')
                print(untrusted_string)
                param_untrusted = param_untrusted + " " + untrusted_string
            for untrusted_ellipse in untrusted_ellipse_coords:
                untrusted_string = ('autoPROC_XdsKeyword_UNTRUSTED_ELLIPSE="' + str(untrusted_ellipse[0]) + ' ' + str(untrusted_ellipse[1]) + ' ' + str(untrusted_ellipse[2]) + ' ' + str(untrusted_ellipse[3]) + '"')
                print(untrusted_string)
                param_untrusted = param_untrusted + " " + untrusted_string
            for untrusted_quad in untrusted_quad_coords:
                untrusted_string = ('autoPROC_XdsKeyword_UNTRUSTED_QUADRILATERAL="' + str(untrusted_quad[0][0]) + ' ' + str(untrusted_quad[0][1]) + ' ' + str(untrusted_quad[1][0]) + ' ' + str(untrusted_quad[1][1]) + ' ' + str(untrusted_quad[3][0]) + ' ' + str(untrusted_quad[3][1]) + ' ' + str(untrusted_quad[2][0]) + ' ' + str(untrusted_quad[2][1]) + '"')
                print(untrusted_string)
                param_untrusted = param_untrusted + " " + untrusted_string
            if len(modified_beamcenter) > 1:
                print('Beam is now: ', str(modified_beamcenter[0]), str(modified_beamcenter[1]))
            if len(dectris_gap_coords) > 1:
                print('Detector gaps:')
                for gap in dectris_gap_coords:
                    untrusted_string = ('autoPROC_XdsKeyword_UNTRUSTED_RECTANGLE="' + str(gap[0]) + ' ' + str(gap[1]) + ' ' + str(gap[2]) + ' ' + str(gap[3]) + '"')
                    print(untrusted_string)
                    param_untrusted = param_untrusted + " " + untrusted_string

            #assemble commandline argument    
            auto_command = (' '.join(["process", param_I, param_h5, param_d, param_R, param_Ano, param_ref, param_free, param_M, param_symm, param_cell, param_extra, param_sweeps, param_bad_imgs, param_cut, param_exp, param_untrusted, param_nthreads, param_footprint, param_appended]))
            auto_command = (' '.join(auto_command.split()))
            bash_command = auto_command + " | tee log.txt"
            print('')
            print('Running AutoPROC with command line:')
            print(auto_command)
            print('')
            #print(values) #(for debug)
            
            # start processing         
            time.sleep(0.5)
            watch = True            
            start_t = time.time()
            stopfile = (dumppath + '/output-files/stopped.txt')
            if os.path.exists(stopfile) == True:
                os.remove(stopfile)
            timer_function(dumppath)
            window['-TIME-'].update(text_color = theme_color)
            window['-TMSG-'].update(value = "Elapsed time : ", text_color = theme_color)
            #progress_bar(dumppath)
            
            # check if HDF5 to mini-cbf conversion is required
            if h52cbf == True:
                cbfconversion_function(cbffolder, h5, BAR_MAX)
                window['-LOGBROWSER-'].update(disabled = True)
                status = ' \u2398  Converting EIGER HDF5 to mini-cbf. This may take a while.'
                window['-STAT-'].update(value = status, text_color = 'white', background_color = 'blue')
                window['-STATICON-'].update(value = "\u2398", text_color = theme_color)
                time.sleep(0.5)
                blinkfile = (dumppath + '/output-files/noblink.txt')
                if os.path.exists(blinkfile) == True:
                    os.remove(blinkfile)
                blink_color1 = theme_color
                blink_color2 = 'blue'
                blink_function(dumppath, blink_color1, blink_color2)
            # start processing
            else:
                window.write_event_value('-THREADON-', '')
                


            
            
            
            
        
                
