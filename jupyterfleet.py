import argparse
import os
import subprocess
import yaml
import time

parser = argparse.ArgumentParser(description='Process YAML file containing options.')
parser.add_argument('-y', '--yaml', type=str, required = True)
#parser.add_argument('-i', '--ip', type=str, required = True)
# This argument is just for testing - the full program will generate it internally

arguments = parser.parse_args()

subprocess.call(['echo "hello world with bash"'], shell=True)

print "Our file is %s." % arguments.yaml

################ Check dependencies





################ Begin parsing of YAML

yamlPar = yaml.load(open(arguments.yaml))


instanceCreate = 'aws ec2 run-instances --image-id ' + yamlPar["instance-creation"]["cli-parameters"]["ami-id"] + ' --count ' + str(yamlPar["instance-creation"]["cli-parameters"]["instance-number"]) + ' --instance-type ' + yamlPar["instance-creation"]["cli-parameters"]["instance-type"] + ' --key-name ' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ' --security-group-ids ' + yamlPar["instance-creation"]["cli-parameters"]["security-group-id"]
# generate the command to instantiate the instances in accordance with YAML specifications
subprocess.call([instanceCreate], shell=True)


print "Execution will now pause for 3 minutes to be sure all instances are active."
print "Their status can be viewed in the web console at this point."
time.sleep(180)
# wait for 3 minutes so the instances can come fully online





subprocess.call(['aws ec2 describe-instances   --query "Reservations[*].Instances[*].PublicIpAddress"   --output=text > ips.txt'], shell=True)
# use the AWS CLI to retrieve the list of IPs in the default region
subprocess.call(['tr "\t" "\n" < ips.txt > ips_newline.txt'], shell=True)
# split the raw output onto separate lines


keyLocation = yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-path"] + '/' + yamlPar["instance-creation"]["cli-parameters"]["keyfile"]["key-name"] + ".pem"
# store the full filepath of the keyfile for convenience due to length of expression

ipFile = open("ips_newline.txt",'r')
for ip in ipFile:
	ip = ip.strip('\n')
	# must strip() the trailing newlines to correctly execute the batch command
	if yamlPar["instance-creation"]["instance-configuration"]["verbosity"] == True:
		print(ip)
		# if verbose, print the IP so user can track the process
	bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@' + ip + ' "screen -dm bash -c \''+ yamlPar["instance-creation"]["instance-configuration"]["conda-path"] +'/jupyter notebook\'"'
	# assemble the command to access each IP and activate Jupyter in a detached screen
	subprocess.call([bashCommand], shell=True)
	if yamlPar["instance-creation"]["instance-configuration"]["logging"]["wait"] == True:
		print("Waiting 120 seconds to be sure the screen will persist...")
		time.sleep(120)
		bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@' + ip + ' "screen -ls"'
		subprocess.call([bashCommand], shell=True)


############## Set up logging
if yamlPar["instance-creation"]["instance-configuration"]["logging"]["cron-interval"] > 0:
	subprocess.call(['echo "#!/bin/bash" > screen_check.sh'], shell=True)
	subprocess.call(['echo "for IP_ADDRESS in \`cat ips_newline.txt\` ; do" >> screen_check.sh'], shell=True)
	bashCommand = 'echo \"' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS}\"'
	subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
	bashCommand = 'ssh -oStrictHostKeyChecking=no -i ' + keyLocation + ' ' + yamlPar["instance-creation"]["instance-configuration"]["username"] + '@\${IP_ADDRESS} \"screen -ls\"'
	subprocess.call(['echo ' + bashCommand + ' >> screen_check.sh'], shell=True)
	subprocess.call(['echo "done" >> screen_check.sh'], shell=True)
	subprocess.call(['echo "*/10 * * * * bash `pwd`/screen_check.sh >> ' + yamlPar["instance-creation"]["instance-configuration"]["logging"]["log-directory"] + '/cron_screen_log.txt 2>&1" > fake_crontab.txt'], shell=True)
	


awkCommand = 'awk \'$0=$0":' + str(yamlPar["instance-creation"]["instance-configuration"]["port"]) + '"\' ' + "ips_newline.txt" + ' > ips_newline_port.txt'
# assemble the command to append the Jupyter port to the IPs
subprocess.call([awkCommand], shell=True)

subprocess.call(['rm ips.txt'], shell=True)
# remove intermediary files

#subprocess.call(['bash generate_directory.sh > user_directory.html'], shell=True)
# call the script that builds the html directory


