# KAAVS: Kind Of Automatic Audio to Video Synchronizer
The KAAVS project is an attempt to simplify the life of an average aviation YouTuber who records vidoes in the cockpit and struggles with synchronizing audio and video streams from various devices.
The solution comprises of two parts: 
- A device with an audio output, that can be connected to an audio recorder
- A command-line tool that processes the recorded audio and splits it into parts

## How this works
The idea is to use the device for generating a synchronization tone. 
The tone should be recorded on a digital audio recorder at the start of every scene. 
Then the command-line tool can be used to cut the audio file into scenes. 
Video content can then be aligned to the audio clips. 
This should be relativelly easy if the user makes sure the KAAVS device is visible on the video recordings when it is activated.


## Prerequisites
1. Install ffmpeg (essentials). You can find the most recent build of FFMPEG [here](https://www.gyan.dev/ffmpeg/builds/). The "essentials" is enough.

2. Install SciPy. If you don't have Python yet, go to the [Python downloads site] (https://www.python.org/downloads/) and get it. You need the 3.x version, not the 2.x. Then invoke:
    `python -m pip install --user numpy scipy matplotlib pandas sympy nose` to install the required libraries.

## Device


## Command-line Tool


