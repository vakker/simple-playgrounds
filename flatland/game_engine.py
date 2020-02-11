import pygame
from pygame.locals import K_q
from flatland.utils.config import *
import time
import cv2

import os
# Center the pygame window and make it pop up
os.environ['SDL_VIDEO_CENTERED'] = '1'


class Engine():

    def __init__(self, playground, agents, rules, engine_parameters):

        '''
        Engine binds a playground, a list of agents, and rules of the game.

        :param playground: a Playground object where agents will play
        :param agents: a list of Agent objects
        :param rules: a dict with the rules of the game
        :param engine_parameters
        '''

        # Playground already exists
        self.playground = playground

        # Add agents to the playground
        self.agents = agents
        for agent in self.agents:
            self.playground.add_agent(agent)

        # Rules for the simulation
        self.replay_until_time_limit = rules.get('replay_until_time_limit', False)
        self.time_limit = rules.get('time_limit', 1000)

        # Engine parameters
        self.inner_simulation_steps = engine_parameters.get('inner_simulation_steps', SIMULATION_STEPS)
        self.display_mode = engine_parameters.get('display_mode', None)


        # Display screen
        self.need_command_display = False
        for agent in self.agents:
            if agent.controller.type == 'keyboard':
                self.need_command_display = True

        if self.need_command_display:
            self.command = pygame.display.set_mode((75, 75))
            self.Q_ready_to_press = True

        # Screen for Pygame
        self.screen = pygame.Surface((self.playground.length, self.playground.width))
        self.screen.set_alpha(None)

        # Initialize time counters and reset trigger variable
        self.game_on = True
        self.current_elapsed_time = 0
        self.total_elapsed_time = 0



    def update_observations(self):

        '''
        Updates the sensors of each agent in the playground.
        '''

        # TODO: Compute environment image once, then add agents when necessary

        # For each agent, compute sensors
        for agent in self.agents:
            img = self.playground.generate_playground_image(sensor_agent = agent)
            agent.compute_sensors(img)


    def step(self, actions):

        '''
        Game engine runs step by step. All simulation logic is concentrated here.
        '''

        # Make agents perform their actions
        # N.B.: agents take their actions in turn
        for agent in self.agents:
            # Initialization before action
            agent.pre_step()

            # Make the agent perform its actions
            agent.apply_action_to_physical_body( actions[agent.name] )

        # Inner simulation steps
        for _ in range(self.inner_simulation_steps):
            self.playground.space.step(1. / self.inner_simulation_steps)

        # Update agents' health total
        for agent in self.agents:
            agent.health += (agent.reward - agent.energy_spent)

        # Update elements of the playground
        self.playground.update_playground()

        # Termination if necessary
        if self.game_terminated():
            # Reset if necessary
            if self.replay_until_time_limit and self.total_elapsed_time < self.time_limit:
                self.game_reset()

            else:
                self.game_on = False

        # Update time counters
        self.total_elapsed_time += 1
        self.current_elapsed_time += 1

    def game_terminated(self):

        '''
        Checks if endgame conditions are satisfied or not.
        '''

        if self.current_elapsed_time == self.time_limit:
            return True

        if self.playground.has_reached_termination:
            return True


        if self.need_command_display:
            if not pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == False:
                self.Q_ready_to_press = True

            elif (pygame.key.get_pressed()[K_q] and self.Q_ready_to_press == True) :
                self.Q_ready_to_press = False
                return True

        return False

    def generate_playground_image(self):

        '''
        Creates the image corresponding to the simulation's state.
        '''

        img = self.playground.generate_playground_image(draw_interaction=True)
        return img

    """def display_full_scene(self):

        img = self.generate_playground_image()
        surf = pygame.surfarray.make_surface(img)
        self.screen.blit(surf, (0, 0), None)

        pygame.display.flip()"""

    def render_simulation(self, sensors=True, actions=True):

        '''
        Displays the simulation in a new window.
        '''


        img = self.generate_playground_image()
        cv2.imshow('Flatland Simulation', img)
        cv2.waitKey(15)

        if sensors:
            pass

        if actions:
            pass



    def game_reset(self):

        '''
        Resets the simuation.
        '''


        self.current_elapsed_time = 0

        self.playground.remove_agents()
        self.playground.reset()

        for agent in self.agents:
            self.playground.add_agent(agent)

    def terminate(self):

        '''
        Terminates the simulation properly.
        '''

        pygame.display.quit()
