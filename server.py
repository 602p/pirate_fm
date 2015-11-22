from flask import Flask, request
import subprocess, thread, os, signal, sys
app=Flask(__name__)

channel=107.5
proc=None

@app.route("/invoke/<url>")
def invoke(url):
	global proc
	if proc: os.killpg(proc.pid, signal.SIGTERM)
	proc=subprocess.Popen("./play_youtube.py "+url+" "+str(channel), cwd=".", shell=True, preexec_fn=os.setsid)
	return "Invoked "+("(may take a while to download)" if url+".wav" not in os.listdir("..") else "(cached)")

@app.route("/stop")
def stop():
	global proc
	if proc:
		os.killpg(proc.pid, signal.SIGTERM)
		os.system("pkill youtube-dl;pkill ffmpeg;pkill pifm")
	proc=None
	return "Stopped"

@app.route("/set/<int:channel>")
def set(chan):
	global channel
	channel=chan
	return "Set (channel="+str(chan)+")"

@app.route("/")
def root():
	return "OK"


app.run(host="0.0.0.0", port=5000, debug=True if len(sys.argv)!=1 else False)
