#this is where the scheduling and holding all the big dicts / writing to disk takes place. also instantiates game instances given specific things.

from littleServer import gameInstance
from multiprocessing import Process
import multiprocessing
import json
import time

print("is this going off in gameserver ")

# 1. Random, 2. AlegAAtr, 3. QAlegAATr, 4. SMAlegAATr 5.RAW0,  ## agent types. # we won't need these anymore
# but this is where we will put the bot types once those have been cleared up.

STAG_POINTS = 20
HARE_POINTS = 10

connected_clients = {}

class GameServer():
    def __init__(self, new_clients, client_id_dict, client_usernames):
        self.connected_clients = new_clients
        self.client_id_dict = client_id_dict
        self.client_usernames = client_usernames
        self.max_rounds = 13 # 1 for warmup, then 12 for actual rounds
        self.points = self.player_points_initialization()
        self.current_round = 0
        self.scheduler(new_clients)

    def scheduler(self, new_clients):
        q = multiprocessing.Queue()
        # TEST FOR SOMETHING -- DELETE LATER (needed to make sure that we could cycle through agent types as well. this is gonna be fun.
        # current_round = 1
        # agent_types = [[1, 1], [1, 1]] # what type each bot should be. We check to make sure there are always 3.
        # player_indices_round_2 = [[0], [1]]  # start them in the same game
        # games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_types)
        # self.run_games(games_list, q, current_round)

        # # **** ROUND 1 ***** # 6 players, each human in their own game (w/ hare first)
        current_round = 1
        agent_types = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]] # what type each bot should be. We check to make sure there are always 3.
        player_indices_round_2 = [[0], [1], [2], [3], [4], [5], [6]] # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_types)
        self.run_games(games_list, q, current_round)

        # # **** ROUND 2 ***** # 6 players, each human in their own game (w/ stag greedy first)
        current_round = 2
        agent_type = [[2, 2],[2, 2],[2, 2],[2, 2],[2, 2],[2, 2],[2, 2]]  # what type each bot should be. We check to make sure there are always 3.
        player_indices_round_2 = [[0], [1], [2], [3], [4], [5], [6]]  # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)


        # so based on my understanding, doing this SHOULD just overwrite the practice rounds, unless we want to keep them.

        # B is []
        # A is [1,1]
        # C is [2,2]
        # D is [2]

        # # **** ROUND 3 ***** # 6 players, each human in their own game (w/ stag greedy first)
        current_round = 1
        player_indices_round_2 = [[0, 1, 5], [2], [3, 4], [6]]  # start them in the same game
        agent_type = [[], [2], [2,2], [1,1]]  # what type each bot should be. We check to make sure there are always 3.
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 2
        player_indices_round_2 = [[0, 1, 5], [2, 4], [3], [6]]  # start them in the same game
        agent_type = [[], [2,2], [1,1], [2]]  # what type each bot should be. We check to make sure there are always 3.
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 3
        player_indices_round_2 = [[0, 3, 6], [1, 2], [4], [5]]  # start them in the same game
        agent_type = [[], [2,2], [1,1], [2]]  # what type each bot should be. We check to make sure there are always 3.
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 4
        player_indices_round_2 = [[0, 1, 2], [3], [4], [5,6]]  # start them in the same game
        agent_type = [[], [1,1], [2], [2,2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 5
        player_indices_round_2 = [[0, 6], [1,2,5], [3], [4]]  # start them in the same game
        agent_type = [[2,2], [], [2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 6
        player_indices_round_2 = [[0,2,3], [1,4], [5], [6]]  # start them in the same game
        agent_type = [[], [2,2], [2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 7
        player_indices_round_2 = [[0,6], [1], [2], [3,4,5]]  # start them in the same game
        agent_type = [[2,2], [2], [1,1], []]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 8
        player_indices_round_2 = [[0, 5], [1,2,6], [3], [4]]  # start them in the same game
        agent_type = [[2,2], [], [1,1], [2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 9
        player_indices_round_2 = [[0, 2, 3], [1, 5], [4], [6]]  # start them in the same game
        agent_type = [[], [2,2], [2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 10
        player_indices_round_2 = [[0], [1, 4, 6], [2], [3,5]]  # start them in the same game
        agent_type = [[1,1], [], [2], [2,2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 11
        player_indices_round_2 = [[0], [1, 3], [2,4,6], [5]]  # start them in the same game
        agent_type = [[2], [2,2], [], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 12
        player_indices_round_2 = [[0,3], [1,4,6], [2], [5]]  # start them in the same game
        agent_type = [[2,2], [], [1,1], [2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 13
        player_indices_round_2 = [[0, 2, 6], [1], [3,4], [5]]  # start them in the same game
        agent_type = [[], [2], [2,2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 14
        player_indices_round_2 = [[0, 3, 4], [1], [2,5], [6]]  # start them in the same game
        agent_type = [[], [1,1], [2,2], [2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 15
        player_indices_round_2 = [[0, 3, 6], [1,4], [2], [5]]  # start them in the same game
        agent_type = [[], [2,2], [2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 16
        player_indices_round_2 = [[0], [1], [2, 6], [3, 4, 5]]  # start them in the same game
        agent_type = [[1,1], [2], [2,2], []]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 17
        player_indices_round_2 = [[0, 4], [1,3,5], [2], [6]]  # start them in the same game
        agent_type = [[2,2], [], [1,1], [2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 18
        player_indices_round_2 = [[0, 2], [1], [3], [4,5,6]]  # start them in the same game
        agent_type = [[2,2], [1,1], [2], []]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 19
        player_indices_round_2 = [[0], [1], [2,6], [3,4,5]]  # start them in the same game
        agent_type = [[2], [1,1], [2,2], []]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 20
        player_indices_round_2 = [[0], [1,2,6], [3,5], [4]]  # start them in the same game
        agent_type = [[2], [], [2,2], [1,1]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)

        current_round = 21
        player_indices_round_2 = [[0], [1,6], [2,4,5], [6]]  # start them in the same game
        agent_type = [[1,1], [2,2], [], [2]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
        self.run_games(games_list, q, current_round)



        # ***** ROUND 2-4 ***** # human on robot violence - not quite sure how jake wants me to handle this.
        for i in range(1, 4): # runs this loop 3 times, using the current round, the agent types, and the players we want grouped together.
            current_round = i
            agent_type = [1,1]
            player_indices_round_2 = [[0]]
            games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, agent_type)
            self.run_games(games_list, q, current_round)

        # # ***** ROUND 5-7 ***** # more rounds.
        for i in range(5, 8):
            current_round = i
            rounds_to_run = 1
            agent_type = [3, 2]
            player_indices_round_2 = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9], [10, 11]]
            games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q,
                                                    agent_type)
            self.run_games(games_list, q, current_round)


    def create_game_processes(self, player_indices, current_round, new_clients, q, agent_types):
        games_list = []

        if len(agent_types[0]) + len(player_indices[0]) != 3: # we don't have the right number of bots and players.
            print("UH OH FETCHER! YOU DIDN'T configure this round correctly!")
            return [] # empty list so no rounds run.

        for i, indices in enumerate(player_indices): # should? now sort through the agent types and make sure it spits out the correct thing.
            # Create a new process for each list of indices
            game_process = Process(target=self.game_thread,
                                   args=(
                                   self.create_player_dict_pairs(indices, new_clients), q, current_round,
                                   agent_types[i]))
            games_list.append(game_process)

        return games_list


    def run_games(self, games_list, q, current_round):
        self.start_and_join_games(games_list, q)
        points_to_send = self.calc_avg_points(current_round)
        self.send_leaderboard(points_to_send)  # sends out the updated leaderboard.


    def start_and_join_games(self, games_list, q):
        for game in games_list:
            game.start()

        for game in games_list:
            game.join()

        dicts_to_merge = []
        while not q.empty():
            item = q.get()
            dicts_to_merge.append(item)

        self.merge_dicts(dicts_to_merge)


    def create_player_dict_pairs(self, new_players, new_clients): # new players is a list containing a bunch of indexes, and returns a dict of pairs.
        return_players =  {}
        for player in new_players:
            player_1 = list(new_clients.items())[player]
            player_1_key, player_1_socket = player_1
            return_players[player_1_key] = player_1_socket
        return return_players


    def game_thread(self, new_clients, q, current_round, agent_types):
        new_points_1 = gameInstance(new_clients, self.client_id_dict, agent_types, current_round)  # need to somehow include an agent type
        q.put(new_points_1.player_points)


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


    def calc_avg_points(self, target_round):
        new_list = [] # list of tuples, holds the clientID and then the number of points that they have accrued
        for key in self.points:
            curr_points = 0
            for curr_round in self.points[key]:
                if curr_round <= target_round: # calculate only up and to the current round. IDK if it will fix our problem but we shall see.
                    if self.points[key][curr_round]['stag'] == True:
                        curr_points += STAG_POINTS
                    if self.points[key][curr_round]['hare'] != False:
                        curr_points += HARE_POINTS / self.points[key][curr_round]['hare']
                else:
                    break # not sure if that will do what I want it to do.

            if curr_points > 0:
                curr_points = curr_points / target_round # just to get the average
                curr_points = round(curr_points, 2)

            # lets grab the username while we are here
            if int(key[1:]) in self.client_usernames: # should always fire but just to prevent null access.
                new_tuple = (self.client_usernames[int(key[1])], curr_points)
                new_list.append(new_tuple)

        sorted_points = sorted(new_list, key=lambda x: x[1], reverse=True)
        return sorted_points


    def send_leaderboard(self, new_points_dict):
        time.sleep(2)  # lets everyone see the leaderboard
        message = {
            "LEADERBOARD": new_points_dict,
        }
        new_message = json.dumps(message).encode()
        for client in self.connected_clients:
            self.connected_clients[client].send(new_message)
        time.sleep(2)  # lets everyone see the leaderboard