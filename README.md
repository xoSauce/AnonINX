# AnonINX
AnonINX is an anonymity system implemented as part requirement for the MEng Degree in Computer Science at UCL.
It is substantially the result of my own work except where explicitly indicated in the accompanying report.

### User Manual
To install AnonINX, clone the repository and run:
```sh
pip install -r requirements.txt --user
```
Make sure that PIP installs the packages for your Python3 version. 
You can install them using pip3. 
Naturally, if you prefer to have a virtual environment, ```venv``` is your friend.
To use a deployed instance of AnonINX, run:
```sh
cd <AnonINX directory>
python3 m_client <ip_address of key_broker> -i <desired index> -db <desired database number> (0..num_db)
```
### System Manual
To deploy AnonINX, first clone the repository.
Install fabric:
```sh
pip install Fabric3
```
#### Configure the servers
After you have some AWS instances running (or your own machines), configure the ```.ssh/config```
Here is an example of one:
```
Host db1
		HostName ec2-52-212-13-53.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host db2
		HostName ec2-34-249-226-25.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host key-brokerU
		HostName ec2-52-31-4-151.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host mix-node1U
		HostName ec2-34-253-114-191.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host mix-node2U
		HostName ec2-52-17-148-131.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host mix-node3U
		HostName ec2-34-252-15-86.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host mix-node4U
		HostName ec2-34-253-103-162.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

Host mix-node5U
		HostName ec2-52-50-108-94.eu-west-1.compute.amazonaws.com
		User ubuntu
		IdentityFile ~/.ssh/e-PrivateDBs.pem

```
On top of this, make a note of the IP of the key-broker server.
Make sure the servers provide SSH access.
In order to deploy to all hosts run:
```sh
fab all_hosts deploy_scratch
```
This will install dependencies for Ubuntu machines only. Deploying on different flavours will require some dependency gathering on the admin side and modifying the fabric file.
The fabric file, ```fabfile.py```, provides a list of options to deploy:
``` deploy_scratch ``` which will install the environment
``` deploy_withvenv ``` will update with the latest version of the repository, without reinstalling the environment. This was mostly used during development, but it could potentially be useful.

If you configured the `.ssh/config` file properly, you will be able to run:
```sh
fab db_1_2 deploy_db_file:db_path=<path_to_db_file>
```
Which will deploy the databases file to your hosts called `db1` and `db2`.
Of course, for additional configuration options (adding more databases, or name changing), the fabfile will require some modifications. 
#### Running the services
Fabric provides mutliple utilities to run the servers. In a terminal window, run:
```sh
fab keybroker_host start_keybroker
```
This will start the keybroker host remotely.
Similarly the following options are available for the rest of the servers:
```sh
fab db_1_2 start_db_listener:ip=<ip_of_keybroker>, port=8080, db_path=<path_to_remote_db_file>
fab mix_hosts start_mix_listener:ip=<ip_of_keybroker>, port=8080
```
Naturally, the keybroker should be started first so the rest of the servers know where to connect.
