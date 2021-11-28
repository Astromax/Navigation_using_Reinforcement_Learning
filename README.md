# Navigation_using_Reinforcement_Learning
Solution to the Udacity DRL Navigation Project

*Project Overview

In this project we have an agent running around in a 2D environment filled with yellow & blue bananas.  The objective is to obtain as many yellow bananas, each worth +1, as possible, while avoiding the blue bananas, each worth -1.  The state space is a 37 element vector corresponding to rays spread out from the agent, it's deliberately left vague as to what exactly these rays are supposed to be physically but they appear to be like LIDAR, with beams sent forward at several different angles.  The action space is just the four directions of motion: forward, backward, left, right.  The environment is considered "solved" when the average score over 100 consecutive episodes is 13 or higher.

*Setup

This was done in the Udacity Workspace, but can be done locally on Windows, Mac, or Linux.  Follow these instructions from the program to do so (props to Github user https://github.com/handria-ntoanina/unity-ml-banana/blob/master/README.md for providing the setup instructions for running locally).  

* Perform a minimal install of OpenAI gym
	* If using __Windows__, 
		* download swig for windows and add it the PATH of windows
		* install Microsoft Visual C++ Build Tools
	* then run these commands
	```bash
	pip install gym
	pip install gym[classic_control]
	pip install gym[box2d]
	```
* Install the dependencies under the folder python/
```bash
	cd python
	pip install .
```
* Create an IPython kernel for the `dqn` environment
```bash
	python -m ipykernel install --user --name dqn --display-name "dqn"
```
* Download the Unity Environment (thanks to Udacity) which matches your operating system
	* [Linux](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Linux.zip)
	* [Mac OSX](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana.app.zip)
	* [Windows (32-bits)](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Windows_x86.zip)
	* [Windows (64 bits)](https://s3-us-west-1.amazonaws.com/udacity-drlnd/P1/Banana/Banana_Windows_x86_64.zip)

* Start jupyter notebook from the root of this python codes
```bash
jupyter notebook
```
* Once started, change the kernel through the menu `Kernel`>`Change kernel`>`dqn`
* If necessary, inside the ipynb files, change the path to the unity environment appropriately


*Running the code 

Once the Jupyter environment is set up, upload qnetworks.py, replays.py, navagents.py, and the main notebook to the directory.  Assuming the workspace has all the dependencies already setup (as the Udacity Workspace did), then one should be able to run the main notebook cell-by-cell to reproduce the results.  The main notebook is arguably just an organizer, the real work was done in writing replays.py and navagents.py, indeed it looks like the prioritized replay needs some pretty serious optimization to be truly functional.


