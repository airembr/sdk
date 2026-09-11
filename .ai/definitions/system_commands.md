# System Commands API

System commands API is a set of functions that can be run to access some system functionality. It is located at: ~/PycharmProjects/dev/airembr/sdk/airembr/system/command
and servers as entry point to the system.

## What responsibility it has 

* has all system functions
* seperates functions per object
* serves as entry point for system operation, no other files can be imported in upper lavers like API, CLI

## What is does not do

* Does not control access rights
* Rights can be controlled only by object that controls context of execution.
