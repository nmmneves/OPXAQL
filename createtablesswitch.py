import requests
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE switch ( identifier VARCHAR PRIMARY KEY, name VARCHAR DEFAULT \'\', physaddress VARCHAR,managementip VARCHAR DEFAULT \'\')'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE neighbours( physaddress VARCHAR PRIMARY KEY,switchidentifierfk VARCHAR FOREIGN KEY @UPDATE-WINS REFERENCES switch(identifier))'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE interfaces (identifier VARCHAR PRIMARY KEY,name VARCHAR, type VARCHAR DEFAULT \'\',description VARCHAR DEFAULT \'\',enabled INTEGER,operstatus INTEGER,physaddress VARCHAR,speed VARCHAR DEFAULT \'\',mtu INTEGER DEFAULT 0,switchidentifierfk VARCHAR FOREIGN KEY @UPDATE-WINS REFERENCES switch(identifier),ip VARCHAR DEFAULT \'\',prefixlength INTEGER DEFAULT 0,lastchange VARCHAR DEFAULT \'\')'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE interfaceschangeslog (id INTEGER PRIMARY KEY,interfaceidentifier VARCHAR,updatetype VARCHAR)'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE interfaceneighbour (interfaceid VARCHAR PRIMARY KEY,physaddress VARCHAR FOREIGN KEY @UPDATE-WINS REFERENCES neighbours(physaddress),remoteinterfacename VARCHAR,remoteinterfacephysaddress VARCHAR DEFAULT \'\',switchidentifierfk VARCHAR FOREIGN KEY @UPDATE-WINS REFERENCES switch(identifier))'})
#only here because of replication
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE interfaceneighbourchangeslog (id INTEGER PRIMARY KEY, interfaceidentifier VARCHAR)'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE ipvfourrib (identifier VARCHAR PRIMARY KEY,routeprefix VARCHAR,prefixlen INTEGER,nexthop VARCHAR,weight INTEGER,interfaceidentifier VARCHAR DEFAULT \'\',switchidentifierfk VARCHAR FOREIGN KEY @UPDATE-WINS REFERENCES switch (identifier))'})
r = requests.post('http://localhost:3002/aql', data={'query': 'CREATE @AW TABLE ipvfourribchangeslog (id INTEGER PRIMARY KEY,identifier VARCHAR,routeprefix VARCHAR,prefixlen INTEGER, operation VARCHAR)'})
