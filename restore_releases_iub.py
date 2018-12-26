#!/usr/bin/env python3
import os
import errno
import re
import time
import logging
import yaml
from ApiHandler import ApiHandler

#Check if the given path is an absolute path
def createAbsolutePath(path):
	if not os.path.isabs(path):
		currentDir = os.path.dirname(os.path.realpath(__file__))
		path = os.path.join(currentDir, path)
		
	return path

def main():
	configFile = "config.yml"
	logFile = "restore_releases.log"
	#Set logging file
	logging.basicConfig(filename=createAbsolutePath(logFile),level=logging.ERROR,format='%(asctime)s %(levelname)-8s %(message)s')
	#Load config
	with open(createAbsolutePath(configFile), 'r') as stream:
		try:
			config = yaml.load(stream)
			#Info for m3u file
			username = config['Settings']['username']
			tokenPath = createAbsolutePath(config['Settings']['tokenPath'])
			url = config['Settings']['urlHandler']
			logLevel = config['Settings']['logLevel']
			seconds = config['Settings']['waitSeconds']
			logging.getLogger().setLevel(logLevel)
			logging.info('Loaded settings started')
		except yaml.YAMLError as exc:
			print("Cannot load file: ["+configFile+"] - Error: "+exc)
			logging.error("Cannot load file: ["+configFile+"] - Error: "+exc)
			exit()

	#Creates handler to send request to the backend site
	handler = ApiHandler(username, url, tokenPath, logging)

	print("Initial request of releases");
	handler.manageReleases()
	logging.info("Obtained releases to check")
	
	for i in range(30):
		print("ITERATION "+str(i)+" - Restore all!")
		handler.restoreAll();
		logging.info("Started restoring iteration #"+str(i))
		if handler.countObjectLeft():
			#There are still object wait
			logging.info("Started to wait "+str(seconds)+" before next restore round")
			time.sleep(seconds)
		else:
			break

	logging.info('STOP - Element left: '+str(handler.countObjectLeft()))

main()
