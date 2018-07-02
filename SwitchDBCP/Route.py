class Route:
    def __init__(self, router_id,network,prefix_length, next_hop, metric):
        self.router_id = router_id
        self.network=network
        self.prefix_length = prefix_length
        self.next_hop = next_hop
        self.metric = metric



