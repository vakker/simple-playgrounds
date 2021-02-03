"""
Game Engine manages the interacitons between agents and Playgrounds.
"""
import numpy as np

import pygame
from pygame.locals import K_q, K_r  # pylint: disable=no-name-in-module
from pygame.color import THECOLORS  # pylint: disable=no-name-in-module
import matplotlib.pyplot as plt

import cv2

from simple_playgrounds.utils.definitions import SensorModality, SIMULATION_STEPS, ActionTypes


class Engine:

    """
    Engine manages the interactions between agents and a playground.

    """

    # pylint: disable=too-many-function-args
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes

    def __init__(self, playground, time_limit=None, replay=False, screen=False):

        """

        Args:
            playground (:obj: 'Playground): Playground where the agents will be placed
            time_limit (:obj: 'int'): Total number of timesteps.
            replay (:obj: 'bool'): Restarts upon termination, until time_limit is reached.
                Default: False
            screen: If True, a pygame screen is created for display.
                Default: False

        Note:
            A pygame screen is created by default if one agent is controlled by Keyboard.
            You can reset the game by using R key, and terminate it using Q key.

        """

        # Playground already exists
        self.playground = playground

        self.agents = self.playground.agents

        # Rules
        self.replay_until_time_limit = replay

        self.time_limit = time_limit
        if time_limit is None:
            self.time_limit = self.playground.time_limit

        assert isinstance(self.time_limit, int)

        # Display screen

        self.screen = None
        if screen:
            # Screen for Pygame
            self.screen = pygame.display.set_mode((self.playground.width, self.playground.length))
            self.screen.set_alpha(None)
            self.quit_key_ready = True
            self.reset_key_ready = True

        # Pygame Surfaces to display the environment
        self.surface_background = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_environment = pygame.Surface((self.playground.width, self.playground.length))
        self.surface_sensors = pygame.Surface((self.playground.width, self.playground.length))

        self.surface_background.fill(THECOLORS["black"])

        for elem in self.playground.scene_elements:
            if elem.background:
                elem.draw(self.surface_background, )

        self.game_on = True
        self.elapsed_time = 0

    def multiple_steps(self, actions, n_steps=1):
        """
        Runs multiple steps of the game, with the same actions for the agents.
        Perforns Interactive (eat and activate) actions oly at the last timestep.

        Args:
            actions: Dictionary containing the actions for each agent.
            n_steps: Number of consecutive steps where the same actions will be applied

        """
        hold_actions = {}
        last_action = {}

        reset = False
        terminate = False

        for agent_name, agent_actions in actions.items():
            hold_actions[agent_name] = {}
            last_action[agent_name] = {}

            for actuator, value in agent_actions.items():

                last_action[agent_name][actuator] = value
                hold_actions[agent_name][actuator] = value

                if actuator.action in [ActionTypes.ACTIVATE, ActionTypes.EAT]:
                    hold_actions[agent_name][actuator] = 0

        cumulated_rewards = {}
        for agent_name in actions:
            cumulated_rewards[agent_name] = 0

        step = 0
        continue_actions = True

        while step < n_steps and continue_actions:

            if step < n_steps-1:
                action = hold_actions
            else:
                action = last_action

            self._engine_step(action)

            for agent in self.agents:
                cumulated_rewards[agent.name] += agent.reward

            step += 1

            reset, terminate = self._handle_terminations()

            if reset or terminate:
                continue_actions = False

        for agent in self.agents:
            agent.reward = cumulated_rewards[agent.name]

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return reset, terminate

    def step(self, actions):
        """
        Runs a single steps of the game, with the same actions for the agents.

        Args:
            actions: Dictionary containing the actions for each agent.

        """

        self._engine_step(actions)

        # Termination
        reset, terminate = self._handle_terminations()

        if self._reached_time_limit() and self.playground.time_limit_reached_reward is not None:
            for agent in self.agents:
                agent.reward += self.playground.time_limit_reached_reward

        return reset, terminate

    def _handle_terminations(self):

        reset = False
        terminate = False

        playground_terminated = self.playground.done
        reached_time_limit = self._reached_time_limit()
        keyboard_reset, keyboard_quit = self._check_keyboard()

        if keyboard_quit:
            terminate = True

        elif keyboard_reset:
            reset = True

        elif playground_terminated:

            if self.replay_until_time_limit:
                reset = True

            else:
                terminate = True

        elif reached_time_limit:
            terminate = True

        return reset, terminate

    def _engine_step(self, actions):

        for agent in self.agents:
            agent.apply_actions_to_body_parts(actions[agent.name])

        self.playground.update(SIMULATION_STEPS)

        self.elapsed_time += 1

    def reset(self):
        """
        Resets the game to its initial state.

        """
        self.playground.reset()
        self.game_on = True

    def _reached_time_limit(self):
        if self.elapsed_time >= self.time_limit:
            return True
        else:
            return False

    def _check_keyboard(self):
        """
        Tests whether the game came to an end, because of time limit or termination of playground.

        Returns:
            True if the game is terminated
            False if the game continues
        """
        reset_game = False
        terminate_game = False

        if self.screen is not None:

            pygame.event.get()

            # Press Q to terminate
            if pygame.key.get_pressed()[K_q] and self.quit_key_ready is False:
                self.quit_key_ready = True

            elif pygame.key.get_pressed()[K_q] and self.quit_key_ready is True:
                self.quit_key_ready = False

                terminate_game = True

            # Press R to reset
            if pygame.key.get_pressed()[K_r] and self.reset_key_ready is False:
                self.reset_key_ready = True

            elif pygame.key.get_pressed()[K_r] and self.reset_key_ready is True:
                self.reset_key_ready = False

                reset_game = True

        return reset_game, terminate_game

    def update_surface_background(self):
        # Check that some background elements maybe need to be drawn
        for element in self.playground.scene_elements:
            if element.background and not element.drawn:
                element.draw(self.surface_background, )

    def update_surface_environment(self):
        """
        Draw all agents and entities on the surface environment.
        Additionally, draws the interaction areas.

        """
        self.update_surface_background()
        self.surface_environment.blit(self.surface_background, (0 ,0) )

        for entity in self.playground.scene_elements:

            if not entity.background or entity.graspable or entity.interactive :
                entity.draw(self.surface_environment, )

        for agent in self.agents:
            agent.draw(self.surface_environment, )

    def update_observations(self):
        """
        Updates observations of each agent

        """

        for agent in self.agents:

            for sensor in agent.sensors:

                if sensor.sensor_modality is SensorModality.VISUAL:

                    self.update_surface_background()
                    self.surface_sensors.blit(self.surface_background, (0, 0))
                    sensor.update(playground=self.playground, sensor_surface=self.surface_sensors)

                elif sensor.sensor_modality is SensorModality.ROBOTIC \
                        or sensor.sensor_modality is SensorModality.SEMANTIC:
                    sensor.update(playground=self.playground)

                else:
                    raise ValueError

    @staticmethod
    def distance_elem(elem_1, elem_2):

        return ((elem_1.position[0] - elem_2.position[0])**2 + (elem_1.position[1] - elem_2.position[1])**2)**(1/2)

    def display_full_scene(self):
        """
        If the screen is set, updates the screen and displays the environment.

        """

        if self.screen is not None:

            self.update_surface_environment()

            rot_surface = pygame.transform.rotate(self.surface_environment, 180)
            self.screen.blit(rot_surface, (0, 0), None)

            pygame.display.flip()

        else:
            raise ValueError

    def generate_topdown_image(self, max_size=None, mode=None):
        """
        Updates the Environment Surface and convert it into an array.
        Color code follows OpenCV

        Returns:

        """

        self.update_surface_environment()

        np_image = pygame.surfarray.pixels3d(self.surface_environment.copy())
        np_image = np.rot90(np_image, 1, (1, 0))
        np_image = np_image[::-1, :, ::-1]

        if max_size is not None:

            scaling_factor = max_size/max(np_image.shape[0], np_image.shape[1])
            np_image = cv2.resize(np_image, None, fx = scaling_factor, fy = scaling_factor)

        if mode == 'plt':
            np_image = np_image[:, :, ::-1]

        return np_image

    def generate_sensor_image(self, agent, width_sensor=200, height_sensor=30, mode=None):
        """
        Generate a full image contaning all the sensor representations of an Agent.
        Args:
            agent: Agent
            width_sensor: width of the display for drawing.
            height_sensor: when applicable (1D sensor), the height of the display.
            mode: None or plt. plt is used to draw images with pyplot.

        Returns:

        """

        border = 5

        list_sensor_images = []
        for sensor in agent.sensors:
            list_sensor_images.append(sensor.draw(width_sensor, height_sensor))

        full_height = sum([im.shape[0] for im in list_sensor_images]) + len(list_sensor_images)*(border+1)

        full_img = np.ones((full_height, width_sensor, 3)) * 0.2

        current_height = 0
        for im in list_sensor_images:
            current_height += border
            full_img[current_height:im.shape[0] + current_height, :, :] = im[:, :, :]
            current_height += im.shape[0]

        if mode == 'plt':
            full_img = full_img[:, :, ::-1]

        return full_img

    def generate_state_image(self, agent):

        state_width = 200
        text_box_height = 30
        h_space = 5
        offset_string = 10

        number_parts_with_actions = len(agent.parts)
        count_all_actions = len(agent.current_actions)

        state_height = (text_box_height + h_space)*(count_all_actions + number_parts_with_actions) - h_space

        current_height = text_box_height

        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 0.5 #height_slot - 2 * space_string
        fontColor = (0, 0, 0)
        lineType = 1

        img_state = np.ones((state_height, state_width, 4))*255

        # for action, value in agent.current_actions.items():
        #
        #     print(action, value)

        # for action, value in agent.current_actions.items():
        #
        #     center = 100 - int(10*len(part_name)/2)
        #
        #     bottomLeftCornerOfText = (center, current_height-offset_string)
        #
        #     cv2.putText(img_state, part_name.upper(),
        #                 bottomLeftCornerOfText,
        #                 font,
        #                 fontScale,
        #                 fontColor,
        #                 lineType)
        #
        #     img_state = cv2.rectangle(img_state, (3, current_height-3), (state_width-3, current_height - text_box_height+3), (0,0,0), 3)
        #
        #
        #     current_height += text_box_height + h_space
        #
        #
        #     for action_index in range(1, len(ActionTypes)+1):
        #
        #         if ActionTypes(action_index) in actions:
        #
        #
        #             action_value = actions[ActionTypes(action_index)]
        #             action_name = ActionTypes(action_index).name
        #
        #             center = 100 - int(8 * len(action_name) / 2)
        #
        #             bottomLeftCornerOfText = (center, current_height - offset_string)
        #
        #             cv2.putText(img_state, action_name.lower(),
        #                         bottomLeftCornerOfText,
        #                         font,
        #                         fontScale,
        #                         fontColor,
        #                         lineType)
        #
        #
        #             # img_state = cv2.rectangle(img_state, (3, current_height - 3),
        #             #                           (state_width - 3, current_height - text_box_height + 3), (0, 0, 0), 3)
        #
        #             current_height += text_box_height + h_space
        #
        img_state = cv2.cvtColor(img_state.astype('float32'), cv2.COLOR_RGBA2BGR)

        return img_state

    def generate_agent_image(self, agent,
                             with_pg = True, max_size_pg = 400, rotate_pg=False,
                             with_state = True,
                             with_sensors = True, sensor_width = 150, sensor_height = 30, mode = None):

        border = 10

        images = []

        if with_pg:
            pg_image = self.generate_topdown_image( max_size = max_size_pg )

            if rotate_pg:
                pg_image = np.rot90(pg_image)


            images.append(pg_image)

        if with_state:
            state_image = self.generate_state_image(agent)
            images.append(state_image)

        if with_sensors:
            sensor_image = self.generate_sensor_image(agent, sensor_width, sensor_height)
            images.append(sensor_image)


        full_image_width = sum( [img.shape[1] + border for img in images ]) + border
        full_image_height = max( [img.shape[0] for img in images ] ) + 2*border

        full_img = np.ones((full_image_height, full_image_width, 3))*255

        current_width = border

        for img in images:
            full_img[border: border+img.shape[0], current_width:current_width + img.shape[1],:] = img[:, :, :]
            current_width += img.shape[1] + border

        if mode == 'plt':
            full_img = full_img[:, :, ::-1]

        return full_img



    def run(self, steps=None, with_screen=False, print_rewards=False):
        """ Run the engine for the full duration of the game"""

        continue_for_n_steps = True

        while self.game_on and continue_for_n_steps:

            actions = {}
            for agent in self.agents:
                actions[agent.name] = agent.controller.generate_commands()

            reset, terminate = self.step(actions)
            self.update_observations()

            if with_screen and self.game_on:
                self.display_full_scene()
                pygame.time.wait(30)

            if print_rewards:
                for agent in self.agents:
                    if agent.reward != 0:
                        print(agent.name, ' got reward ', agent.reward)

            if steps is not None:
                steps -= 1
                if steps == 0:
                    continue_for_n_steps = False

            if reset:
                self.reset()

            if terminate:
                continue_for_n_steps = False
                self.terminate()

    def terminate(self):

        self.game_on = False
        pygame.quit()
