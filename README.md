# DBCP

Routing implemented with the help of Databases.

### ----------Getting Virtual Machine Image----------

1- Download Vagrant(2.1.2), Virtual Box(5.2.8) and VMWare WorkstationPro(14.1.2).

Note: In Windows you might need to go "Manage Optional Features" in "Settings" and install OpenSSH Client and Server
and also go to "Use Developer Features" e select Developer Mode.

2- Open Virtualbox.

3- Create a "Vagrantfile", preferably in the Desktop directory, with this:

Vagrant.configure("2") do |config|
  config.vm.box = "opx/2.2.0"
  config.vm.box_version = "2.2.0"
end

4- In the same directory do "vagrant up". It should download a VMI with OPX Version 2.2 pre-installed.

5- Now in Virtual Box, the VM you just downloaded should be running.

6- Shutdown the VM.

7- Follow one of this tutorials to change from VirtualBox to VMWare.

-https://kb.vmware.com/s/article/2010196

-https://askubuntu.com/questions/588426/how-to-export-and-import-virtualbox-vm-images

8- Put file 80-dn-virt-intf.rules in the directory etc/udev/rules.d.

### --------------------Instalation--------------------

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
**5-Run the installation script (choose between "Switch" or "Controller" as the only argument for the script)**
```
./install.sh Switch
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
**For the controller, it receives the public ip of each switch that wants to be connected. In the simple example where there are only two switches and the controller, the start script should look like this, since the controller IP is not necessary:**
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
