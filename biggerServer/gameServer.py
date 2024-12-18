#this is where the scheduling and holding all the big dicts / writing to disk takes place. also instantiates game instances given specific things.


from littleServer import gameInstance
import multiprocessing
connected_clients = {}

class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.max_rounds = 13 # 1 for warmup, then 12 for actual rounds
        self.points = self.player_points_initialization()

        self.scheduler(new_clients)

    def scheduler(self, new_clients):
        # **** ROUND 1 *****
        new_points_1 = gameInstance(new_clients, self.client_id_dict, 1, 1, 3) # need to somehow include an agent type


        # all gameplay finished, update points
        dicts_to_merge = [dict(new_points_1.player_points)]
        self.merge_dicts(dicts_to_merge) # make a list of all the dicts that we need to merge and go from there
        print(dict(self.points))



        # display average points to all clients.


        # **** ROUND 2-4 *****

        # **** ROUND 5-7 *****

        # **** ROUND 8-10 ****

        # **** ROUND 11-13 *****

        # create 4 different round types and then randomize them so they don't know what agents they are playing with.

        # return (program over)



    def player_points_initialization(self):
        player_points = {} # have it like this for now see if that changes anything.
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


    def merge_dicts(self, dicts_to_merge):
        for dict_entry in dicts_to_merge:
            # For each dictionary, loop through its keys (e.g., 'H1', 'H10')
            for key, updates in dict_entry.items():
                # Check if the key exists in the main_dict
                if key in self.points:
                    # Now apply the updates to the main_dict for the current key (e.g., 'H1', 'H10')
                    for index, update in updates.items():
                        if index in self.points[key]:  # Ensure the index exists in the nested dictionary
                            self.points[key][index].update(update)


