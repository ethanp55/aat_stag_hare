from operator import truediv




BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)

hunters = [Random(name='R1'), Random(name='R2'), humanAgent(name='H')]
# hunters = [AlegAATr(name='R1', lmbda=0.0, ml_model_type='knn', enhanced=True),
#            AlegAATr(name='R2', lmbda=0.0, ml_model_type='knn', enhanced=True),
#            humanAgent(name='H')]
# hunters = [DQNAgent(name='R1'),
#            DQNAgent(name='R2'),
#            humanAgent(name='H')]


SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.
from pygame.locals import ( # gets us the four caridnal directions for movement from the user.
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
)


def main():
    this_player = player.Player("player", HEIGHT, WIDTH)
    stag = enemy.Enemy("stag", HEIGHT, WIDTH)
    hare = enemy.Enemy("hare", HEIGHT, WIDTH)
    agent1 = enemy.Enemy("agent1", HEIGHT, WIDTH)
    agent2 = enemy.Enemy("agent2", HEIGHT, WIDTH)

    pygame.init()  # actually starts the game.
    running = True
    rewards = [0] * (len(hunters) + 2)



    while True:
        stag_hare = StagHare(HEIGHT, WIDTH, hunters)
        if not stag_hare.is_over():
            break

    while running:  #and not stag_hare.is_over(): # make sure that we aren't over

        draw_grid(HEIGHT, WIDTH)

        state = stag_hare.return_state()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                pressed_keys = pygame.key.get_pressed()

                new_row, new_col = set_player_position(pressed_keys, state)
                hunters[-1].set_next_action(new_row, new_col)

                round_rewards = stag_hare.transition()

                # Update rewards
                for i, reward in enumerate(round_rewards):
                    rewards[i] += reward


            for agent in state.agent_positions:
                if agent == 'hare':
                    hare.update(SCREEN, state.agent_positions[agent])
                if agent == "stag":
                    stag.update(SCREEN, state.agent_positions[agent])
                if agent == "R1":
                    agent1.update(SCREEN, state.agent_positions[agent])
                if agent == "R2":
                    agent2.update(SCREEN, state.agent_positions[agent])
                if agent == "H":
                    #current_position = (3,2)
                    #this_player.update(SCREEN, current_position)
                    this_player.update(SCREEN, state.agent_positions[agent])


            pygame.display.update()

            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:  # gives us a way to stop execution.
                    running = False

        if stag_hare.is_over():
            if stag_hare.state.hare_captured():
                hare.update(SCREEN, state.agent_positions["hare"], True)
            else:
                stag.update(SCREEN, state.agent_positions["stag"], True)
            pygame.display.update()
            time.sleep(PAUSE_TIME)
            running = False


def draw_grid(height, width): # draws the grid on every frame just so we have it.
    SCREEN.fill(WHITECOLOR)
    widthOffset = (SCREEN_WIDTH / width)
    heightOffset = (SCREEN_HEIGHT / height)
    for x in range(0, width):
        for y in range(0, height):
            rect = pygame.Rect(x*widthOffset, y*heightOffset, widthOffset, heightOffset)
            pygame.draw.rect(SCREEN, BLACKCOLOR, rect, 1)



def set_player_position(pressed_keys, state):

    curr_row, curr_col = state.agent_positions["H"] # because thats the name of the human player
    if pressed_keys[K_UP]:
        curr_row -= 1
    if pressed_keys[K_DOWN]:
        curr_row += 1  # move down
    if pressed_keys[K_LEFT]:
        curr_col -= 1  # move left
    if pressed_keys[K_RIGHT]:
        curr_col += 1  # move right

    return curr_row, curr_col

if __name__ == '__main__':
    main()
