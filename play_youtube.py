#! /usr/bin/python

import os, sys

if len(sys.argv) < 3 or len(sys.argv) > 4:
	print "Usage: play_youtube.py URL"
	sys.exit(1)

if sys.argv[1]+".wav" not in os.listdir("./cache"):
	print "Streaming..."
	cmd="youtube-dl -f 140 -o - \""+sys.argv[1]+"\" | ffmpeg -i - -f wav -acodec pcm_s16le -ac 2 - | tee \"cache/"+sys.argv[1]+".wav\" | sudo ./pifm - "+sys.argv[2]+" 44100 stereo"
else:
	print "Playing from cache..."
	cmd="sudo ./pifm cache/"+sys.argv[1]+".wav "+sys.argv[2]+" 44100 stereo"
print "(cmd=\""+cmd+"\")"
os.system(cmd)
with open("play_youtube_success", 'w'): pass
