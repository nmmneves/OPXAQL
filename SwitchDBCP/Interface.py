class Interface:
    def __init__(self, name,type,enabled, phy_saddress, mtu, oper_status, speed,ip,prefix_length):
        self.name = name
        self.type = type
        self.enabled = enabled
        self.phys_address = phy_saddress
        self.mtu = mtu
        self.oper_status = oper_status
        self.speed = speed
        self.ip =ip
        self.prefix_length=prefix_length


