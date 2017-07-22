#!/usr/bin/python
#-*- coding: windows-1250 -*-

import libtagaudio as lta

import sys

tags = lta.read_new_tags( sys.argv[1] )
print tags
