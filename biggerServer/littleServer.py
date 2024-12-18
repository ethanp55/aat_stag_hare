# this holds the actual instance of stag hunt, only runs 1 round based on scheduling. run this and then return the new dicts that we need to append to the large dicts up above.
import select
import json

import time # tit for tat pausing?
from server.udpServer import connected_clients

PAUSE_TIME = 3
HEIGHT = 15
WIDTH = 15

from agents.random_agent import *
from agents.human import *
from environment.world import StagHare


class gameInstance():
    def __init__(self, connected_clients, client_id_dict, player_points, agentType, round=0, max_rounds=1):
        self.connected_clients = connected_clients
        self.client_id_dict = client_id_dict
        self.agentType = agentType
        self.create_hunters()
        self.player_points = player_points
        self.max_rounds = max_rounds # have it be 1 if nothing is given, just becuase.
        self.HUMAN_PLAYERS = len(connected_clients)
        self.AI_AGENTS = 3 - self.HUMAN_PLAYERS
        self.round = round # start with round 1, but I should probably make it an actual thinger so I can keep track of it better.
        while True:  # set up stag hunt and avoid weird edgecase
            stag_hare = StagHare(HEIGHT, WIDTH, self.hunters)
            if not stag_hare.is_over():
                break
        self.stag_hare = stag_hare  # just to have that down.
        self.main_game_loop()


    def main_game_loop(self):
        while True:
            client_input = {}
            while True:
                self.send_state()  # sends out the current game state
                data = self.get_client_data()
                for client, received_json in data.items():
                    if "NEW_INPUT" in received_json and received_json["NEW_INPUT"] != None:
                        client_input[self.client_id_dict[client]] = received_json["NEW_INPUT"]
                        print(f"Received input from {client}: {received_json['NEW_INPUT']}")
                # Check if all clients have provided input
                if len(client_input) == len(self.connected_clients):
                    break
            print("All clients have provided input. continuing")


            running = self.stag_hunt_game_loop(self.player_points, client_input)
            if running == False:
                break
            client_input.clear()

    def send_state(self):
        current_state = self.create_current_state()
        send_player_points = self.player_points.copy()
        for client in self.connected_clients:
            client_id = self.client_id_dict[self.connected_clients[client]]
            response = {
                "CLIENT_ID": client_id,
                "AGENT_POSITIONS": current_state,
                "POINTS": send_player_points,
                "CURR_ROUND": self.round,
            }

            new_message = json.dumps(response).encode()
            self.connected_clients[client].send(new_message)

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

    def stag_hunt_game_loop(self, player_points, player_input):

        rewards = [0] * (len(self.hunters) + 2)

        self.next_round(rewards, player_input)

        self.send_state()

        if self.stag_hare.is_over():
            timer = Timer(2) # well fetch thats not going to get fixed is it.
            hare_dead = False
            stag_dead = False
            while True:

                print("*************GAME OVER************")
                print("HERE Are the current playre points", player_points)

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
                for client in self.connected_clients:  # does this update the points correctly?
                    client_id = self.client_id_dict[self.connected_clients[client]]
                    response = {
                        "CLIENT_ID": client_id,
                        "AGENT_POSITIONS": current_state,
                        "POINTS": dict(points_to_send),
                        "CURR_ROUND": self.round,
                        "GAME_OVER": small_dict,
                    }

                    new_message = json.dumps(response).encode()
                    self.connected_clients[client].send(new_message)

                if timer.time_out(): # import timer at some point.
                    break

            if self.round == self.max_rounds: #
                for client in self.connected_clients:  # does this update the points correctly?
                    client_id = self.client_id_dict[self.connected_clients[client]]
                    response = {
                        "CLIENT_ID": client_id,
                        "AGENT_POSITIONS": current_state,
                        "POINTS": dict(points_to_send),
                        "CURR_ROUND": self.round,
                        "GAME_OVER": small_dict,
                        "GAME_ENDED": True,
                    }

                    new_message = json.dumps(response).encode()
                    self.connected_clients[client].send(new_message)
                print("GAME OVER")
                time.sleep(PAUSE_TIME)
                return False

            else:
                self.round += 1
                self.reset_stag_hare()

    def next_round(self, rewards, new_positions):
        for client_id in new_positions:
            client_agent = "H" + str(client_id)
            current_position = self.stag_hare.state.agent_positions[client_agent]
            new_tuple_row = new_positions[client_id][0] + current_position[0]
            new_tuple_col = new_positions[client_id][1] + current_position[1]
            self.hunters[client_id - 1].set_next_action(new_tuple_row, new_tuple_col)
            print(f"this is the client_ID, {client_id}")

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
            new_name = "R" + str(i+1)
            # different types of agents can go here, might be work making a different functioun
            if self.agentType == 1:
                new_hunters.append(Random(name=new_name))

        self.hunters = new_hunters

    def find_hunter_hare(self):
        global HARE_POINTS
        print("distributing points")
        hare_position = self.stag_hare.state.agent_positions["hare"]
        hare_positionX = hare_position[1]
        hare_positionY = hare_position[0]
        # we need the hare here.
        print("here is the hare position", hare_positionY, ",", hare_positionX)
        for hunter in self.stag_hare.state.agent_positions:
            if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non agents.
                continue

            position = self.stag_hare.state.agent_positions[hunter]
            positionX = position[1]
            positionY = position[0]
            print("here is the position of the agent that we think ", positionY, ",", positionX)

            if abs(positionX - hare_positionX) == 1 and positionY == hare_positionY or \
                    abs(positionY - hare_positionY) == 1 and positionX == hare_positionX:  # if they are right next to eachtoher
                small_dict = {}
                small_dict["hare"] = True
                print("Hunter ", hunter, " was given hare points! next to eachtoher no diff")
                self.worker2(hunter, self.round, small_dict)

            elif positionX == hare_positionX and (
                    (positionY == 0 and hare_positionY == HEIGHT - 1) or
                    (positionY == HEIGHT - 1 and hare_positionY == 0)
            ):  # seperated by height
                small_dict = {}
                small_dict["hare"] = True
                print("Hunter ", hunter, " was given hare points! shot around wall left or right")
                self.worker2(hunter, self.round, small_dict)

            elif positionY == hare_positionY and (
                    (positionX == 0 and hare_positionX == WIDTH - 1) or
                    (positionX == WIDTH - 1 and hare_positionX == 0)
            ):  # seperated by width
                small_dict = {}
                small_dict["hare"] = True
                print("Hunter ", hunter, " was given hare points! shot thorugh celing or floor")
                self.worker2(hunter, self.round, small_dict)

    # given that we already know that the stag is dead, all players receive points. Much easier than hare.f
    def find_hunter_stag(self):
        print("distributing points")
        for hunter in self.stag_hare.state.agent_positions:
            if not hunter[0] == "H" and not hunter[0] == "R":  # should filter out all non agents.
                continue

            small_dict = {}
            small_dict["stag"] = True

            self.worker2(hunter, self.round, small_dict)
            print("Hunter ", hunter, " was given stag points!")

    def worker2(self, hunter_name, round, updated_states_dict):
        print("updated states dict ", updated_states_dict)

        if hunter_name not in self.player_points:
            # If the hunter doesn't exist in the dictionary, create an entry for them
            self.player_points[hunter_name] = {}

        current_entry = self.player_points[hunter_name]

        # If the round doesn't exist, create a new entry for that round
        if self.round not in current_entry:
            current_entry[self.round] = {}

        # Check if "hare" is in the updated states dict and add it if necessary
        if "hare" in updated_states_dict:
            current_entry[round]["hare"] = updated_states_dict["hare"]

        # Check if "stag" is in the updated states dict and add it if necessary
        if "stag" in updated_states_dict:
            current_entry[round]["stag"] = updated_states_dict["stag"]

        # After updating the round, save it back to the dictionary
        self.player_points[hunter_name] = current_entry

        print("post update states dict ", self.player_points)

    def reset_stag_hare(self):
        self.hunters.clear()
        self.create_hunters()

        while True:  # set up stag hunt and avoid weird edgecase
            stag_hare = StagHare(HEIGHT, WIDTH, self.hunters)
            if not stag_hare.is_over():
                break
        self.stag_hare = stag_hare



# tried having this in a separate file and it just kept bricking, pulled it out and we are good to go.
class Timer:
    def __init__(self, time_limit: float = 60):
        self.start = time.time()
        self.time_limit = time_limit

    def time(self) -> float:
        return time.time() - self.start

    def time_out(self) -> bool:
        return self.time() > self.time_limit