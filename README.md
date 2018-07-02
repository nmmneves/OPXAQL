# DBCP

Routing implemented with the help of Databases.

### Instalation

This represents the basic tutorial to install a Switch and a Controller(Will be updated with more detail in a short period of time)

**1- Make sure you have the lastest git version installed and up to date.**
sudo apt-get install -y git

**2- Get the files including all the scripts**
git clone https://github.com/nmmneves/OPXAQL.git

**3- Get rid of the basis directory**
mv OPXAQL/* .

**4- Give permissions to the script file so you can run it**
chmod +x install.sh

**5-Run the installation script(choose between Switch or Controlleras the only argument for the script)**
./install.sh Switch (or Controller)

**6-Start the switch/controller. The first time you run it may take a while since it's compiling and creating a Antidote release.
The start script for the switch receives IPs as arguments (as much as you want). This IPs will correspond to a interface, starting
with e101-001-0 and ending in e101-00X-0 where x is the number of IPs you've writen.**
./start

