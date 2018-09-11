#!/usr/bin/env python

import argparse
import os
import subprocess
import yaml
import time
import sys
import datetime

#################################

class cloud:
	def __init__(self, platform="aws"):
		self.platform = platform
		

	def createTable(self):
		"""Create a textfile with pastable links to the Jupyter instances in the form 'ip:port'

		Uses file(s):
			'ips_newline.txt'

		Creates file(s):
			'ips_newline_port.txt'

		Removes file(s):
			'ips.txt'

		"""
		awkCommand = 'awk \'$0=$0":' + str(yamlPar["instance-creation"]["instance-configuration"]["jupyter-port"]) + '"\' ' + "ips_newline.txt" + ' > ips_newline_port.txt'
		subprocess.call([awkCommand], shell=True)
		subprocess.call(['rm ips.txt'], shell=True)

	def createDirectory(self):
		"""Create an HTML user directory matching each user to an IP and displaying any extra instances as 'unassigned'

		This function will abort if there are not enough instances for all participants, as there is no way to predict user priority

		This HTML file can then be pushed directly to any website and will let users access their instances by clicking a link


		Uses file(s):
			The 'user-list' file denoted in the YAML
			'generate_direcrtory.sh'
			'ips_newline_port.txt'

		Creates file(s):
			'user_directory.html'

		Removes file(s):
			N/A
			
		"""
		if yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["generate-directory"] == True:
			if os.path.exists(yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["user-list"]):
				num_lines = sum(1 for line in open(yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["user-list"]))
				if num_lines > yamlPar["instance-creation"]["cli-parameters"]["instance-number"]:
					sys.exit("\033[1m" + "Warning: Insufficient instances for all participants.  Exiting without generating directory." + "\033[0m")
				subprocess.call(["cp " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["user-list"] + " registration_tiny.csv"], shell=True)
				bashCommand = "bash generate_directory.sh " + str(yamlPar["instance-creation"]["instance-configuration"]["jupyter-password"]) + " > user_directory.html"
				subprocess.call([bashCommand], shell=True)
			else:
				print("\033[1m" + "Error: No user list found under the specified filename.  Skipping directory generation.  Instances are still active." + "\033[0m")

			if "push-repo" in yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]:
				subprocess.call(['cp user_directory.html ' + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + "/" + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-subfolder"]], shell=True)
				gitCommand = "git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " add -A && git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " commit -m \"JupyterFleet directory autopushed\" && git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " push origin master"
				subprocess.call([gitCommand], shell=True)



	def timer(self, length):
		"""Creates an in-line countdown timer for long processes.  The countdown will be displayed at an interval determined by the total time.
		"""
		totalTime = length
		if totalTime >= 600:
			interval = 60
		elif totalTime > 180:
			interval = 30
		else:
			interval = 15
		sys.stdout.write('Execution will resume in: ' + str(totalTime) + ' ')
		sys.stdout.flush()
		for i in xrange(totalTime-interval,0-interval,-interval):
    			time.sleep(interval)
    			sys.stdout.write(str(i) + ' ')
    			sys.stdout.flush()
		sys.stdout.write('\n')




class aws(cloud):

	def checkSoftware(self):
		"""Check to see if the AWS CLI tool (the only current software dependency) is in the user's PATH

		Execution will be terminated if it is not found, as it is needed for this software to interact with AWS

		"""
		missingAWS = subprocess.call(['which aws'], shell=True, stdout=subprocess.PIPE)
		if missingAWS == True:
			sys.exit("\033[1m" + "Error: The AWS Command Line Interface is not installed or not in your PATH.  Please refer to the AWS documentation for the installation instructions for your system." + "\033[0m")


	def configureCLI(self):
		"""Configure the AWS CLI using the parameters specified in the YAML'

		Existing configuration files will be overwritten using the YAML's parameters if this function is called

		Uses file(s):
			None

		Creates file(s):
			~/.aws/config
			~/.aws/credentials

		Removes file(s):
			None
			
		"""
		if yamlPar["instance-creation"]["aws-credentials"]["generate-configuration"] == True:
			subprocess.call(['echo "[default]" > ~/.aws/config'], shell=True)
			textCommand = 'echo "region = ' + yamlPar["instance-creation"]["aws-credentials"]["default-region"] + ' " >> ~/.aws/config'
			subprocess.call([textCommand], shell=True)
			# write the two-line 'config' file setting the default region to be used throughout

			subprocess.call(['echo "[default]" > ~/.aws/credentials'], shell=True)
			textCommand = 'echo "aws_access_key_id = ' + yamlPar["instance-creation"]["aws-credentials"]["key-id"] + ' " >> ~/.aws/credentials'
			subprocess.call([textCommand], shell=True)
			textCommand = 'echo "aws_secret_access_key = ' + yamlPar["instance-creation"]["aws-credentials"]["secret-key"] + ' " >> ~/.aws/credentials'
			subprocess.call([textCommand], shell=True)

	def checkConfig(self):
		"""Check to see if the CLI is configured (i.e. if the last step worked)

		If this function causes execution to break, the configuration files were not created, likely due to a permissions issue

		"""
		missingConf = subprocess.call(['aws configure get aws_access_key_id'], shell=True, stdout=subprocess.PIPE)
		# this will resolve to 0 if there is a key in the configuration file
		if missingConf == True:
			sys.exit("\033[1m" + "AWS CLI is not configured.  Please ensure the YAML file includes your AWS credentials." + "\033[0m")


	def prepareBlacklist(self):
		"""Blacklist all extant instances (if requested in the YAML)

		Also generates a list of all existing EC2 ids for use with kill()
		"""
		if(yamlPar["instance-creation"]["blacklist"]["blacklist-type"] == "automatic"):
			subprocess.call(['aws ec2 describe-instances   --query "Reservations[*].Instances[*].PublicIpAddress"   --output=text > blacklist.txt'], shell=True)
			subprocess.call(['tr "\t" "\n" < blacklist.txt > blacklist_newline.txt'], shell=True)
			subprocess.call(["rm blacklist.txt"], shell=True)

			subprocess.call(["aws ec2 describe-instances | grep InstanceId | awk \'{print $2}\' | awk -F\'\"\' \'{ print $2 }\' > preexisting_ids.txt"], shell=True)



	def requestInstances(self):
		"""Request on-demand EC2 instances of the type specified in the YAML

		Once the instances are requested, excecution will pause for 3 minutes so they can fully come online

		"""
		instanceCreate = 'aws ec2 run-instances --image-id ' + yamlPar["instance-creation"]["cli-parameters"]["ami-id"] + ' --count ' + str(yamlPar["instance-creation"]["cli-parameters"]["instance-number"]) + ' --instance-type ' + yamlPar["instance-creation"]["cli-parameters"]["instance-type"] + ' --key-name ' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ' --security-group-ids ' + yamlPar["instance-creation"]["cli-parameters"]["security-group-id"]
		subprocess.call([instanceCreate], shell=True, stdout=subprocess.PIPE)
		print "Instances have been successfully requested and are presently instantiating."
		print "Execution will now pause for 3 minutes to be sure all instances are active."
		print "Their status can be viewed in the web console at this point."
		run.timer(180)
		#time.sleep(180)

	def spotRequest(self):
		"""Request spot EC2 instances of the type specified in the YAML

		TODO: ADD DOCUMENTATION FOR FALLBACK PROCEDURES ONCE THEY ACTUALLY EXIST

		"""
		subprocess.call(["osascript -e \'display notification \"Spots have been requested\" with title \"JupyterFleet\" subtitle \"JupyterFleet Alert\"\'"], shell=True)
		instanceCreate = 'aws ec2 request-spot-instances --spot-price ' + str(yamlPar["instance-creation"]["cli-parameters"]["spot"]["spot-price"]) + ' --instance-count ' + str(yamlPar["instance-creation"]["cli-parameters"]["instance-number"]) + ' --launch-specification \"{\\\"KeyName\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + '\\\", \\\"ImageId\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["ami-id"] + '\\\", \\\"InstanceType\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["instance-type"] + '\\\", \\\"SecurityGroupIds\\\": [\\\"' + yamlPar["instance-creation"]["cli-parameters"]["security-group-id"] + '\\\"]}\"'
		# generate the command to instantiate the instances in accordance with YAML specifications
		resultString = subprocess.call([instanceCreate], shell=True, stdout=subprocess.PIPE)
		if resultString == 0: # if there is no error with the spot request command
			print "Spot instances have been successfully requested and are presently instantiating."
			print "Execution will now pause for " + str(yamlPar["instance-creation"]["cli-parameters"]["spot"]["wait-time"]) + " minutes to be sure all instances are active."
			print "Their status can be viewed in the web console at this point."
			#time.sleep(int(yamlPar["instance-creation"]["cli-parameters"]["spot"]["wait-time"]) * 60)
			run.timer(int(yamlPar["instance-creation"]["cli-parameters"]["spot"]["wait-time"]) * 60)

			if yamlPar["instance-creation"]["cli-parameters"]["spot"]["fallback"] == True:
				lengthBase = int(yamlPar["instance-creation"]["cli-parameters"]["instance-number"])
				lengthCheck = int(subprocess.check_output(['aws ec2 describe-spot-instance-requests --filters Name=state,Values=active | grep "Your spot request is fulfilled." | wc -l'], shell=True))
				allActive = (lengthBase == lengthCheck)
				# check if all requested spot instances have actually been generated (i.e. see if the number of spot requests marked 'active' is the same as the number requested)
				priceCheck = int(subprocess.check_output(['aws ec2 describe-spot-instance-requests --query SpotInstanceRequests[*].{Status:*} | grep "price-too-low" | wc -l'], shell=True))
				if(priceCheck) > 0:
					print("Your bid was too low to be filled.  Now deleting all spot requests...")
					subprocess.call(['aws ec2 describe-spot-instance-requests --query "SpotInstanceRequests[*].SpotInstanceRequestId" --output=text > sirfile.txt'], shell=True)
					subprocess.call(['tr "\t" "\n" < sirfile.txt > sirfile_newline.txt'], shell=True)
					subprocess.call(['rm sirfile.txt'], shell=True)
					sir = open("sirfile_newline.txt",'r')
					for entry in sir:
						entry = entry.strip('\n')
						bashCommand = 'aws ec2 cancel-spot-instance-requests --spot-instance-request-id ' + entry + ''
						with open(os.devnull, "w") as f:
							subprocess.call([bashCommand], shell=True, stdout=f)
						print("deleted %s") % entry
					subprocess.call(["rm sirfile_newline.txt"], shell=True)






					print("Invoking contingency settings...")
					if yamlPar["instance-creation"]["cli-parameters"]["spot"]["contingency-type"] == "on-demand":
						print("Using on-demand instances instead of spot instances...")
						run.requestInstances()
					elif yamlPar["instance-creation"]["cli-parameters"]["spot"]["contingency-type"] == "continue":
						print("Continuing with whatever instances did spawn...")
					elif yamlPar["instance-creation"]["cli-parameters"]["spot"]["contingency-type"] == "abort":
						sys.exit("Aborting run [manually kill everything for now]")
		elif resultString == 255: # the error code for a bid that is so low it is invalid
			sys.exit("Please increase the bid and retry.  No instances have been generated.")



	def kill(self):
		"""Kill all instances in the default region"""

		# TODO: MAKE THIS FUNCTION MORE CONTROLLABLE, WITH TEXT VALIDATION INSTEAD OF WAITING, EXITING WITHOUT KILLING OTHERWISE
		if arguments.kill:
			print "All instances in the region specified in the YAML file will now be deactivated.  Execution will pause for 30 seconds to give you a chance to cancel (ctrl+c) if that is not desired.  Once that time elapses, this operation is irreversible."
			time.sleep(30)
			subprocess.call(['aws ec2 describe-instances | grep InstanceId | awk \'{print $2}\' | awk -F\'\"\' \'{ print $2 }\' > all_instance_ids.txt'], shell=True)
			idFile = open("all_instance_ids.txt", "r")
			idList = idFile.readlines()

			filteredFile = open("ids_to_delete.txt","w") 
			for i in idList:
				subprocessCommand = "grep -c \'" + str(i).strip() + "\' preexisting_ids.txt"
				print(subprocessCommand)
				try:
			   		output = subprocess.check_output([subprocessCommand], shell=True)
			   		#print("BLACKLISTED")
				except subprocess.CalledProcessError:                                                                                                   
			   		#print("OK")
			   		filteredFile.write(i)
			filteredFile.close()
			idFile.close()
			subprocess.call(["rm all_instance_ids.txt preexisting_ids.txt"], shell=True)
			subprocess.call(["cat ids_to_delete.txt | xargs aws ec2 terminate-instances --instance-ids"], shell=True)
			#subprocess.call(['aws ec2 describe-instances | grep InstanceId | awk \'{print $2}\' | awk -F\'\"\' \'{ print $2 }\' | xargs aws ec2 terminate-instances --instance-ids'], shell=True, stdout=subprocess.PIPE)
			# terminate instances
			
			print "Archiving all intermediary files..."
			currentTime = datetime.datetime.now().strftime(("%Y-%m-%d_%H:%M"))
			archivePath = 'jupyterfleet_archive_' + str(currentTime)
			subprocess.call(['mkdir ' + archivePath], shell=True)
			subprocess.call(['mv ips_newline* ' + archivePath], shell=True)
			subprocess.call(['mv cron_screen_log.txt ' + archivePath], shell=True)
			subprocess.call(['mv blacklist_newline.txt ' + archivePath], shell=True)
			subprocess.call(['mv ids_to_delete.txt ' + archivePath], shell=True)
			if os.path.exists('user_directory.html'):
				subprocess.call(['mv user_directory.html ' + archivePath], shell=True)
				# if a directory was generated, archive it
			if yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"] > 0:
				subprocess.call(['crontab -l | sed \$d | crontab -'], shell=True)
				# remove the last line of crontab if logging was enabled, since the logging command was added to the bottom of crontab
				subprocess.call(['mv screen_check.sh ' + archivePath], shell=True)
				# archive cron script

			if "push-repo" in yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]:
				# if a user directory was automatically pushed, delete it from github
				gitCommand = "rm " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + "/" + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-subfolder"] + "/user_directory.html && git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " add -A && git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " commit -m \"JupyterFleet directory autoremoved\" && git -C " + yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["push-repo"] + " push origin master"
				subprocess.call([gitCommand], shell=True)


			sys.exit("Resources are now being deactivated.  Execution will now terminate.  Spin-down status can be monitored from the console and will take approximately one minute.")

	def getIPs(self):
		"""Retrieve the IPs for each instance and store them in a file, with each IP on a separate line

		IPs will be retrieved for all active instances in the default region, by default including any previously extant

		Options permit the use of a blacklist, which can either be 'automatic' (all preexisting instances) or manual (IPs designated in a file)

		Uses file(s):
			None

		Creates file(s):
			'ips.txt'
			'ips_newline.txt'

		Removes file(s):
			None
			
		"""
		subprocess.call(['aws ec2 describe-instances   --query "Reservations[*].Instances[*].PublicIpAddress"   --output=text > ips.txt'], shell=True)
		subprocess.call(['tr "\t" "\n" < ips.txt > ips_newline.txt'], shell=True)
		# split the raw output onto separate lines



		ipFile = open("ips_newline.txt", "r")
		ipList = ipFile.readlines()

		filteredFile = open("filtered_ips_newline.txt","w") 
		for i in ipList:
			subprocessCommand = "grep -c \'" + str(i).strip() + "\' blacklist_newline.txt"
			#print(subprocessCommand)
			try:
		   		output = subprocess.check_output([subprocessCommand], shell=True)
		   		#print("BLACKLISTED")
			except subprocess.CalledProcessError:                                                                                                   
		   		#print("OK")
		   		filteredFile.write(i)
		# compare each IP to the blacklist, and save it if it's not in the blacklist
		filteredFile.close()
		ipFile.close()
		subprocess.call(["mv filtered_ips_newline.txt ips_newline.txt"], shell=True)		

		#if(yamlPar["instance-creation"]["blacklist"]["blacklist-type"] == "automatic"):
			# if a blacklist should be created automatically, generate that empty file
			#blacklistFile = open("blacklist_file.txt", "r")
		#else:
			#blacklistFile = open(yamlPar["instance-creation"]["blacklist"]["blacklist-file"], "r")







	def manageKey(self):
		"""Process the AWS keyfile and be sure it is usable

		This function checks the permissions of the keyfile and sees if they are '400' (user read only) as required by AWS

		If the permissions are wrong, it attempts to change them to be correct

		Finally, it verifies the change worked - if not, it aborts, as the instances will not be accessible

		Soon, a flag '--skip' will allow the user to skip right back here in the event that occurs

		"""
		#keyLocation = yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-path"] + '/' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ".pem"
		# store the full filepath of the keyfile for convenience due to length of expression
		if (os.path.exists(yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-path"]) == False):
			sys.exit("\033[1m" + "Fatal Error: Key directory not found.  Please make sure 'key-path' is specified correctly in the YAML." + "\033[0m")
		print("Making sure the keyfile's permissions are correctly set...")
		if yamlPar["instance-creation"]["user-platform"] == "osx":
			keyPermissions = subprocess.check_output(['stat -f \'%A %a %N\' ' + keyLocation], shell=True)
		elif yamlPar["instance-creation"]["user-platform"] == "linux":
			keyPermissions = subprocess.check_output(['stat -c \'%a %n\' ' + keyLocation], shell=True)
		# check permissions of the keyfile using system-specific syntax
		if int(keyPermissions[:3]) != 400:
			subprocess.call(['chmod 400 ' + keyLocation], shell=True)
			print("Attempting to change permissions to read-only...")
			if yamlPar["instance-creation"]["user-platform"] == "osx":
				keyPermissions = subprocess.check_output(['stat -f \'%A %a %N\' ' + keyLocation], shell=True)
			elif yamlPar["instance-creation"]["user-platform"] == "linux":
				keyPermissions = subprocess.check_output(['stat -c \'%a %n\' ' + keyLocation], shell=True)
		# check again to see if update was successful using the same syntax
		if int(keyPermissions[:3]) != 400:
			sys.exit("Error: Key permissions incorrect even after an attempt to modify them, likely due to inadequate user access level.  Unable to proceed.  Please contact your system administrator for assistance.")
		else:
			print("Permissions are already correct - proceeding.")
		print("Done verifying permissions.")

	def startJupyter(self):
		"""ssh into each instance and initialize the Jupyter server

		This function loops over each IP in the 'ips_newline.txt' file to generate the activation command

		Jupyter is run in a detached screen to ensure it persists indefinitely

		"""
		print("Deploying Jupyter...")
		ipFile = open("ips_newline.txt",'r')
		for ip in ipFile:
			# loop over the IP file and perform steps on each IP
			ip = ip.strip('\n')
			# must strip() the trailing newlines to correctly execute the batch command
			if yamlPar["instance-creation"]["instance-configuration"]["verbosity"] == True:
				print(ip)
				# if verbose, print the IP so user can track the process
			bashCommand = 'ssh -q -oStrictHostKeyChecking=no -o \"UserKnownHostsFile /dev/null\" -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@' + ip + ' "screen -dm bash -c \''+ yamlPar["instance-creation"]["instance-configuration"]["conda-path"] +'/jupyter notebook\'"'
			# assemble the command to access each IP and activate Jupyter in a detached screen
			# do not add to UserKnownHostsFile because eventually an IP will be reused and your computer will erroneously flag it as a man-in-the-middle attack and break execution
			subprocess.call([bashCommand], shell=True)
			if yamlPar["instance-creation"]["instance-configuration"]["logging"]["wait"] == True:
				print("Waiting 120 seconds to be sure the screen will persist...")
				time.sleep(120)
				# wait 2 minutes to be sure the screen stays active - this setting is meant for testing and not production deployment due to how much time it takes
				bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@' + ip + ' "screen -ls"'
				subprocess.call([bashCommand], shell=True)
				# list running screens 
		time.sleep(15)
		print("Jupyter should now be active on all instances.  It is recommended to spot-check a few to validate this fact.")

	def createLogger(self):
		"""Configure instance logging that will periodically check screen status on each instance

		This function creates a bash script based on the YAML parameters, as cron needs a script to properly execute long looping commands

		The resulting cron job will list all active screens on all instances every X minutes as specified in the YAML

		TODO: Add a way to summarize this output to be reviewed in one glance without reading the long log file	

		Uses file(s):
			None

		Creates file(s):
			crontab file (if not extant)
			'screen_check.sh'
			'cron_screen_log.txt'

		Removes file(s):
			None

		"""
		if yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"] > 0:
		# setting the interval to 0 will disable logging
			#subprocess.call(['touch ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt'], shell=True)
			subprocess.call(['echo "#!/bin/bash" > screen_check.sh'], shell=True)
			fileCommand = '> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt'
			subprocess.call(['echo \"' + fileCommand + '\" > screen_check.sh'], shell=True)
			
			#scriptCommand = "osascript -e \\'display notification \\\"Spots are being requested\\\" with title \\\"JupyterFleet Alert\\\" subtitle \\\"Raw log re-generated\\\"\\'"
			# failed due to extra slash before single quotes
			scriptCommand = "osascript -e 'display notification \\\"Raw log re-generated\\\" with title \\\"JupyterFleet\\\" subtitle \\\"JupyterFleet Alert\\\"'"

			subprocess.call(['echo \"' + scriptCommand + '\" >> screen_check.sh'], shell=True)
			

			subprocess.call(['echo "for IP_ADDRESS in \`cat ' + workingDirectory +'/ips_newline.txt\` ; do" >> screen_check.sh'], shell=True)
			#bashCommand = 'echo \"' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS}\"'
			#subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
			bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS} \"screen -ls\"'
			subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
			subprocess.call(['echo "done" >> screen_check.sh'], shell=True)
			subprocess.call(['echo "echo \\"-----------------------------------------------------------\\"" >> screen_check.sh'], shell=True)
			subprocess.call(['echo "echo \\" \\" "  >> screen_check.sh'], shell=True)
			subprocess.call(['echo "echo \\" \\" "  >> screen_check.sh'], shell=True)
			subprocess.call(['echo "echo \\" \\" "  >> screen_check.sh'], shell=True)
			# use the YAML parameters to write a bash script that logs into each IP and lists the active screens
			#subprocess.call(['echo "*/' + str(yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"]) + ' * * * * bash `pwd`/screen_check.sh >> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt 2>&1" > fake_crontab.txt'], shell=True)
			cronCommand = 'echo \"*/' + str(yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"]) + ' * * * * bash `pwd`/screen_check.sh >> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt 2>&1\"'
			try:
   		 		cronCheck = subprocess.check_output(['crontab -l'], shell=True)
			except subprocess.CalledProcessError as error:
    				cronCheck = "no crontab"
    			# ridiculous hack because checking for a crontab when there is none returns nonzero exit code so it works but then breaks immediately after
    			# also it is bugged and requires double indentation on the above line (and only the above line) for some reason
			if "no crontab" in cronCheck:
				subprocess.call([cronCommand + ' | crontab -'], shell=True)
			else:
				subprocess.call(['(crontab -l && ' + cronCommand + ') | crontab -'], shell=True)
				# set up a cron job to run the script at the desired interval (TODO: fix this to base its location on the system - need to figure out where mac crontab goes first)



# "1 Socket"
# means Jupyter is running
# "No Sockets"
# means Jupyter is not running
# "Operation timed out"
# means the node is entirely down

#test = int(subprocess.check_output(['grep "1 Socket" cron_screen_log_backup.txt | wc -l'], shell=True))


#'wait' - use a while loop to check every 2 minutes
# Based on testing, if the price is too low it will never be filled, so this option would be pointless



#Fallback behavior (what to do if requests are not filled):
#'on-demand' - terminate unfilled requests and use on-demand instances to fill the rest of the slots
#'ignore' - proceed without all slots filled
#'abort' - spin-down instances and exit






# Create argument parser
parser = argparse.ArgumentParser(description='Uses a YAML file to deploy a designated number of Jupyter instances on AWS according to user specifications.  Please visit http://placeholder for a thorough explanation of the YAML file\'s format.')
parser.add_argument('-y', '--yaml', type=str, required = True, help = 'The YAML configuraton file')
parser.add_argument('--kill', help = 'Deactivates all resources', action="store_true")
parser.add_argument('--skip', help = 'Skip the spin-up steps and jump to Jupyter activation', action="store_true")

# Parse arguments
arguments = parser.parse_args()


# Begin parsing of YAML
yamlPar = yaml.load(open(arguments.yaml))
if "keyfile" in yamlPar["instance-creation"]["cli-parameters"]:
	keyLocation = yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-path"] + '/' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ".pem"



if  __name__ == "__main__":
	run = aws()
	workingDirectory = os.getcwd()
	if arguments.skip == False:
		run.checkSoftware()
		run.configureCLI()
		run.checkConfig()
		run.kill()
		if "blacklist" in yamlPar["instance-creation"]:
			run.prepareBlacklist()
		if "spot" in yamlPar["instance-creation"]["cli-parameters"]:
			run.spotRequest()
		else:
			run.requestInstances()
	run.getIPs()
	run.manageKey()
	run.startJupyter()
	run.createLogger()
	run.createTable()
	run.createDirectory()

