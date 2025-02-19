# wnat to test leaderbhoard so thats the plan.
# lets get self.points as an example and try and make sure it does what I want it to do.
from gameServer import GameServer
STAG_POINTS = 20
HARE_POINTS = 10


def calc_avg_points(target_round, our_points, client_usernames):
    new_list_to_send = []  # list of tuples, holds the clientID and then the number of points that they have accrued
    new_list_to_save = []
    for key in our_points:
        curr_points = 0
        for curr_round in our_points[key]:
            if curr_round <= target_round:  # calculate only up and to the current round. IDK if it will fix our problem but we shall see.
                if our_points[key][curr_round]['stag'] == True:
                    curr_points += STAG_POINTS
                if our_points[key][curr_round]['hare'] != False:
                    curr_points += HARE_POINTS / our_points[key][curr_round]['hare']
            else:
                break

        if curr_points > 0:
            curr_points = curr_points / target_round  # just to get the average
            curr_points = round(curr_points, 2)

        # lets grab the username while we are here
        if int(key[1:]) in client_usernames:  # should always fire but just to prevent null access.
            new_tuple = (client_usernames[int(key[1])], curr_points)
            new_list_to_send.append(new_tuple)
            save_tuple = (key, curr_points)
            new_list_to_save.append(save_tuple)

    sorted_points = sorted(new_list_to_send, key=lambda x: x[1], reverse=True)
    sorted_save_tuples = sorted(new_list_to_save, key=lambda x: x[1], reverse=True)
    return sorted_points, sorted_save_tuples

current_points_dict = {
    'H1': {
        1: {'avg_points': 0, 'hare': False, 'new_points': 0, 'situation': 'A', 'stag': False},
        2: {'avg_points': 0, 'hare': 2, 'new_points': 0, 'situation': 'A', 'stag': False},
        3: {'avg_points': 0, 'hare': False, 'new_points': 0, 'situation': 'A', 'stag': False},
        4: {'avg_points': 0, 'hare': 1, 'new_points': 0, 'situation': 'A', 'stag': False},
        5: {'avg_points': 0, 'hare': False, 'new_points': 0, 'situation': 'A', 'stag': False},
        6: {'avg_points': 0, 'hare': 2, 'new_points': 0, 'situation': 'A', 'stag': False},
    },
    'H2': {
        1: {'avg_points': 0, 'hare': False, 'new_points': 20, 'situation': 'D', 'stag': True},
        2: {'avg_points': 0, 'hare': 2, 'new_points': 20, 'situation': 'D', 'stag': False},
        3: {'avg_points': 0, 'hare': False, 'new_points': 20, 'situation': 'D', 'stag': True},
        4: {'avg_points': 0, 'hare': False, 'new_points': 20, 'situation': 'D', 'stag': False},
        5: {'avg_points': 0, 'hare': 1, 'new_points': 20, 'situation': 'D', 'stag': False},
        6: {'avg_points': 0, 'hare': 2, 'new_points': 20, 'situation': 'D', 'stag': False},
    }
}


if __name__ == "__main__":
    client_usernames = {1: "H1", 2: "H2"}
    for i in range(1,7):
        points_to_send, points_to_save = calc_avg_points(i, current_points_dict, client_usernames)
        print("this is our points to send. Shoul dhave H1 with 20/6 and H2 with 10", points_to_send, "for round ", i)