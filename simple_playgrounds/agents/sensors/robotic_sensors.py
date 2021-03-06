""" Module implementing robotic sensors: Cameras, Lidar, touch sensing.

These sensors are very close to physical sensors that could be used on real robots.
These sensors can be noisy.
Importantly, as Simple-Playgrounds is a 2D environments, these sensors are 1D.
"""

import math
from operator import attrgetter

import numpy as np
import cv2

from simple_playgrounds.agents.sensors.sensor import RayCollisionSensor
from simple_playgrounds.utils.definitions import SensorTypes

# pylint: disable=no-member


class RgbCamera(RayCollisionSensor):
    """
    Provides a 1D image (line of RGB pixels) from the point of view of the anchor.
    """

    sensor_type = SensorTypes.RGB

    def __init__(self, anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 **sensor_params):

        super().__init__(anchor=anchor, invisible_elements=invisible_elements,
                         normalize=normalize, noise_params=noise_params,
                         remove_duplicates=False, remove_occluded=False,
                         **sensor_params)

        self._sensor_max_value = 255

    def _compute_raw_sensor(self, playground, *_):

        collision_points = self._compute_points(playground)

        pixels = np.zeros((self._resolution, 3))

        for angle_index, ray_angle in enumerate(self._ray_angles):

            collisions = collision_points[ray_angle]

            if collisions:

                col = min(collisions, key=attrgetter('alpha'))

                elem_colliding = playground.get_entity_from_shape(pm_shape=col.shape)

                angle_element = elem_colliding.position[2]
                pos_element = elem_colliding.position[0:2]

                col_x, col_y = playground.size[0] - col.point.y, col.point.x
                rel_x, rel_y = col_x - pos_element[0], col_y - pos_element[1]

                rel_pos_point = (rel_x*math.cos(angle_element) + rel_y*math.sin(angle_element),
                                 - rel_x*math.sin(angle_element) + rel_y*math.cos(angle_element))

                coord = (int(rel_pos_point[1]+(elem_colliding.texture_surface.get_size()[1]-1)/2),
                         int(rel_pos_point[0]+(elem_colliding.texture_surface.get_size()[0]-1)/2)
                         )

                rgb = elem_colliding.texture_surface.get_at(coord)[:3]

                pixels[angle_index] = rgb

        pixels = pixels[::-1, ::-1]

        self.sensor_values = pixels

    def _apply_normalization(self):
        self.sensor_values /= 255.

    @property
    def shape(self):
        return self._resolution, 3

    def draw(self, width, height):
        """
        Function that creates an image for visualizing a sensor.

        Args:
            width: width of the image
            height: height of the rendered 1D sensor

        Returns:
            Numpy array containing the visualization of the sensor values.
        """

        img = np.expand_dims(self.sensor_values, 0)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)
        if not self._normalize:
            img /= 255.

        return img


class GreyCamera(RgbCamera):
    """
    Provides a 1D image (line of Grey-level pixels) from the point of view of the anchor.
    """

    sensor_type = SensorTypes.GREY

    def _compute_raw_sensor(self, playground, *_):
        super()._compute_raw_sensor(playground)
        self.sensor_values = np.dot(self.sensor_values[..., :3], [0.114, 0.299, 0.587])

    @property
    def shape(self):
        return self._resolution

    def draw(self, width, height):

        expanded = np.zeros((self.shape, 3))

        for i in range(3):
            expanded[:, i] = self.sensor_values[:]
        img = np.expand_dims(expanded, 0)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)

        if not self._normalize:
            img /= 255.

        return img


class Lidar(RayCollisionSensor):
    """
    Lidar are Sensors that measure distances by projecting rays.
    """

    sensor_type = SensorTypes.LIDAR

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 **sensor_params):

        super().__init__(anchor=anchor, invisible_elements=invisible_elements,
                         normalize=normalize, noise_params=noise_params,
                         remove_duplicates=False, remove_occluded=False,
                         **sensor_params)

        self._sensor_max_value = self._range

    def _compute_raw_sensor(self, playground, *_):

        collision_points = self._compute_points(playground)

        pixels = np.ones(self._resolution) * self._range

        for angle_index, ray_angle in enumerate(self._ray_angles):

            collisions = collision_points[ray_angle]

            if collisions:
                col = collisions[0]
                pixels[angle_index] = col.alpha*self._range

        self.sensor_values = pixels[::-1].astype(float)

    @property
    def shape(self):
        return self._resolution

    def _apply_normalization(self):

        self.sensor_values /= self._sensor_max_value

    def draw(self, width, height):

        expanded = np.zeros((self.shape, 3))
        for i in range(3):
            expanded[:, i] = self.sensor_values[:]
        img = np.expand_dims(expanded, 0)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_NEAREST)

        if not self._normalize:
            img /= self._sensor_max_value

        return img


class Touch(Lidar):
    """
    Touch Sensors detect close proximity of Entities to the anchor of the sensor.
    It emulates artificial skin, at the condition that the shape of the anchor is round.

    The range parameter is used to describe the thickness of the artificial skin.
    """

    sensor_type = SensorTypes.TOUCH

    def __init__(self,
                 anchor,
                 invisible_elements=None,
                 normalize=True,
                 noise_params=None,
                 **sensor_params):

        super().__init__(anchor=anchor, invisible_elements=invisible_elements,
                         normalize=normalize, noise_params=noise_params,
                         **sensor_params)

        self._sensor_max_value = self._range
        self._range = self.anchor.radius + self._range  # pylint: disable=access-member-before-definition

    def _compute_raw_sensor(self, playground, *_):

        super()._compute_raw_sensor(playground)

        distance_to_anchor = self.sensor_values - self.anchor.radius
        distance_to_anchor[distance_to_anchor < 0] = 0
        self.sensor_values = self._sensor_max_value - distance_to_anchor
