# Changelog


### Upcoming Features


An option to create a cron job that will automatically kill all instances after X hours to avoid accidental overbilling

More informative errors as beta testing reveals issues (ongoing)

An option to enable or disable OSX alerts, and to customize which alerts to get (all alerts, only startup alerts, or only critical failure alerts)

Logs that summarize instance status in a concise, human-skimmable fashion

git pull first before committing

An option to name all of the spawned instances something specific


### Beta Build


#### Version 0.9.1


Added instance blacklist functionality: preexisting instances will no longer be accessed by jupyter during activation or killed by --kill

#### Version 0.9


Added a countdown timer for processes that take several minutes

'--kill' flag now removes the crontab entry JupyterFleet generated

'--kill' now creates a folder for the old files and moves them all there

Added an option to automatically push the directory to a github repo (using cached git credentials)

'--kill' now removes the autopushed directory (if it exists)

#### Version 0.8.1


Logging crontab bugs fixed

Logging script function partially overhauled (raw log file per iteration)

Partial implementation of OSX alert function

#### Version 0.8


Added more robust fallback checking, auto-removal of spot requests if bid is too low

#### Version 0.7.1


Added error message for the case where the user list is missing


#### Version 0.7


Fixed critical issue with logging (correct directory is now checked for IPs)



#### Version 0.6.1


Fixed typo

Added temporary fallback option for the case where bid is deemed so low that it is invalid

#### Version 0.6


Added a customizable wait time for spot instances

Added a way to check if spot bid fails

Began adding fallback options for the case where spot bid fails

Fixed a bug regarding spot price parsing

The user directory now shows the Jupyter password by default for ease of copying

Added command line option '--skip' to skip instance spin-up (proceeding directly to IP retrieval and key valdiation)

#### Version 0.5.3


Added \_\_name\_\_ check

#### Version 0.5.2


Implemented docstrings for functions - YAML documentation can be found on this site

#### Version 0.5.1


Code refactored for modularity

Added option to use spot instances instead of on-demand instances

#### Version 0.5


Initial beta build designated as Version 0.5


### Alpha Build


#### Version 1.4


Logging functionality implemented for OSX and Linux

Alpha build feature-complete other than directory construction (to be addressed in beta)

#### Version 1.3


Added a more robust key permission check with platform-specificity and a custom error message

#### Version 1.2


Fixed critical bug with AWS CLI configuration file generation

#### Verson 1.1


Added changelog

Added --kill argument to deactivate resources

Suppressed superfluous output from various commands

Added manual page
