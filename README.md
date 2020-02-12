To install: 
(sudo) pip install -e /path/to/package



# flatland
New version of flatland.

# TODO General:
- documentation
- safeguard
- jupyter notebook / colab compatible
- install pipy and pip
- visualization agent, fpv, topdown view
- harmonize view (carthesian) and coordinates
- video recording
- log/print important messages (reset, ...)
- one starting position per agent
- clarify room shape, scene shape
- noise


# Game engine
- config file
- start position: random in area (circle, square, gaussian), random pick in list positions, random pick in list areas
- fixed, list_fixed, area, list_areas
- each playground should suggest starting positions
- also random position for object placements
- basic environments
- change default parameters and use config / yaml ?
- teleport agent to position (and set all agent speeds to zero)
- add cost of activation / grasp for objects
- remove entity-frame

# Todo PG:
- Scene layouts linear, array, random maze
- test pg with all items
- walls of random colors / one color per wall 
- random position: weighted list of areas
- check if position valid

# TODO RL:
- wrapper openai & gym
- wrapper library state representation
- parallel vector agents and environments


# TODO:
- Replace Ctr+q with clean exiting which doesnt require a pygame display
- Add a cost of activation for actionable objects ?

# TODO agents:
- add rbgd, depth, rbg-limited_view, top-down
- Modify metabolism, harmonize name for head_velocity, head_speed, ... and computation of energy
- focus on single agent
- merge sm-agent

# TODO Gui
- one window per agent with sensors and reward
- integration with ipynb

# TODO Edible:
- Make one mask, keep it.
- Cut the projection instead, so that image is kept, and it is easier to handle