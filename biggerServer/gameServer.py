#this is where the scheduling and holding all the big dicts / writing to disk takes place. also instantiates game instances given specific things.
import os

import numpy as np

from littleServer import gameInstance
from multiprocessing import Process
import multiprocessing
import json
import time


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
        self.high_level_dict = {}  # this stores the round and then situation break down.
        self.scheduler(new_clients)


    def scheduler(self, new_clients):
        q = multiprocessing.Queue()
        big_queue = multiprocessing.Queue()
        # TEST FOR SOMETHING -- DELETE LATER (needed to make sure that we could cycle through agent types as well. this is gonna be fun.
        # current_round = 1
        # situations = [[1, 1], [1, 1]] # what type each bot should be. We check to make sure there are always 3.
        # player_indices_round_2 = [[0], [1]]  # start them in the same game
        # games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations)
        # self.run_games(games_list, q, current_round)

        # # **** ROUND 1 ***** # 6 players, each human in their own game (w/ hare first)

        current_round = 1
        situations = [["A"]] # so having them all in the same situation does weird thigns to the dict, but other than that this SHOULD work.
        player_indices_round_2 = [[0]]  # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)
        self.save_stuff()

        current_round = 2
        situations = [["C"]]
        player_indices_round_2 = [[0, 1]]  # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)


        # # **** ROUND 1 ***** # 6 players, each human in their own game (w/ hare first)
        current_round = 1
        situations = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]] # what type each bot should be. We check to make sure there are always 3.
        player_indices_round_2 = [[0], [1], [2], [3], [4], [5], [6]] # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)


        # # **** ROUND 2 ***** # 6 players, each human in their own game (w/ stag greedy first)
        current_round = 2
        situations = [[2, 2],[2, 2],[2, 2],[2, 2],[2, 2],[2, 2],[2, 2]]  # what type each bot should be. We check to make sure there are always 3.
        player_indices_round_2 = [[0], [1], [2], [3], [4], [5], [6]]  # start them in the same game
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        # so based on my understanding, doing this SHOULD just overwrite the practice rounds, unless we want to keep them.


        # # **** ROUND 3 ***** # 6 players, each human in their own game (w/ stag greedy first)
        current_round = 1
        player_indices_round_2 = [[0, 1, 5], [2], [3, 4], [6]]   # the players that will be in the same game
        situations = [["B"], ["D"], ["C"], ["A"]]  # the number and type of bot we are expecting.
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 2
        player_indices_round_2 = [[0, 1, 5], [2, 4], [3], [6]]
        situations = [["B"], ["C"], ["A"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 3
        player_indices_round_2 = [[0, 3, 6], [1, 2], [4], [5]]
        situations = [["B"], ["C"], ["A"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 4
        player_indices_round_2 = [[0, 1, 2], [3], [4], [5,6]]
        situations = [["B"], ["A"], ["D"], ["C"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 5
        player_indices_round_2 = [[0, 6], [1,2,5], [3], [4]]
        situations = [["C"], ["B"], ["D"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 6
        player_indices_round_2 = [[0,2,3], [1,4], [5], [6]]
        situations = [["B"], ["C"], ["D"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 7
        player_indices_round_2 = [[0,6], [1], [2], [3,4,5]]
        situations = [["C"], ["D"], ["A"], ["B"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 8
        player_indices_round_2 = [[0, 5], [1,2,6], [3], [4]]
        situations = [["C"], ["B"], ["A"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 9
        player_indices_round_2 = [[0, 2, 3], [1, 5], [4], [6]]
        situations = [["B"], ["C"], ["D"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 10
        player_indices_round_2 = [[0], [1, 4, 6], [2], [3,5]]
        situations = [["A"], ["B"], ["D"], ["C"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 11
        player_indices_round_2 = [[0], [1, 3], [2,4,6], [5]]
        situations = [["D"], ["C"], ["B"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 12
        player_indices_round_2 = [[0,3], [1,4,6], [2], [5]]
        situations = [["C"], ["B"], ["A"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 13
        player_indices_round_2 = [[0, 2, 6], [1], [3,4], [5]]
        situations = [["B"], ["D"], ["C"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 14
        player_indices_round_2 = [[0, 3, 4], [1], [2,5], [6]]
        situations = [["B"], ["A"], ["C"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 15
        player_indices_round_2 = [[0, 3, 6], [1,4], [2], [5]]
        situations = [["B"], ["C"], ["D"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 16
        player_indices_round_2 = [[0], [1], [2, 6], [3, 4, 5]]
        situations = [["A"], ["D"], ["C"], ["B"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 17
        player_indices_round_2 = [[0, 4], [1,3,5], [2], [6]]
        situations = [["C"], ["B"], ["A"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 18
        player_indices_round_2 = [[0, 2], [1], [3], [4,5,6]]
        situations = [["C"], ["A"], ["D"], ["B"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 19
        player_indices_round_2 = [[0], [1], [2,6], [3,4,5]]
        situations = [["D"], ["A"], ["C"], ["B"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 20
        player_indices_round_2 = [[0], [1,2,6], [3,5], [4]]
        situations = [["D"], ["B"], ["C"], ["A"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)

        current_round = 21
        player_indices_round_2 = [[0], [1,6], [2,4,5], [6]]
        situations = [["A"], ["C"], ["B"], ["D"]]
        games_list = self.create_game_processes(player_indices_round_2, current_round, new_clients, q, situations, big_queue)
        self.run_games(games_list, q, current_round, big_queue)
        self.append_average_points(current_round)
        self.save_stuff()

    def create_game_processes(self, player_indices, current_round, new_clients, q, situations, big_queue):
        games_list = []

        # make a way to to check that everything sums up to 3 ig.

        for i, indices in enumerate(player_indices): # should? now sort through the agent types and make sure it spits out the correct thing.
            # Create a new process for each list of indices
            game_process = Process(target=self.game_thread,
                                   args=(
                                   self.create_player_dict_pairs(indices, new_clients), q, current_round,
                                   situations[i], big_queue))
            games_list.append(game_process)

        return games_list


    def run_games(self, games_list, q, current_round, big_queue):
        print('attempitng to run games here')
        situations_dict, big_dict_list = self.start_and_join_games(games_list, q, big_queue)
        self.add_to_master_dict(situations_dict, current_round)
        self.add_to_big_dict(big_dict_list, current_round)
        points_to_send, points_to_save = self.calc_avg_points(current_round)
        self.points_to_save = points_to_save
        self.send_leaderboard(points_to_send)  # sends out the updated leaderboard.

    def add_to_big_dict(self, big_dict_list, current_round):
        for big_dict in big_dict_list:
            for situation, current_dict in big_dict.items():
                self.high_level_dict[current_round][situation] = current_dict

    def add_to_master_dict(self, situations_dict, current_round):
        total_dict = {}
        for situation, values in situations_dict.items():
            new_dict = {}
            for player in values:
                selected_keys = ["hare", "stag"]
                new_dict[player] = {key : self.points[player][current_round][key] for key in selected_keys}
            total_dict[situation] = new_dict
        self.high_level_dict[current_round] = total_dict # that might brick as well. lets find out.


    def start_and_join_games(self, games_list, q, big_queue):
        for game in games_list:
            game.start()

        for game in games_list:
            game.join()

        dicts_to_merge = []
        all_big_dicts = []
        while not q.empty():
            item = q.get()
            dicts_to_merge.append(item)

        while not big_queue.empty():
            item = big_queue.get()
            all_big_dicts.append(item)

        return self.merge_dicts(dicts_to_merge), all_big_dicts


    def create_player_dict_pairs(self, new_players, new_clients): # new players is a list containing a bunch of indexes, and returns a dict of pairs.
        return_players =  {}
        for player in new_players:
            player_1 = list(new_clients.items())[player]
            player_1_key, player_1_socket = player_1
            return_players[player_1_key] = player_1_socket
        return return_players


    def game_thread(self, new_clients, q, current_round, situations, big_queue):
        new_points_1 = gameInstance(new_clients, self.client_id_dict, situations, current_round)  # need to somehow include an agent type
        new_dict = {}
        new_dict[new_points_1.situation] = new_points_1.player_points
        #new_dict["Big"] = new_points_1.big_dict
        q.put(new_dict)
        big_queue.put(new_points_1.big_dict)


    def player_points_initialization(self):
        player_points = {} # have it like this for now see if that changes anything.
        self.points = player_points  # just so its the right kind of object.
        hunters = ["H1","H2","H3","H4","H5","H6","H7"] # max 7 players. I SHOULD make this dynamic.
        for i in range(len(self.connected_clients)):
            new_name = "H" + str(i+1)
            hunters.append(new_name)

        for hunter in hunters:
            if hunter not in player_points:
                player_points[hunter] = {}  # Initialize an empty dictionary for each hunter (not a list)

            # for round in range(1, self.max_rounds + 1):
            #     # Directly create the round entry with "stag" and "hare" for each hunter
            #     current_entry = player_points[hunter]
            #
            #     small_dict = {
            #         "stag": False,
            #         "hare": False,
            #         "avg_points" : 0,
            #     }
            #     # Directly assign the round as a key and small_dict as the value
            #     current_entry[round] = small_dict
            #     if round not in player_points[hunter]:
            #         player_points[hunter] = current_entry
        return player_points


    def merge_dicts(self, dicts_to_merge):
        for situation in dicts_to_merge:
            # For each dictionary, loop through its keys (e.g., 'H1', 'H10')
            for key, dict_entry in situation.items(): # should cycle through the situations.
                for key, updates in dict_entry.items():
                    # Check if the key exists in the main_dict
                    if key in self.points:
                        # Now apply the updates to the main_dict for the current key (e.g., 'H1', 'H10')
                        for index, update in updates.items():
                            if index in self.points[key]:  # Ensure the index exists in the nested dictionary
                                self.points[key][index].update(update)
        situation_player_dict = {}
        for situation in dicts_to_merge:
            situation_list = []
            for key, dict_entry in situation.items():
                for player_name, values in dict_entry.items():
                    situation_list.append(player_name)
                situation_player_dict[key] = situation_list
        return situation_player_dict


    def calc_avg_points(self, target_round):
        new_list_to_send = [] # list of tuples, holds the clientID and then the number of points that they have accrued
        new_list_to_save = []
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
                new_list_to_send.append(new_tuple)
                save_tuple = (key, curr_points)
                new_list_to_save.append(save_tuple)

        sorted_points = sorted(new_list_to_send, key=lambda x: x[1], reverse=True)
        sorted_save_tuples = sorted(new_list_to_save, key=lambda x: x[1], reverse=True)
        return sorted_points, sorted_save_tuples


    def send_leaderboard(self, new_points_dict):
        time.sleep(2)  # lets everyone see the leaderboard
        message = {
            "LEADERBOARD": new_points_dict,
        }
        new_message = json.dumps(message).encode()
        for client in self.connected_clients:
            self.connected_clients[client].send(new_message)
        time.sleep(2)  # lets everyone see the leaderboard

    def append_average_points(self, current_round):
        # we need to modify self.points to include another feild - the average points
        # here's how we are going to do this
        for tuple in self.points_to_save:
            self.points[tuple[0]][current_round]["avg_points"] = tuple[1]
        print(self.points_to_save, "thats the points we were supposed to save")
        print(self.points, "\n and that is the overall points dict at the end")

    def save_stuff(self):
        desktop_path = os.path.expanduser("~/Desktop")
        top_level_path = "stag_hare_top_level.json"
        low_level_path = "stag_hare_low_level.json"
        file_path_1 = os.path.join(desktop_path, top_level_path)
        file_path_2 = os.path.join(desktop_path, low_level_path)
        unique_file_path_1 = self.get_unique_filename(file_path_1)
        unique_file_path_2 = self.get_unique_filename(file_path_2)

        with open(unique_file_path_1, "w") as f:
            json.dump(self.client_usernames, f, indent=4)
            json.dump(self.points, f, indent=4)

        # Convert to JSON string
        json_string = json.dumps(self.high_level_dict, indent=4, cls=NumpyEncoder)
        json_string = json_string.replace(" [", "[").replace(", ", ",").replace(" ]", "]")

        with open(unique_file_path_2, "w") as f:
            f.write(json_string)

    def get_unique_filename(self, file_path):
        if not os.path.exists(file_path):
            return file_path
        else:
            base, extension = os.path.splitext(file_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{extension}"):
                counter += 1
            return f"{base}_{counter}{extension}"


# Custom encoder to handle np.int64 conversion to Python int
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)  # Convert np.int64 to native Python int
        return super(NumpyEncoder, self).default(obj)
