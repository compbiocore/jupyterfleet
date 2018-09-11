# YAML File Specifications

### Introduction to the YAML format

This tutorial concerns the creation of a YAML file to be read by JupyterFleet.  This file will specify all the parameters used to interact with AWS, as well as optionally aid in debugging and instance monitoring.

This tutorial will *not* address the creation of an AMI in any capacity, as JupyterFleet is designed to deploy an existing AMI.  If you are affiliated with Brown and need assistance in creating an AMI, please contact our help line.


**What is a YAML file?**

A YAML file is basically a configuration file that uses an indented, hierarchical structure to make it both human-readable and machine-readable in equal measure.  It allows all options for an entire piece of software to be specified in one place without having to type out a ten-line command on the command line that is difficult to read and annoying to edit.

YAML files can be formatted in a number of ways; the exact specifications for the YAML file that JupyterFleet can read are outlined below.  **A sample YAML file can be found** `here <https://raw.githubusercontent.com/compbiocore/jupyterfleet/master/example.yaml>`_ **(with credentials redacted).**  The entries that are feature descriptions in parentheses instead of values are not yet implemented so leaving them as is will not break anything.


### instance-creation


#### cloud-service


The 'cloud-service' option is used to designate which cloud service will be used to run Jupyter.  Only 'aws' is supported at this time, though others may be added in the future.


#### user-platform

The 'user-platform' option is used to specify the platform JupyterFleet itself is being run from - not the platform of the AMI.  This information is used to ensure the keyfile's permissions are correct and in a future build will also be used to configure logging in the event that you elect to enable logging, as platform determines the location of the crontab (system tool for running a task at a designated interval) configuration file.  Supported options are 'osx' for Mac OSX and 'linux' for Linux distributions.



#### aws-credentials


**generate-configuration**

The 'generate-configuration' option is used to designate whether JupyterFleet should configure the AWS Command Line Interface (CLI).  The CLI must be configured to use JupyterFleet, but this option can be set to FALSE if you have already configured the tool yourself.  Importantly, the default region must be set to the region in which the instances are to be deployed (and the AMI must be in that region too).  The rest of the options under 'aws-credentials' will only be used if 'generate-configuration' is set to TRUE.

**default-region**

The 'default-region' option is used to specify the region to be used in deploying the instances.  The AMI to be used must be available in this region.

**key-id**

The 'key-id' option is used to specify your AWS key ID.

**secrey-key**

The 'secret-key' option is used to specify your AWS key ID.



#### cli-parameters


**ami-id**

The 'ami-id' option is used to specify the AMI ID - *not* the AMI's name.  This ID can be found on the 'AMIs' page linked in the left toolbar on the main EC2 page.

Within that page, the AMI ID corresponding to your AMI of choice can be found in the column bearing that name.

**instance-type**

The 'instance-type' option is used to designate what type of EC2 instance to use.  A list of available instance types and their capabilities can be found on Amazon's `EC2 page <https://aws.amazon.com/ec2/instance-types/>`_.  We have found that the 't2.medium' instance type affords the best balance of cost and performance for an interactive workshop (as jobs that require significant memory will take too long to be demonstrated in this format), though the choice will necessarily be dictated by use case.

Please be mindful of the fact that each instance type is governed by its own instance limit, and be sure that the instance you've selected has a limit greater than or equal to the number of instances you plan to deploy.

**instance-number**

The 'instance-number' option is used to specify the number of instances - and thereby the number of notebooks - to instantiate.

**security-group-id**

The 'security-group-id' option is used to designate which security group to attach to the instances.  As in the case of 'ami-id', this option uses the security group's ID, not its name.  The security group ID can be found on the 'Security Groups' page linked in the left toolbar on the main EC2 page.


Within that page, the security group ID corresponding to your security group of choice can be found in the 'Group ID' column.


**keyfile**

*key-path*

The 'key-path' option is used to designate the location of the folder containing the .pem keyfile used to connect to AWS instances.  A keypair must first be created; this task can be performed by going into the 'Keypairs' page using the left toolbar on the main EC2 page and then selecting 'Create Key Pair'.  More details about creating keypairs is beyond the scope of this tutorial and can be found in the AWS documentation.

By convention, keyfiles are stored in the '.ssh' hidden subdirectory of the user's home directory i.e. ~/.ssh - this option should specify the directory's path not including the name of the keyfile itself, which is specified immediately below.

*key-name*

The 'key-name' option is used to designate the name of the keyfile itself.

**spot** (this field and all subfields are optional)

*spot-price*

The price to bid for a spot instance.  If this field is included in the YAML, JupyterFleet will submit spot requests; if not, it will use standard on-demand instances.  Please ensure that your bid is a reasonable amount - execution will pause for five minutes to give the requests time to procure, but if the bid is too low the software will then break.  It is a good idea to check the spot price history for your desired instance type to inform your bid value. 

*wait-time*

The amount of time in minutes to wait for the spot requests to be filled.  Based on testing, 3 minutes is generally sufficient for 30 instances to be successfully requested, though a lower price should generally be accompanied by a longer wait time.  Once this time elapses, JupyterFleet will check to see if all requests have been filled and then take action based on the fallback options [not yet implemented].

*fallback*

This field controls whether or not the software will proceed to implement a fallback option in the event that the spot requests are not fulfilled.

NB: Due to the way spot requests work and how their price has stabilized over the past few years, the option to continue is presently of minimal use, as it is incredibly unlikely that some requests will be filled and others will not when using one consistent price; the option is still supported to accommodate possible future changes to this status.

*contingency-type*

This field will control what the software does if all spot requests are not fulfilled (terminate itself, continue with only the instances that exist, or use on-demand instances to fill the rest of the quota).  Right now, 'on-demand' is the only supported option; it cancels the spot requests and substitutes on-demand instances.

#### blacklist

This field is optional; if enabled, it will generate blacklist files.

**blacklist-type**

This field controls what type of blacklist is to be employed; at this time, only 'automatic' is a valid option.  With 'automatic' selected, JupyterFleet will create two blacklist files: one containing the instance IDs of all instances existing at the time the software is run, and one containing a list of IPs generated at the same time.  Then, future JupyterFleet operations will ignore the instances described therein; it will neither access the blacklisted IPs to run Juptyer nor include them in the directory, and it will not kill the instances with the blacklisted instance IDs.

The purpose of this option is to ensure that running and then killing JupyterFleet will leave that region in the same state it was originally.  As a result, JupyterFleet now also supports a more flexible workshop setup protocol on the back end; for example, it is commonplace to manually create a single 'presenter instance' for the instructor that has resources in excess of those provided to students as a safeguard against edge-case notebook memory issues that would disrupt the lecture.  The use of a blacklist means that the software will not interact with and misconfigure such preexisting instances during workshop spin-up.

#### instance-configuration

**directory-parameters**


*generate-directory*

The 'generate-directory' option is used to control whether or not a directory should be generated.  The directory is (for the moment exclusively) an html file that associates each registrant's name with an IP address in the form of a clickcable link (with the port appended, such that clicking the link opens the Jupyter landing screen).

*user-list*

The 'user-list' option is used to input a list of the users that will attend the workshop.  This option is currently implemented in an overly-specific manner (names must be the third column of a CSV and there must be a header, as this is the format of the one real dataset available to the developer) and should not be used.  Eventually, this option will require a list of names, each on its own line, with no header.

*directory-type*

The 'directory-type' option will be used to allow control over the nature of the directory.  This option is not currently used - at the moment, the only directory type that can be generated is the default type consisting of an html file where the first column is the IP link and the second column is the user's name.

*push-repo*

This optional field, if included, specifies which local git repo to place the user directory inside.  At this time, only local repos associated with a remote github repo are supported.  This path should indicate the root directory of the local repo; the subdirectory path is specified separately.  The local repository will then be pushed to the master branch of the remote repo using cached github credentials.

*push-subfolder*

This optional field specifies, relative to the 'push-repo' file path, where precisely to put the user directory.  In a default github pages / sphinx setup, this path will usually be 'docs/html/_static'.

**verbosity**

The 'verbosity' option is used to control whether or not the software outputs each IP before it connects to it to activate the Jupyter server.  It will probably do other things later as well.

**logging**

*cron-interval*

The 'cron-interval' option is used to determine how frequently, in minutes, the instances will be checked and their screen statuses logged.  Setting this interval to 0 will disable logging entirely.

*log-directory*

The 'log-directory' option is used to designate where the log file will be written.  Setting the option '.' will cause the logs to be placed in the current directory.

*wait*

The 'wait' option is used to force the software to wait for 120 seconds after activating Jupyter and then check the status of screens on that instance; this test is conducted on every instance.  If there is an error with the activation of the Jupyter server, the screen will almost certainly die during that interval, meaning that no screens will be visible when the query is executed.  If no screens are visible, there is likely a problem with the AMI that must be addressed (or a misspecification of the 'conda-path' option described below).  *This option is intended for small-scale testing purposes only, as it adds two minutes to the configuration of every instance, increasing the spin-up time by hours for a full-scale deployment.*

**username**

The 'username' option is used to specify the username of the root user on the AMI (the username you used to login to the instance you used to generate the AMI).  This value will depend entirely on the AMI you have created (e.g. any AMI built from the default Ubuntu base image will be 'ubuntu').

**conda-path**

The 'conda-path' option is used to specify the full filepath to the conda binary folder within the AMI.  If this path is misspecified, attempts to activate the Jupyter server will fail and the screen will die - you can monitor for this problem by enabling the 'wait' option under 'logging' as described above.

**jupyter-port**

The 'jupyter-port' option is used to specify which port the Jupyter server is exposed on (as specified in the Jupyter configuration file on the AMI).  This option is used to generate the list of instance links and the user directory and does not ameliorate a misconfigured security group (i.e. even if 'jupyter-port' is listed correctly, Jupyter will be inaccessible if the wrong security group is applied to the instances).  Likewise, if the security group is correct but 'jupyter-port' is wrong, Jupyter itself will work fine but the directory will be populated by dead links.

**jupyter-password**

The 'jupyter-password' option is used to specify the password requried to access the Jupyter server on the instances, as designated in the AMI's Jupyter permissions file.  This password will be visible at the top of the user directory so that users can easily copy and paste it to access their Jupyter instance.