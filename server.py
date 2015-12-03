#!/usr/bin/python
from flask import Flask, request
import subprocess, thread, os, signal, sys, json, atexit, threading, util
app=Flask(__name__)

channel=107.5
sub=None

cachedata={
 "valid_caches":[],
 "name_mappings":{}
}

def load_cachedata():
	if "cachedata.json" in os.listdir("."):
		with open("cachedata.json", 'r') as fd:
			data=json.load(fd)
	else: return cachedata
	return data

def save_cachedata():
	with open("cachedata.json", 'w') as fd:
		json.dump(cachedata, fd)

def validate_cache(url):
	print("Validating Cache of ["+url+"]")
	if url not in cachedata["valid_caches"]:
		cachedata["valid_caches"].append(url)
		cachedata["name_mappings"][url]=util.get_name(url)

def destroy_cache(url):
	print("Destroying Cache of ["+url+"]")
	if url in cachedata["valid_caches"]:
		del cachedata["valid_caches"][cachedata["valid_caches"].index(url)]
	if url+".wav" in os.listdir("cache"):
		os.remove("cache/"+url+".wav")

def check_success():
	t="play_youtube_success" in os.listdir(".")
	if t: os.remove("play_youtube_success")
	return t

def play_url(url):
	stop_thread()
	#validate_cache(url)
	if url not in cachedata["valid_caches"]:
        	print "Streaming..."
        	cmd="youtube-dl -f 140 -o - \""+url+"\" | ffmpeg -i - -f wav -acodec pcm_s16le -ac 2 - | tee \"cache/"+url+".wav\" | sudo ./pifm - "+str(channel)+" 44100 stereo > pifm.log"
	else:
        	print "Playing from cache..."
        	cmd="sudo ./pifm cache/"+url+".wav "+str(channel)+" 44100 stereo"
	print "(cmd=\""+cmd+"\")"
	global sub
	sub=subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
	sub.url=url
	#validate_cache(url)

def stop_thread():
	if sub:
		#os.killpg,' signal.SIGTERM)
		s=open("pifm.log",'r').read()
		v="exiting" in s and "recv" not in s
		print("IN ->"+str(v))
		os.killpg(sub.pid, signal.SIGTERM)
		if v: validate_cache(sub.url)

def cleanup():
	os.system("sudo python cleanup.py")

@app.route("/invoke/<url>")
def invoke(url):
	play_url(url)
	return "Invoked "+("(streaming)" if url not in cachedata["valid_caches"] else "(cached)")+" "+(cachedata["name_mappings"][url] if url in cachedata["name_mappings"] else "")

@app.route("/stop")
def stop():
	stop_thread()
	return "Stopped"

@app.route("/set/<int:channel>")
def set(chan):
	global channel
	channel=chan
	return "Set (channel="+str(chan)+")"

@app.route("/get")
def get():
	return json.dumps(cachedata)

@app.route("/clean")
def clean():
	stop_thread()
	cleanup()

@app.route("/")
def root():
	return "OK"


if __name__=="__main__":
	if "cachedata.json" in os.listdir("."):cachedata=load_cachedata()
	atexit.register(save_cachedata)
	if "nocsd" not in sys.argv:
		atexit.register(cleanup)
	app.run(host="0.0.0.0", port=5000, debug=True if "debug" in sys.argv else False)
	
