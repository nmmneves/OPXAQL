# DBCP

Routing implemented with the help of Databases.

### Instalation

This represents the basic tutorial to install a Switch and a Controller (will be updated with more detail in a short period of time). In the end of this explination there is a copy/paste segment with all the commands so you dont have to run one by one, excluding the start.

**1- Make sure you have the lastest git version installed and up to date.**
```
sudo apt-get install -y git
```
**2- Get the files including all the scripts**
```
git clone https://github.com/nmmneves/OPXAQL.git
```
**3- Get the files from the basis directory**
```
mv OPXAQL/* .
```
**4- Give permissions to the script file so you can run it**
```
chmod +x install.sh
```
**5-Run the installation script (choose between Switch or Controller as the only argument for the script)**
```
./install.sh Switch (or Controller)
```
**6-Start the switch/controller. The first time you run it may take a while since it's compiling and creating a Antidote release.
The start script for the switch receives IPs as arguments (as much as you want). Each IP will correspond to a single interface, starting with e101-001-0 and ending in e101-00X-0 where x is the number of IPs you've writen. For example:**
```
./start 10.1.1.1 11.1.1.1

```
**It will print something like this in response (if nothing fails):**
```
Setting Interface e101-001-0 Up with IP = 10.1.1.1
Setting Interface e101-002-0 Up with IP = 11.1.1.1
```
**For the controller, it receives the public ip of each switch that wants to be connected to him. In the simple example where there are only two switchs and the controller, the start script should look like this:**
```
./start 192.168.1.1 192.168.1.2

```

**7-Copy/paste**
```
sudo apt-get -y update &&
sudo apt-get -y upgrade &&
sudo apt-get -y install git &&
git clone https://github.com/nmmneves/OPXAQL.git &&
mv OPXAQL/* . &&
chmod +x install.sh &&
./install.sh Controller
```
