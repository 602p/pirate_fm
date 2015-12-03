#!/usr/bin/python

import urllib, json, sys, server, os

if len(sys.argv)==1:
	print("USAGE: ./download_playlist.py PLAYLIST-ID [force]")
	sys.exit(1)

base="https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=50&playlistId=[PLAYLIST]&key="+open('apikey.txt','r').read()

ret=json.loads(urllib.urlopen(base.replace("[PLAYLIST]",sys.argv[1])).read())

#ret['items'][0]['snippet']["resourceId"]["videoId"]

videos=[]

for element in ret['items']:
	videos.append(element['snippet']['resourceId']['videoId'])

server.cachedata=server.load_cachedata()

print "Videos -> "+", ".join(videos)
if "force" not in sys.argv:
	if raw_input("OK? (y/N)").upper()!="Y":
		print "Aborted."
		sys.exit(0)

for vid in videos:
	if vid in server.cachedata["valid_caches"]:
		print "Skipping "+vid+" (already cached)"
		continue
	print "Downloading "+vid+"... ",
	os.system("rm cache/"+vid+".wav")
	os.system("youtube-dl -f 140 -o - \""+vid+"\" 2> youtube-dl.log | ffmpeg -i - -f wav -acodec pcm_s16le -ac 2 cache/"+vid+".wav 2> ffmpeg.log")
	log=open("ffmpeg.log",'r').read()+open("youtube-dl.log",'r').read()
	open("test.txt",'w').write(log)
	if "signal 2" in log or "Interrupted" in log or "KeyboardInterrupt" in log:
		print "[INTERRUPTED]"
		continue
	server.cachedata["valid_caches"].append(vid)
	print "[COMPLETE]"

server.save_cachedata()
