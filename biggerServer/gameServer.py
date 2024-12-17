#this is where the scheduling and holding all the big dicts / writing to disk takes place. also instantiates game instances given specific things.


from littleServer import gameInstance
import multiprocessing
connected_clients = {}

class GameServer():
    def __init__(self, new_clients, client_id_dict):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.max_rounds = 13 # 1 for warmup, then 12 for actual rounds
        self.points = self.player_points_initialization()

        self.scheduler()

    def scheduler(self):
        # so what I want to be able to do is make a call w/ the players
        gameInstance(self.connected_clients, self.points, 0, None) # just with all human players (as warm up)
        # now calcualte and display average points
        # call gameInstance again and go from there.




    def player_points_initialization(self):
        manager = multiprocessing.Manager()
        player_points = manager.dict()
        self.points = player_points  # just so its the right kind of object.

        for player in self.client_id_dict: # need to generate usernames or something cause rn IDK what this is gonna spit.
            if self.client_id_dict[player] not in self.points:
                self.points[self.client_id_dict[player]] = {}  # Initialize an empty dictionary for each hunter (not a list)

            for round in range(1, self.max_rounds + 1):
                current_entry = self.points[self.client_id_dict[player]]
                small_dict = {
                    "stag": False,
                    "hare": False,
                }
                # Directly assign the round as a key and small_dict as the value
                current_entry[round] = small_dict
                if round not in self.points[self.client_id_dict[player]]:
                    self.points[player] = current_entry
        return self.points





