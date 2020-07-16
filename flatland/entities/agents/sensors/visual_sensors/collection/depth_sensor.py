"""
Module defining Depth Sensor
"""
import numpy as np
import cv2

from flatland.entities.agents.sensors.visual_sensors.visual_sensor import VisualSensor

# pylint: disable=no-member


class DepthSensor(VisualSensor):

    """Depth Sensor calculates a Depth image from the point of view of the agent.
    Similar to a Depth Camera.
    """

    sensor_type = 'depth'

    def __init__(self, anchor, invisible_elements, normalize=True, **kwargs):

        super(DepthSensor, self).__init__(anchor, invisible_elements, normalize, **kwargs)

    def update_sensor(self, img):

        super().update_sensor(img)

        mask = self.polar_view != 0
        sensor = np.min(np.where(mask.any(axis=1), mask.argmax(axis=1),
                                 self.polar_view.shape[1] - 1), axis=1)

        sensor_value = (self.polar_view.shape[1] - sensor)

        image = np.asarray(sensor_value)
        image = np.expand_dims(image, 0)
        self.sensor_value = cv2.resize(image, (self._resolution, 1),
                                       interpolation=cv2.INTER_NEAREST)[0, :]

        if self.normalize:
            self.sensor_value = self.sensor_value*1.0/self._range

    @property
    def shape(self):
        return self._resolution