# import and init pygame library
import threading
import asyncio
import pygame
import server


def start_server(loop, future):
    loop.run_until_complete(server.main(future))

def stop_server(loop, future):
    loop.call_soon_threadsafe(future.set_result, None)


loop = asyncio.get_event_loop()
future = loop.create_future()
thread = threading.Thread(target=start_server, args=(loop, future))
thread.start()

pygame.init()
pygame.fastevent.init()

# screen dimensions
HEIGHT = 320
WIDTH = 480

# set up the drawing window
screen = pygame.display.set_mode([WIDTH, HEIGHT])

color = pygame.Color('blue')
radius = 30
x = int(WIDTH/2)

# run until the user asks to quit
running = True
while running:
    # did the user close the window
    for event in pygame.fastevent.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == server.EVENTTYPE:
            print(event.message)
            color = pygame.Color('red')
            x = (x + radius / 3) % (WIDTH - radius * 2) + radius

    # fill the background with white
    screen.fill((255,255,255))

    # draw a solid blue circle in the center
    pygame.draw.circle(screen, color, (x, int(HEIGHT/2)), radius)

    # flip the display
    pygame.display.flip()

print("Stoping event loop")
stop_server(loop, future)
print("Waiting for termination")
thread.join()
print("Shutdown pygame")
pygame.quit()