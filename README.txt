----------------------------DOWNLOAD DA IMAGEM E SETUP NO VMWARE---------------------------------------------

1.Fazer o download e installar o Vagrant, Virtual Box e VMWare

2.Ir ao "Manage Optional Features" dos "Settings" e instalar OpenSSH Client e Server

3.Ir ao "Use Developer Features" e selecionar Developer Mode

4.Criar um "Vagrantfile" com isto, na linha de comandos, de preferencia na directoria do Desktop:

Vagrant.configure("2") do |config|
  config.vm.box = "opx/2.2.0"
  config.vm.box_version = "2.2.0"
end

5.Na linha de comandos na diretoria do ficheiro fazer vagrant up

6.Agora na Virtual Box deve estar a imagem cujo o download foi feito.

7.Parar a execução dessa imagem

8.Descobrir a directoria do ficheiro base para a imagem (.vmdk) que por default esta na C:\Users\"nome do utilizador"\VirtualBox VMs\"nome da imagem"

9.Seguir este tutorial para criar uma imagem no VMware a partir deste link https://kb.vmware.com/s/article/2010196

10.Check that the /lib/udev/rules.d/80-dn-virt-intf.rules and /user/bin/opx-vport.sh (applies to release 2.2.0 and above) files are present on your device — otherwise copy the files and reboot.

----------------------------DOWNLOAD E SETUP ERLANG---------------------------------------------

(Dentro da maquina virtual)

11.sudo apt-get -y install build-essential && sudo apt-get -y update && sudo apt-get -y upgrade

12.wget erlang.org/download/otp_src_19.3.tar.gz

13.tar zfx otp_src_19.3.tar.gz

14.cd otp_src_19.3

15.sudo apt-get -y install libncurses-dev && sudo apt-get -y install default-jdk && sudo apt-get -y install g++

16../configure

17.sudo make

18.sudo make install

19.cd .. && erl(algo deste estilo deveria aparecer)

Erlang/OTP 19 [erts-8.3] [source] [64-bit] [smp:8:8] [async-threads:10] [kernel-poll:false]

Eshell V8.3  (abort with ^G)

----------------------------DOWNLOAD E SETUP ANTIDOTE E AQL---------------------------------------------

20.sudo apt-get -y update && sudo apt-get -y upgrade && sudo apt-get -y install git

21.git clone https://github.com/pedromslopes/antidote.git

22.cd antidote

23.git checkout aql_oriented_features

24.git config --global url.https://github.com/.insteadOf git://github.com/

25.sudo make rel

(Para testar)
26.make shell

(Noutra consola)
27.cd .. && git clone https://github.com/pedromslopes/AQL.git

28.cd AQL

29.git checkout new_features

30.make shell

----------------------------PARA TESTAR---------------------------------------------

(Mudar onde diz ip para o IP da maquina virtual ou utilizar localhost)
31. curl -d "query=SHOW TABLES" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://-->IP<--:3002/aql

(Ou)
32.sudo apt-get install python-pip

33.pip install requests

34.Criar e correr um script python com este formato, que a partida se encontra criado por defeito com o nome testscript:

import requests
import json
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE switch ( identifier VARCHAR PRIMARY KEY, name VARCHAR DEFAULT \'\',physaddress VARCHAR,managementip VARCHAR DEFAULT \'\')'})
r = requests.post('http://localhost:3002/aql', data={'query': 'INSERT INTO switch(identifier,name,physaddress,managementip) VALUES (\'switchid\',\'switch123\',\'physicaladdress1\',\'0.0.0.0\')'})
r = requests.post('http://localhost:3002/aql', data={'query': 'SELECT * FROM switch'})
print(r.status_code, r.reason)
fix = r.json()[0][0]
identifier = ''.join(chr(i) for i in fix['identifier'])
print(identifier)
