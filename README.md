# RoboticArmControllerforDiagnostics
Repository of all source code and instructions for how to run our Robotic Arm Controller for diagnostics project for WUSTL CSE520S Real-Time Systems

## Install

First, follow the instructions to setup the Speech Recognition API with microphone capabilities [here](https://github.com/Uberi/speech_recognition). There are specific instructions for each host OS as well as version of Python, so it is more efficient for us to point you there.

Once that is setup, you must install the AWS IoT SDK for Python. **Either** clone [this](https://github.com/aws/aws-iot-device-sdk-python) repository and run `python setup.py install`, run `pip install AWSIoTPythonSDK` from a terminal, or download the zip file [here](https://s3.amazonaws.com/aws-iot-device-sdk-python/aws-iot-device-sdk-python-latest.zip) and run `python setup.py install`.

Then, download the HostController.py program and run it while the controller arm is connected via USB. You may need to alter the USB port specified within the Python program to be compatible with your host.

Since the program communicates directly to the system within our personal AWS account, you must contact me in order to register your email and receive the proper certificates and keys.

## How to Run

Once everything is setup, simply run `python HostController.py` from a terminal with the controller arm connected via USB port. Say "start" to begin the test, move the controller arm to perform the test, and say "stop" once you are finished. You will then receive an email with a graph analyzing your performance.

## Other Source Code

This repository also contains the software running on the Teensy 3.2 microcontroller (ControllerArmArduino) as well as our AWS Lambda programs.