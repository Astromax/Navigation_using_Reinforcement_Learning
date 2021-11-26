# Navigation_using_Reinforcement_Learning
Solution to the Udacity DRL Navigation Project

#Project Overview
In this project we have an agent running around in a 2D environment filled with yellow & blue bananas.  The objective is to obtain as many yellow bananas, each worth +1, as possible, while avoiding the blue bananas, each worth -1.  The state space is a 37 element vector corresponding to rays spread out from the agent, it's deliberately left vague as to what exactly these rays are supposed to be physically but they appear to be like LIDAR, with beams sent forward at several different angles.  The action space is just the four directions of motion: forward, backward, left, right.  The environment is considered "solved" when the average score over 100 consecutive episodes is 13 or higher.

#Setup
This was done in the Udacity Workspace, but can be done locally on Windows, Mac, or Linux.  Follow these instructions from the program to do so.  
Install Conda on Windows.
Create a env Conda using Python 3.6
conda create --name drlnd python=3.6 
3. Activate this env.

conda activate drlnd
4. Within this environment, you will need to install the necessary packages. There are several options for this, as you can install all packages manually using PIP or clone an existing conda environment.

4.1 Install Packages using PIP. First of all, you should go to your workspace, and download all your work using the following command in a cell from your notebook:
 

!tar chvfz notebook.tar.gz *
Then, unzip this file, and go to the directory where you unzipped it. In this directory, open a terminal and introduce the next command to move to the python folder.

cd python
Using the terminal in this folder, introduce the next command in order to install all the packages:

pip install .
In case of problems with some of the packages, just remove it from the requirements.txt file and try to install it manually. I seem to remember that the torch==0.4.0 package is missing. If this installation gives you your problem, there are two solutions:

1) Modify the torch==0.4.1 file, as this version is also supported.

2) Install torch==0.4.0 manually: Download torch 0.4.0 wheel from http://download.pytorch.org/whl/cpu/torch-0.4.0-cp36-cp36m-win_amd64.whl. Once downloaded, introduce:

pip install --no-deps FILE-PATH\torch-0.4.0-cp36-cp36m-win_amd64.whl
4.2. The second solution (in case that the previous one does not work) consist into clone an existing conda env. To avoid problems with package insertion, I have exported my conda environment to you, and you can easily clone it. To download it, click on this link.
4.2.1. Create (and activate) a new environment with Python 3.6 via Anaconda.
conda create --name your_env_name python=3.6
4.2.2. Clone the repository, and navigate to the python/ folder
conda env create -f environment_DRL.yml


#Running the code
The central notebook is self-contained, if you have access to Udacity's Workspace then just run every cell in order and it will work.


