#!/usr/bin/python

import json, urllib, server, sys

#server.cachedata=server.load_cachedata()

def get_name(vidid):
	base="https://www.googleapis.com/youtube/v3/videos?part=snippet&id=[ID]&key="+open('apikey.txt','r').read()
	ret=json.loads(urllib.urlopen(base.replace("[ID]",vidid)).read())
	return ret['items'][0]['snippet']['title'] if len(ret['items'])>0 else "NAME_NOT_FOUND"

def update_names():
	server.cachedata=server.load_cachedata()
	for i in server.cachedata["valid_caches"]:
		print "Pulling for '"+i+"'...",
		server.cachedata["name_mappings"][i]=get_name(i)
		print "Name="+server.cachedata["name_mappings"][i]
	server.save_cachedata()

if __name__=="__main__":
	if len(sys.argv)>1:
		eval(sys.argv[1])()
	else:
		print "Pass a function to execute"
