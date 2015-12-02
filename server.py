from flask import Flask, request
import subprocess, thread, os, signal, sys, json, atexit, threading
app=Flask(__name__)

channel=107.5
sub=None

cachedata={
 "valid_caches":[]
}

def load_cachedata():
	with open("cachedata.json", 'r') as fd:
		data=json.load(fd)
	return data

def save_cachedata():
	with open("cachedata.json", 'w') as fd:
		json.dump(cachedata, fd)

def validate_cache(url):
	print("Validating Cache of ["+url+"]")
	if url not in cachedata["valid_caches"]:
		cachedata["valid_caches"].append(url)

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
		#os.killpg(sub.pid, signal.SIGTERM)
		print("PIFM.LOG -> "+open("pifm.log",'r').read())
		os.killpg(sub.pid, signal.SIGTERM)
		if "exiting" in open("pifm.log",'r').read(): validate_cache(sub.url)

@app.route("/invoke/<url>")
def invoke(url):
	play_url(url)
	return "Invoked "+("(streaming)" if url+".wav" in os.listdir("cache") else "(cached)")

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

@app.route("/")
def root():
	return "OK"


if __name__=="__main__":
	if "cachedata.json" in os.listdir("."):cachedata=load_cachedata()
	atexit.register(save_cachedata)
	app.run(host="0.0.0.0", port=5000, debug=True if len(sys.argv)!=1 else False)
	
