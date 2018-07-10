sudo apt-get -y install build-essential && sudo apt-get -y update && sudo apt-get -y upgrade
wget erlang.org/download/otp_src_19.3.tar.gz
tar zfx otp_src_19.3.tar.gz
cd otp_src_19.3
sudo apt-get -y install libncurses-dev && sudo apt-get -y install default-jdk && sudo apt-get -y install g++
./configure
sudo make
sudo make install
cd ..
sudo apt-get -y update && sudo apt-get -y upgrade && sudo apt-get install screen && sudo apt-get install curl
git clone https://github.com/pedromslopes/antidote.git
cd antidote
git checkout aql_oriented_features
#git checkout 25aaa7a5c306ad5ba534c5a6281794922fe6c6a4
git config --global url.https://github.com/.insteadOf git://github.com/
cd ..
git clone https://github.com/pedromslopes/AQL.git
cd AQL
git checkout new_features
#git checkout eb68cfa20c89187e2b26a0d47b99e46be0b978e9
cd ..
sudo rm -rf otp_src_19.3.tar.gz
sudo rm -rf otp_src_19.3
sudo apt-get install python-pip
sudo pip install networkx
mv changetoinstall/antidote.erl antidote/src/ 
mv changetoinstall/triggers.erl antidote/src/
mv changetoinstall/aqlparser.erl AQL/src/ 
mv changetoinstall/aql_http_handler.erl AQL/src/
rm -rf changetoinstall
rm -rf OPXAQL
rm README.md
if [ $1 = "Switch" ]
then
 sudo rm -rf ControllerDBCP
 rm createtablescontroller.py
 sudo rm -rf StartControllerScript
 mv StartSwitchScript/start.sh .
 rm -rf StartSwitchScript
 rm join_dcs_script.erl
elif [ $1 = "Controller" ]
then
 sudo rm -rf SwitchDBCP
 rm createtablesswitch.py
 sudo rm -rf StartSwitchScript
 mv StartControllerScript/start.sh .
 rm -rf StartControllerScript
 chmod +x join_dcs_script.erl
else
 echo "Choose between Switch or Controller"
fi
chmod +x start.sh
chmod +x stop.sh


