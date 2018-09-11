# JupyterFleet Documentation

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   manual

   yaml_specifications

   changelog

# Introduction

JupyterFleet is a software utility developed by the Brown University Computational Biology Core for the purpose of quick and easy Jupyter deployment on AWS.  It brings together numerous tools and allows them to be configured from a single YAML parameter specification file that controls every aspect of the deployment process.  This configuration file is hierarchical and easily human-readable, ensuring that each step of the process will proceed as desired.

JupyterFleet is intended primarily for use in conducting interactive workshops wherein a lecturer covers material written in a Jupyter notebook and students follow along in realtime on their own personal Jupyter instances, each running on its own AWS instance.  As each node is spawned from a single common Amazon Machine Image, each student will have access to an identical system in which they can interact with the lecture's content, completely eliminating the issue of system-specific errors that has until now plagued interactive programming tutelage.

When run, JupyterFleet begins by requesting EC2 nodes from Amazon in accordance with the parameters specified in the configuration YAML.  From there, it waits until these nodes have been provisioned, then activates Jupyter on each of them.  Next, it (optionally) creates a cron job to track the status of Jupyter on the EC2 nodes by writing an ad hoc bash script that is invoked by a crontab entry.  Finally, it generates an HTML directory that matches each name from a provided user list to an instance; this directory contains the Jupyter password and a clickable link to access each instance.

In its current state, JupyterFleet is functional, albeit with some features still in development.  It has been tested in the real-world setting of several Computational Biology Core workshops and has performed to completion without any problems.  That said, it has (by necessity) only been tested with the single Amazon account our organization has access to, so if you encounter problems, please feel free to contact us so we can work together on a resolution.

JupyterFleet is intended to be run on OSX or Linux.  Windows is not supported at this time, and no such support is planned in the near future.

### Authors

Andrew Leith

### Contact

For assistance, if you are associated with Brown University, contact cbc-help@brown.edu - this is our general help line, so please specify that your issue is with this site's contents

If you are not associated with Brown University, please open an issue on Github instead