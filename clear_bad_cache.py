#!/usr/bin/python

import os, server

valid=server.load_cachedata()["valid_caches"]
toclear=[]

for x in os.listdir('cache'):
	if x!="dummy" and x.replace(".wav","") not in valid:
		toclear.append(x)

print "This will remove: "+", ".join(toclear)
if raw_input("Sure? (y/N) ").upper()=="Y":
	for x in toclear:
		os.system("yes|sudo rm cache/"+x)
	print "Done"
else:
	print "Aborted"
