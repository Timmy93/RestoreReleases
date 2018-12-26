
import requests
import json
import time
import random

class ApiHandler:
	def __init__(self, username, apiSite, tokenPath, loggingHandler):
		self.username = username
		self.apiSite = apiSite
		self.tokenPath = tokenPath
		self.logging = loggingHandler
		#Read token
		self.readToken()
	
	res = {
		"ONLINE":"Files already online",
		"WAIT":"Wait before next refresh",
		"RESTORING":True,
		"ALREADY_REQ":"Link already requested"
	}

	#Read the token from the given url
	def readToken(self):
		file = open(self.tokenPath, "r")
		if not file:
			self.logging.error('Token file not read - Cannot execute any request')
			exit()
		self.token = file.read().strip()
		self.logging.info('Token read from file')

	#Request the available genres
	def getGenres(self):
		req = "generi"
		r = requests.post(self.apiSite, data = {'user':self.username, 'psw':self.token, 'req':req})
		return json.loads(r.text)
	
	#Retrieve the list of all releases from the server		
	def getAllReleases(self):
		self.logging.info('Requested all releases')
		req = "get_all_releases"
		r = requests.post(self.apiSite, data = {'user':self.username, 'psw':self.token, 'req':req})
		return json.loads(r.text)
	
	#Creates the dictionaries
	def manageReleases(self):
		self.toRestore = {}
		all_rel = self.getAllReleases()
		#Creates a list of all releases ignoring the genre
		for genre in all_rel:
			for account in all_rel[genre]:
				#Creates array in the dictionary if needed
				try:
					dic = self.toRestore[account]
				except KeyError:
					self.logging.info("Generated key in library for: "+account)
					self.toRestore[account] = []
				
				#Populate dictionary
				for release in all_rel[genre][account]:
					self.toRestore[account].append(release)
		
		#Log the account to check
		for account in self.toRestore:
			now = len(self.toRestore[account])
			self.logging.info("Account: "+account+" - To check "+str(now)+" releases")
	
	#Restore a single release
	def restoreRelease(self, code):
		self.logging.debug('Request restore: '+str(code))
		req = "refresh_1f"
		r = requests.post(self.apiSite, data = {'code':code, 'user':self.username, 'psw':self.token, 'req':req})
		return json.loads(r.text)
		
	#Start restoring all until I can only wait
	def restoreAll(self):
		cloneToRestore = self.toRestore.copy()
		#Iterate over all account
		for account in cloneToRestore:
			
			# ~ #Control only 1 account
			# ~ if not (account == "iceupload-222@yahoo.it"):
				# ~ print("Skip: "+account)
				# ~ continue
			
			now = len(self.toRestore[account])
			print("START: Account: "+account+" - To check "+str(now)+" releases")
			#Create initial copy and iterate over it
			new_list = self.toRestore[account].copy()
			#Iterate over all the releases
			for code in new_list:
				#Measure time
				start_time = time.time()
				
				try:
					resp = self.restoreRelease(code)

					if resp == self.res["ONLINE"]:
						self.logging.debug('Already online: '+str(code))
						self.removeObject(account, code)
					elif resp == self.res["WAIT"]:
						#Exit from this loop and not remove the object!
						self.logging.debug('Wait before new request: '+str(code)+'\nExit from loop')
						break
					elif self.res["RESTORING"]:
						print("Restoring: "+str(code))
						self.logging.info('Restore succesfully request of: '+str(code))
						self.removeObject(account, code)
					elif resp == self.res["ALREADY_REQ"]:
						print("Already requested: "+str(code))
						self.logging.warning('Unexpected: Restore already requested of: '+str(code))
						self.removeObject(account, code)
				except:
					print("Problem restoring release: "+str(code))
					self.logging.error("Problem restoring release: "+str(code))
				
				print(str(random.randrange(0, 1000)/1000))
				time.sleep(random.randrange(0, 1000)/1000)
				
			after = len(self.toRestore[account])
			print("STOP: Account: "+account+" - To check "+str(after)+" releases")
			#Remove empty dictionaries
			if not after:
				lib_bef = len(self.toRestore)
				print(account+" removed")
				self.toRestore.pop(account, None)
				lib_aft = len(self.toRestore)
				self.logging.info("Removed account: "+account+" - Before: "+str(lib_bef)+' elem - After: '+str(lib_aft))
			else:
				print("There are still "+str(after)+" elements for account: "+account)
			
			
	# Remove an object from the original library
	def removeObject(self, account, item):
		self.logging.debug('Remove: '+str(item)+' from '+account)
		elem_before = len(self.toRestore[account])
		self.toRestore[account].remove(item)
		elem_after = len(self.toRestore[account])
		self.logging.debug('-->Before: '+str(elem_before)+' Now: '+str(elem_after))
	
	#Return the count of left objects
	def countObjectLeft(self):
		numElem = 0
		for account in self.toRestore:
			numElem += len(self.toRestore[account])
		return numElem
	
