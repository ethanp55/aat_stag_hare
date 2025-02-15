# this holds the actual instance of stag hunt, only runs 1 round based on scheduling. run this and then return the new dicts that we need to append to the large dicts up above.
import select
import json

import time # tit for tat pausing?

# from agents.alegaatr import AlegAATr
# from agents.dqn import DQNAgent
# from agents.qalegaatr import QAlegAATr
# from agents.smalegaatr import SMAlegAATr
# from agents.rawo import RawO

PAUSE_TIME = 5
HEIGHT = 3
WIDTH = 3

from agents.random_agent import *
from agents.human import *
from environment.world import StagHare

import random

class gameInstance():
    def __init__(self, connected_clients, client_id_dict, agentType, round=0):
        self.connected_clients = connected_clients
        self.client_id_dict = client_id_dict
        self.agentType = agentType
        self.create_hunters()
        self.start_round = round # needed for dictionary purposes
        self.HUMAN_PLAYERS = len(connected_clients)
        self.AI_AGENTS = 3 - self.HUMAN_PLAYERS
        self.round = round # start with round 1, but I should probably make it an actual thinger so I can keep track of it better.
        self.max_rounds = round
        client_id_list = []
        for client in self.connected_clients:
            client_id_list.append(client+1)
        self.client_id_list = client_id_list
        while True:  # set up stag hunt and avoid weird edgecase
            stag_hare = StagHare(HEIGHT, WIDTH, self.hunters)
            if not stag_hare.is_over():
                break
        self.player_points_initialization()
        self.stag_hare = stag_hare  # just to have that down.
        self.main_game_loop()


    def main_game_loop(self):
        while True:
            client_input = {}
            client_intent = {}
            client_time = []
            while True:
                current_time = time.time()
                self.send_state()  # sends out the current game state
                data = self.get_client_data()
                for client, received_json in data.items():
                    if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] != None:
                        new_time = time.time() - current_time
                        client_input[self.client_id_dict[client]] = received_json["NEW_INPUT"]
                        client_intent[self.client_id_dict[client]] = received_json["INTENT"]
                        client_time.append(new_time)

                # Check if all clients have provided input
                if len(client_input) == len(self.connected_clients):
                    pause_time = max(3.0, sum(client_time) / len(client_time))  # keeps the AI agents paused, but for no more than 3 seconds tops.
                    print("WE HAVE FINISHED, here is the client wait time : ", pause_time)
                    # for i in range(3 - len(client_input)):  # confusing pausing timimg thingy.
                    #     time.sleep(pause_time) # put this back in later. fast for now.

                    break # gets us out of the input loop. hopefully.

            running = self.stag_hunt_game_loop(self.player_points, client_input, client_intent, client_time)
            if running == False:
                break
            client_input.clear()

        return self.adjust_points()

    def send_state(self):
        current_state = self.create_current_state()
        send_player_points = self.player_points.copy()
        # lets make a list of all of the connected_clients_ids and use those to generate players
        response = {}
        response = { # KEEP THIS OUTSIDE THE LOOP PLEASE
            "HUMAN_AGENTS": len(self.connected_clients),
            "AI_AGENTS": 3 - len(self.connected_clients),
            "CLIENT_ID_LIST": self.client_id_list,
            "AGENT_POSITIONS": current_state,
            "POINTS": send_player_points,
            "CURR_ROUND": self.round,
            "HEIGHT": HEIGHT,
            "WIDTH": WIDTH,
        }


        for client in self.connected_clients:
            new_message = json.dumps(response).encode()
            self.connected_clients[client].send(new_message)
        time.sleep(0.1) # makes sure not to overwhelm the client.

    def get_client_data(self):
        ready_to_read, _, _ = select.select(list(self.connected_clients.values()), [], [], 0.1)
        data = {}
        for client in ready_to_read:
            try:
                msg = ''
                while True:  # Accumulate data until the full message is received
                    chunk = client.recv(1024).decode()
                    msg += chunk
                    if len(chunk) < 1024:  # End of message
                        break
                if msg:
                    data[client] = json.loads(msg)
            except Exception as e:
                pass
        return data

    def stag_hunt_game_loop(self, player_points, player_input, client_intent, client_time):

        rewards = [0] * (len(self.hunters) + 2)

        self.next_round(rewards, player_input, client_intent, client_time)

        self.send_state()

        if self.stag_hare.is_over():

            # formualtes the server response to client.
            hare_dead = False
            stag_dead = False

            if self.stag_hare.state.hare_captured():
                self.find_hunter_hare()
                hare_dead = True
            else:
                self.find_hunter_stag()
                stag_dead = True

            small_dict = {}  # helps me know who to light up red on death.
            small_dict["HARE_DEAD"] = hare_dead
            small_dict["STAG_DEAD"] = stag_dead

            points_to_send = dict(player_points)
            current_state = self.create_current_state()
            response = {}
            response = {
                "AGENT_POSITIONS": current_state,
                "POINTS": dict(points_to_send),
                "CURR_ROUND": self.round,
                "GAME_OVER": small_dict,
                "HEIGHT": HEIGHT,
                "WIDTH": WIDTH,
            }

            for i in range(4):
                for client in self.connected_clients:  # does this update the points correctly?
                    new_message = json.dumps(response).encode()
                    self.connected_clients[client].send(new_message)
                time.sleep(0.1) # slow down packet transmission.


            if self.round == self.max_rounds: #
                response = {} # clear the response I guess.
                response = { # KEEP THIS OUTSIDE TEH LOOP
                    "AGENT_POSITIONS": current_state,
                    "POINTS": dict(points_to_send),
                    "CURR_ROUND": self.round,
                    "GAME_OVER": small_dict,
                    "GAME_ENDED": True,
                    "HEIGHT": HEIGHT,
                    "WIDTH": WIDTH,
                }
                for client in self.connected_clients:  # does this update the points correctly?
                    new_message = json.dumps(response).encode()
                    self.connected_clients[client].send(new_message)
                time.sleep(2) # when game ends, give them a second to realize that it has, in fact, ended.
                return False

            else:
                self.round += 1
                self.reset_stag_hare()

    def next_round(self, rewards, new_positions, client_intent, client_time):
        for client_id in new_positions:
            client_agent = "H" + str((self.client_id_list.index(client_id))+1) # once again, off by one error
            current_position = self.stag_hare.state.agent_positions[client_agent]
            new_tuple_row = new_positions[client_id][0] + current_position[0]
            new_tuple_col = new_positions[client_id][1] + current_position[1]

            self.hunters[self.client_id_list.index(client_id)].set_next_action(new_tuple_row, new_tuple_col) # change that up
            self.hunters[self.client_id_list.index(client_id)].set_hare_hunting(client_intent[client_id])

        round_rewards = self.stag_hare.transition()
        for i, reward in enumerate(round_rewards):
            rewards[i] += reward

    def create_current_state(self):
        current_state = {}

        # Prepare current state to send to clients
        for agent in self.stag_hare.state.agent_positions:
            hidden_second_dict = {}
            hidden_second_dict["X_COORD"] = int(self.stag_hare.state.agent_positions[agent][1])
            hidden_second_dict["Y_COORD"] = int(self.stag_hare.state.agent_positions[agent][0])
            current_state[agent] = hidden_second_dict
        return current_state


    def create_hunters(self):
        new_hunters = []
        for i in range(len(self.connected_clients)): # connected clients is only the clients who are supposed to be in the game
            new_name = "H" + str(i+1)


            new_hunters.append(humanAgent(name=new_name))

        for i in range(3 - len(self.connected_clients)): # bc they always need to add up to 3
            index = 0
            new_name = "R" + str(i+1)
            agent_type = self.agentType[index]
            # different types of agents can go here, might be work making a different functioun
            if agent_type == 1:
                new_hunters.append(Random(name=new_name))
            if agent_type == 2:
                new_hunters.append(Random(name=new_name))
            # if self.agentType == 2:
            #     new_hunters.append(AlegAATr(name=new_name, lmbda=0.0, ml_model_type='knn', enhanced=True))
            # if self.agentType == 3:
            #     new_hunters.append(QAlegAATr(name=new_name, enhanced=True))
            # if self.agentType == 4:
            #     new_hunters.append(SMAlegAATr(name=new_name))
            # if self.agentType == 5:
            #     new_hunters.append(RawO(name=new_name, enhanced=True))
            index += 1 # go through the list bc we are expecting it to be an array now.



        self.hunters = new_hunters

    def find_hunter_hare(self):
        global HARE_POINTS

        hare_position = self.stag_hare.state.agent_positions["hare"]
        hare_positionX = hare_position[1]
        hare_positionY = hare_position[0]
        # we need the hare here.

        for hunter in self.stag_hare.state.agent_positions:
            if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non players. maybe. I think it might no longer split the hare points correctly.
                continue

            position = self.stag_hare.state.agent_positions[hunter]
            positionX = position[1]
            positionY = position[0]
            agent = next(agent for agent in self.stag_hare.agents if agent.name == str(hunter))
            if not (agent.is_hunting_hare()): # if we aren't hunting the hare, then don't consider us.
                continue



            if abs(positionX - hare_positionX) == 1 and positionY == hare_positionY or \
                    abs(positionY - hare_positionY) == 1 and positionX == hare_positionX:  # if they are right next to eachtoher
                small_dict = {}
                small_dict["hare"] = True
                self.worker2(hunter, self.round, small_dict)

            elif positionX == hare_positionX and (
                    (positionY == 0 and hare_positionY == HEIGHT - 1) or
                    (positionY == HEIGHT - 1 and hare_positionY == 0)
            ):  # seperated by height
                small_dict = {}
                small_dict["hare"] = True

                self.worker2(hunter, self.round, small_dict)

            elif positionY == hare_positionY and (
                    (positionX == 0 and hare_positionX == WIDTH - 1) or
                    (positionX == WIDTH - 1 and hare_positionX == 0)
            ):  # seperated by width
                small_dict = {}
                small_dict["hare"] = True

                self.worker2(hunter, self.round, small_dict)

    # given that we already know that the stag is dead, all players receive points. Much easier than hare.f
    def find_hunter_stag(self):

        for hunter in self.stag_hare.state.agent_positions:
            if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non agents.
                continue

            small_dict = {}
            small_dict["stag"] = True

            self.worker2(hunter, self.round, small_dict)

    def worker2(self, hunter_name, round, updated_states_dict):
        # Ensure player_points is a Manager dictionary
        if hunter_name not in self.player_points:
            # If the hunter doesn't exist in the dictionary, create an entry for them
            self.player_points[hunter_name] = {}

        current_entry = self.player_points[hunter_name]

        # If the round doesn't exist, create a new entry for that round
        if round not in current_entry:
            current_entry[round] = {}

        # Update the current round with "hare" and "stag" values from updated_states_dict
        if "hare" in updated_states_dict:
            current_entry[round]["hare"] = updated_states_dict["hare"]

        if "stag" in updated_states_dict:
            current_entry[round]["stag"] = updated_states_dict["stag"]

        # Using `update()` to ensure changes are reflected in the Manager dict
        self.player_points[hunter_name] = current_entry



    def reset_stag_hare(self):
        self.hunters.clear()
        self.create_hunters()

        while True:  # set up stag hunt and avoid weird edgecase
            stag_hare = StagHare(HEIGHT, WIDTH, self.hunters)
            if not stag_hare.is_over():
                break
        self.stag_hare = stag_hare

    def player_points_initialization(self):
        player_points = {}
        for hunter in self.hunters:
            if hunter.name not in player_points:
                player_points[hunter.name] = {}  # Initialize an empty dictionary for each hunter (not a list)

            for round in range(self.round, self.max_rounds + 1): # adjust that to start from round IG.
                # Directly create the round entry with "stag" and "hare" for each hunter
                current_entry = player_points[hunter.name]

                small_dict = {
                    "stag": False,
                    "hare": False,
                }
                # Directly assign the round as a key and small_dict as the value
                current_entry[round] = small_dict
                if round not in player_points[hunter.name]:
                    player_points[hunter.name] = current_entry
        self.player_points = player_points

    def adjust_points(self):
        for currRound in range(self.start_round, self.max_rounds + 1):  # if we ever don't have a player this will blow up
            hareKillers = 0
            for key in self.player_points:  # hare points first per round
                if self.player_points[key][(currRound)]["hare"] == True:
                    hareKillers += 1

            for key in self.player_points:
                if key[0] == "R":
                    del self.player_points[key][currRound] # erases the agents after we don't need them anymore.
                else:
                    if self.player_points[key][(currRound)]["hare"] == True: # only replace it if they ACTUALLY killed the hare.
                        self.player_points[key][(currRound)]["hare"] = hareKillers
        # erase agents from final dict entirely after we finish updating it.
        if "R1" in self.player_points:
            del self.player_points["R1"]
        if "R2" in self.player_points:
            del self.player_points["R2"]

        new_points = {}


        if "H1" in self.player_points:
            new_name = "H" + str(self.client_id_list[0])
            new_points[new_name] = self.player_points.pop("H1")
        if "H2" in self.player_points:
            new_name = "H" + str(self.client_id_list[1])
            new_points[new_name] = self.player_points.pop("H2")
        if "H3" in self.player_points:
            new_name = "H" + str(self.client_id_list[2])
            new_points[new_name] = self.player_points.pop("H3")

        self.player_points = new_points # don't worry about it.
        return self.player_points





# tried having this in a separate file and it just kept bricking, pulled it out and we are good to go.
class Timer:
    def __init__(self, time_limit: float = 60):
        self.start = time.time()
        self.time_limit = time_limit

    def time(self) -> float:
        return time.time() - self.start

    def time_out(self) -> bool:
        return self.time() > self.time_limit