#!/usr/bin/env python

import argparse
import os
import subprocess
import yaml
import time
import sys

#################################

class cloud:
	def __init__(self, platform="aws"):
		self.platform = platform


class aws(cloud):

	def checkSoftware(self):
		missingAWS = subprocess.call(['which aws'], shell=True, stdout=subprocess.PIPE)
		# this will resolve to 0 if the AWS CLI is installed
		if missingAWS == True:
			sys.exit("\033[1m" + "Error: The AWS Command Line Interface is not installed or not in your PATH.  Please refer to the AWS documentation for the installation instructions for your system." + "\033[0m")


	def configureCLI(self):
		if yamlPar["instance-creation"]["aws-credentials"]["generate-configuration"] == True:
			subprocess.call(['echo "[default]" > ~/.aws/testconfig'], shell=True)
			textCommand = 'echo "region = ' + yamlPar["instance-creation"]["aws-credentials"]["default-region"] + ' " >> ~/.aws/testconfig'
			subprocess.call([textCommand], shell=True)
			# write the two-line 'config' file setting the default region to be used throughout

			subprocess.call(['echo "[default]" > ~/.aws/testcredentials'], shell=True)
			textCommand = 'echo "aws_access_key_id = ' + yamlPar["instance-creation"]["aws-credentials"]["key-id"] + ' " >> ~/.aws/testcredentials'
			subprocess.call([textCommand], shell=True)
			textCommand = 'echo "aws_secret_access_key = ' + yamlPar["instance-creation"]["aws-credentials"]["secret-key"] + ' " >> ~/.aws/testcredentials'
			subprocess.call([textCommand], shell=True)

	def checkConfig(self):
		missingConf = subprocess.call(['aws configure get aws_access_key_id'], shell=True, stdout=subprocess.PIPE)
		# this will resolve to 0 if there is a key in the configuration file
		if missingConf == True:
			sys.exit("\033[1m" + "AWS CLI is not configured.  Please ensure the YAML file includes your AWS credentials." + "\033[0m")
			# be sure that the CLI is configured, either through the above block or through previous settings

	def requestInstances(self):
		instanceCreate = 'aws ec2 run-instances --image-id ' + yamlPar["instance-creation"]["cli-parameters"]["ami-id"] + ' --count ' + str(yamlPar["instance-creation"]["cli-parameters"]["instance-number"]) + ' --instance-type ' + yamlPar["instance-creation"]["cli-parameters"]["instance-type"] + ' --key-name ' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ' --security-group-ids ' + yamlPar["instance-creation"]["cli-parameters"]["security-group-id"]
		# generate the command to instantiate the instances in accordance with YAML specifications
		subprocess.call([instanceCreate], shell=True, stdout=subprocess.PIPE)
		print "Instances have been successfully requested and are presently instantiating."
		print "Execution will now pause for 3 minutes to be sure all instances are active."
		print "Their status can be viewed in the web console at this point."
		time.sleep(180)

	def spotRequest(self):
		instanceCreate = 'aws ec2 request-spot-instances --spot-price 0.007 --instance-count ' + str(yamlPar["instance-creation"]["cli-parameters"]["instance-number"]) + ' --launch-specification \"{\\\"KeyName\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + '\\\", \\\"ImageId\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["ami-id"] + '\\\", \\\"InstanceType\\\": \\\"' + yamlPar["instance-creation"]["cli-parameters"]["instance-type"] + '\\\", \\\"SecurityGroupIds\\\": [\\\"' + yamlPar["instance-creation"]["cli-parameters"]["security-group-id"] + '\\\"]}\"'
		# generate the command to instantiate the instances in accordance with YAML specifications
		subprocess.call([instanceCreate], shell=True, stdout=subprocess.PIPE)
		print "Spot instances have been successfully requested and are presently instantiating."
		print "Execution will now pause for 3 minutes to be sure all instances are active."
		print "Their status can be viewed in the web console at this point."
		time.sleep(180)

	def kill(self):
		if arguments.kill:
			print "All instances in the region specified in the YAML file will now be deactivated.  Execution will pause for 30 seconds to give you a chance to cancel (ctrl+c) if that is not desired.  Once that time elapses, this operation is irreversible."
			time.sleep(30)
			subprocess.call(['aws ec2 describe-instances | grep InstanceId | awk \'{print $2}\' | awk -F\'\"\' \'{ print $2 }\' | xargs aws ec2 terminate-instances --instance-ids'], shell=True, stdout=subprocess.PIPE)
			sys.exit("Resources are now being deactivated.  Execution will now terminate.  Spin-down status can be monitored from the console and will take approximately one minute.")

	def getIPs(self):
		subprocess.call(['aws ec2 describe-instances   --query "Reservations[*].Instances[*].PublicIpAddress"   --output=text > ips.txt'], shell=True)
		# use the AWS CLI to retrieve the list of IPs in the default region
		subprocess.call(['tr "\t" "\n" < ips.txt > ips_newline.txt'], shell=True)
		# split the raw output onto separate lines

	def manageKey(self):
		keyLocation = yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-path"] + '/' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ".pem"
		# store the full filepath of the keyfile for convenience due to length of expression
		print("Making sure the keyfile's permissions are correctly set...")
		if yamlPar["instance-creation"]["user-platform"] == "osx":
			keyPermissions = subprocess.check_output(['stat -f \'%A %a %N\' ' + keyLocation], shell=True)
		elif yamlPar["instance-creation"]["user-platform"] == "linux":
			keyPermissions = subprocess.check_output(['stat -c \'%a %n\' ' + keyLocation], shell=True)
		# check permissions of the keyfile
		if int(keyPermissions[:3]) != 400:
			# keyfile must have these exact permissions or the connection will be declined by AWS
			subprocess.call(['chmod 400 ' + keyLocation], shell=True)
			print("Attempting to change permissions to read-only...")
			if yamlPar["instance-creation"]["user-platform"] == "osx":
				keyPermissions = subprocess.check_output(['stat -f \'%A %a %N\' ' + keyLocation], shell=True)
			elif yamlPar["instance-creation"]["user-platform"] == "linux":
				keyPermissions = subprocess.check_output(['stat -c \'%a %n\' ' + keyLocation], shell=True)
		# check again to see if update was successful with syntax based on user platform
		if int(keyPermissions[:3]) != 400:
			sys.exit("Error: Key permissions incorrect even after an attempt to modify them, likely due to inadequate user access level.  Unable to proceed.  Please contact your system administrator for assistance.")
		else:
			print("Permissions are already correct - proceeding.")
		print("Done verifying permissions.")


parser = argparse.ArgumentParser(description='Uses a YAML file to deploy a designated number of Jupyter instances on AWS according to user specifications.  Please visit http://placeholder for a thorough explanation of the YAML file\'s format.')
parser.add_argument('-y', '--yaml', type=str, required = True, help = 'The YAML configuraton file')
parser.add_argument('--kill', help = 'Deactivates all resources', action="store_true")


arguments = parser.parse_args()

################ Begin parsing of YAML

yamlPar = yaml.load(open(arguments.yaml))

################ Check dependencies



run = aws()
run.checkSoftware()
run.configureCLI()
run.checkConfig()
run.kill()
if "spot" in yamlPar["instance-creation"]["cli-parameters"]:
	run.spotRequest()
else:
	run.requestInstances()
run.getIPs()
run.manageKey()


# TODO: ADD MANUAL CONFIRMATION ASKING WHETHER OR NOT TO PROCEED IF NUMBER OF REGISTRANTS IS GREATER THAN THE NUMBER OF INSTANCES




################ Configure AWS CLI (optional step)


	# write the three-line 'credentials' file setting the default key id and associated secret key (see walkthough for more information)

if yamlPar["instance-creation"]["aws-credentials"]["generate-configuration"] == False:
	print(yamlPar["instance-creation"]["nonsense"]["garbage"])



################## KILL RESOURCES IF TOLD TO DO SO (must wait for CLI to be configured first just in case a new computer is being used)





# wait for 3 minutes so the instances can come fully online







print("Deploying Jupyter...")
ipFile = open("ips_newline.txt",'r')
for ip in ipFile:
# loop over the IP file and perform steps on each IP
	ip = ip.strip('\n')
	# must strip() the trailing newlines to correctly execute the batch command
	if yamlPar["instance-creation"]["instance-configuration"]["verbosity"] == True:
		print(ip)
		# if verbose, print the IP so user can track the process
	bashCommand = 'ssh -oStrictHostKeyChecking=no -o \"UserKnownHostsFile /dev/null\" -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@' + ip + ' "screen -dm bash -c \''+ yamlPar["instance-creation"]["instance-configuration"]["conda-path"] +'/jupyter notebook\'"'
	# assemble the command to access each IP and activate Jupyter in a detached screen
	# do not add to UserKnownHostsFile because eventually an IP will be reused and your computer will erroneously flag it as a man-in-the-middle attack
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

############## Set up logging
if yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"] > 0:
# setting the interval to 0 will disable logging
	subprocess.call(['echo "#!/bin/bash" > screen_check.sh'], shell=True)
	subprocess.call(['echo "for IP_ADDRESS in \`cat ips_newline.txt\` ; do" >> screen_check.sh'], shell=True)
	bashCommand = 'echo \"' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS}\"'
	subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
	bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS} \"screen -ls\"'
	subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
	subprocess.call(['echo "done" >> screen_check.sh'], shell=True)
	# use the YAML parameters to write a bash script that logs into each IP and lists the active screens
	#subprocess.call(['echo "*/' + str(yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"]) + ' * * * * bash `pwd`/screen_check.sh >> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt 2>&1" > fake_crontab.txt'], shell=True)
	cronCommand = 'echo \"*/' + str(yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"]) + ' * * * * bash `pwd`/screen_check.sh >> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt 2>&1\"'
	try:
   		 	cronCheck = subprocess.check_output(['crontab -l'], shell=True)
	except subprocess.CalledProcessError as error:
    		cronCheck = "no crontab"
    	# ridiculous hack because checking for a crontab when there is none returns nonzero exit code so it works but then breaks immediately after
    	# also it is bugged and requires double indentation for some reason
	if "no crontab" in cronCheck:
		subprocess.call([cronCommand + ' | crontab -'], shell=True)
	else:
		subprocess.call(['(crontab -l && ' + cronCommand + ') | crontab -'], shell=True)
	# set up a cron job to run the script at the desired interval (TODO: fix this to base its location on the system - need to figure out where mac crontab goes first)


awkCommand = 'awk \'$0=$0":' + str(yamlPar["instance-creation"]["instance-configuration"]["jupyter-port"]) + '"\' ' + "ips_newline.txt" + ' > ips_newline_port.txt'
# assemble the command to append the Jupyter port to the IPs
subprocess.call([awkCommand], shell=True)

subprocess.call(['rm ips.txt'], shell=True)
# remove intermediary files

if yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["generate-directory"] == True:
	num_lines = sum(1 for line in open(yamlPar["instance-creation"]["instance-configuration"]["directory-parameters"]["user-list"]))
	if num_lines > yamlPar["instance-creation"]["cli-parameters"]["instance-number"]:
			sys.exit("\033[1m" + "Warning: Insufficient instances for all participants.  Exiting without generating directory." + "\033[0m")
	
	subprocess.call(['bash generate_directory.sh > user_directory.html'], shell=True)
# call the script that builds the html directory


