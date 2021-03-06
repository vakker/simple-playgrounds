""" Module implementing Platform.

A Platform is a Part which serves as the base to attach other Links.
Platform is controlled by longitudinal or lateral force, and angular velocity.
"""

from abc import ABC

import pymunk

from simple_playgrounds.agents.parts.part import Part, Actuator
from simple_playgrounds.utils.definitions import ActionTypes, AgentPartTypes
from simple_playgrounds.utils.parser import parse_configuration

# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods


class Platform(Part, ABC):
    """
    Base class for Platforms.
    Inherits from Part.
    An agent requires a Platform to build its body.

    """

    entity_type = AgentPartTypes.PLATFORM

    def __init__(self, **kwargs):
        """

        Args:
            **kwargs: optional additional parameters

        Keyword Args:
            physical_shape (str): circle, square, pentagon, hexagon. Default: circle.
            texture (:obj: 'dict': dictionary of texture parameters.
            radius: radius of the platform. Default: 20.
            mass: mass of the platform. Default: 15.
            max_linear_force: Maximum longitudinal and lateral force. Default: 0.3.
            max_angular_velocity: Maximum angular velocity (radian per timestep). Default: 0.25.
        """

        default_config = parse_configuration('agent_parts', self.entity_type)
        body_part_params = {**default_config, **kwargs}

        Part.__init__(self, **body_part_params)

        self.max_linear_force = body_part_params['max_linear_force']
        self.max_angular_velocity = body_part_params['max_angular_velocity']


class FixedPlatform(Platform):
    """
        Platform that is fixed.
        Can be used to build Arms with fixed base.
        Refer to the base class Platform.

    """

    movable = False


class ForwardPlatform(Platform):
    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.longitudinal_force_actuator = Actuator(self.name, ActionTypes.LONGITUDINAL_FORCE,
                                                    ActionTypes.CONTINUOUS_NOT_CENTERED, 0, 1)
        self.actuators.append(self.longitudinal_force_actuator)

        self.angular_velocity_actuator = Actuator(self.name, ActionTypes.ANGULAR_VELOCITY,
                                                  ActionTypes.CONTINUOUS_CENTERED, -1, 1)
        self.actuators.append(self.angular_velocity_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        value = self._check_value_actuator(actuator, value)

        if actuator is self.longitudinal_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(value, 0) * self.max_linear_force * 100, (0, 0))

        if actuator is self.angular_velocity_actuator:
            self.pm_body.angular_velocity = - value * self.max_angular_velocity

        return value


class ForwardBackwardPlatform(ForwardPlatform):
    """
    Platform that can move forward and rotate.
    Refer to the base class Platform.

    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.actuators.remove(self.longitudinal_force_actuator)

        self.longitudinal_force_actuator = Actuator(self.name, ActionTypes.LONGITUDINAL_FORCE, ActionTypes.CONTINUOUS_CENTERED, -1, 1)
        self.actuators.append(self.longitudinal_force_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        value = self._check_value_actuator(actuator, value)

        if actuator is self.longitudinal_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(value, 0) * self.max_linear_force * 100, (0, 0))

        if actuator is self.angular_velocity_actuator:
            self.pm_body.angular_velocity = - value * self.max_angular_velocity

        return value


class HolonomicPlatform(ForwardBackwardPlatform):
    """
    Platform that can translate in all directions, and rotate.
    Refer to the base class Platform.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.lateral_force_actuator = Actuator(self.name, ActionTypes.LATERAL_FORCE, ActionTypes.CONTINUOUS_CENTERED, -1, 1)
        self.actuators.append(self.lateral_force_actuator)

    def apply_action(self, actuator, value):

        super().apply_action(actuator, value)
        value = self._check_value_actuator(actuator, value)

        if actuator is self.lateral_force_actuator:
            self.pm_body.apply_force_at_local_point(pymunk.Vec2d(0, -value) * self.max_linear_force * 100, (0, 0))

        return value
