usage:
`python main.py`

arguments:
    -wd: integer sets the grid world width
    -ht: integer sets the grid world height
    -na: integer sets the number of agents to spawn
    -t: tells the grid world to run headless and output data to data.csv

controls:
    arrow keys move active agent
    c: changes active agent
    v: sets active target to stag for display of paths
    b: sets active target to hare for display of paths
    0,1,2,3,4,5,6,7: selects and next action to be the corresponding generator
    t: ticks the world for all agents to move according to their predefined algorithm
    p: prints the grid to the screen
    any other key: prints the key to the screen (debug purposes only)