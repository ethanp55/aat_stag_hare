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

        self.scheduler(new_clients)

    def scheduler(self, new_clients):
        # **** ROUND 1 *****
        gameInstance(new_clients, self.client_id_dict, self.points, 1, 1, 1) # need to somehow include an agent type
        # calculate and display points (this one is a little more of a doozy)
        # **** ROUND 2-4 *****

        # **** ROUND 5-7 *****

        # **** ROUND 8-10 ****

        # **** ROUND 11-13 *****

        # create 4 different round types and then randomize them so they don't know what agents they are playing with.

        # return (program over)



    def player_points_initialization(self):
        manager = multiprocessing.Manager()
        player_points = manager.dict()
        self.points = player_points  # just so its the right kind of object.
        hunters = ["H1","H2","H3","H4","H5","H6","H7","H8","H9","H10","H11","H12"] # max 12 players. Make this dynamic

        for hunter in hunters:
            if hunter not in player_points:
                player_points[hunter] = {}  # Initialize an empty dictionary for each hunter (not a list)

            for round in range(1, self.max_rounds + 1):
                # Directly create the round entry with "stag" and "hare" for each hunter
                current_entry = player_points[hunter]

                small_dict = {
                    "stag": False,
                    "hare": False,
                }
                # Directly assign the round as a key and small_dict as the value
                current_entry[round] = small_dict
                if round not in player_points[hunter]:
                    player_points[hunter] = current_entry
        return player_points





