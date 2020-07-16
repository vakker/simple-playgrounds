from .semantic_sensor import SemanticSensor
from flatland.utils.definitions import SensorModality
from collections import namedtuple

import pymunk
import math

from operator import attrgetter



LidarPoint = namedtuple('Point', 'entity distance angle')


class LidarRays(SemanticSensor):

    sensor_modality = SensorModality.SEMANTIC

    sensor_type = 'lidar-rays'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        super().__init__(anchor, invisible_elements, remove_occluded = remove_occluded, allow_duplicates = allow_duplicates, **sensor_params)

        # Field of View of the Sensor
        self._range = sensor_params.get('range')
        self._angle = sensor_params.get('fov') * math.pi / 180
        self.number_rays = sensor_params.get('number_rays')

        self.radius_beam = 1

        if self.number_rays == 1:
            self.angles = [0]
        else:
            self.angles = [n * self._angle / (self.number_rays - 1) - self._angle / 2 for n in range(self.number_rays)]

        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)
        self.sensor_value = {}

        self.invisible_shapes = []
        for entity in self.invisible_elements:
            self.invisible_shapes += [entity.pm_visible_shape, entity.pm_interaction_shape]
        self.invisible_shapes=list(set(self.invisible_shapes))
        if None in self.invisible_shapes: self.invisible_shapes.remove(None)

    def remove_occlusions(self, collisions):

        if collisions == []:
            return collisions
        else:
            min_distance_point = min(collisions, key=attrgetter('alpha'))
            return [min_distance_point]

    def remove_duplicates(self, sensor_value):

        all_points = []
        all_angles = []

        for angle, points in sensor_value.items():
            all_points += points
            all_angles.append(angle)

        for s in sensor_value:
            sensor_value[s] = []

        all_entities = list(set(pt.entity for pt in all_points))

        for entity in all_entities:
            min_distance_point = min([pt for pt in all_points if pt.entity is entity],
                                     key=attrgetter('distance'))

            angle_ray = min(all_angles, key=lambda x: (x - min_distance_point.angle) ** 2)
            sensor_value[angle_ray] = [min_distance_point]

        return sensor_value

    def compute_collisions(self, pg, sensor_angle):

        position = self.anchor.pm_body.position
        angle = self.anchor.pm_body.angle + sensor_angle

        position_end = (position[0] + self._range * math.cos(angle),
                        position[1] + self._range * math.sin(angle)
                        )

        collisions = pg.space.segment_query(position, position_end, 2 * self.radius_beam, self.filter)

        # remove invisibles
        collisions = [col for col in collisions if col.shape not in self.invisible_shapes and col.shape.sensor != True]

        # filter occlusions
        if self.remove_occluded:
            collisions = self.remove_occlusions(collisions)

        shapes = [collision.shape for collision in collisions]
        distances = [collision.alpha * self._range for collision in collisions]

        # Take entities which are not sensors
        entities = [(pg.get_scene_element_from_shape(shape), dist)
                     for shape, dist in zip(shapes, distances)
                     if pg.get_scene_element_from_shape(shape) is not None]

        entities = list(set([LidarPoint(ent, dist, sensor_angle) for ent, dist in entities]))

        agents = [pg.get_agent_from_shape(shape) for shape in shapes]
        agents = list(set([LidarPoint(ag, dist, sensor_angle) for ag, dist in zip(agents, distances) if ag is not None]))

        return entities+agents

    def update_sensor(self, pg):

        self.sensor_value = {}

        for sensor_angle in self.angles:

            collisions = self.compute_collisions(pg, sensor_angle)

            self.sensor_value[sensor_angle] = collisions

        if not self.allow_duplicates:

            self.sensor_value = self.remove_duplicates(self.sensor_value)


    @property
    def shape(self):
        return None


class LidarCones(LidarRays):
    """
    maximum angle of cones should be
    """
    sensor_modality = SensorModality.SEMANTIC

    sensor_type = 'lidar-cones'

    def __init__(self, anchor, invisible_elements, remove_occluded = True, allow_duplicates = False, **sensor_params):

        default_config = self.parse_configuration(self.sensor_type)
        sensor_params = {**default_config, **sensor_params}

        self.number_cones = sensor_params['number_cones']
        self.resolution = sensor_params['resolution']
        self._range = sensor_params.get('range')
        self._angle = sensor_params.get('fov') * math.pi / 180

        number_rays = int((self._range * self._angle / self.resolution)) + 1

        super().__init__(anchor, invisible_elements, number_rays=number_rays,
                         remove_occluded = remove_occluded, allow_duplicates = allow_duplicates, **sensor_params)

        if self.number_cones == 1:
            self.angles_cone_center = [0]
        else:
            angle = self._angle - self._angle / (self.number_cones)
            self.angles_cone_center = [n * angle / (self.number_cones - 1) - angle / 2 for n in
                                       range(self.number_cones)]

        self.filter = pymunk.ShapeFilter(mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b1)

    def remove_cone_occlusions(self, collisions):

        if collisions == []:
            return collisions
        else:
            min_distance_point = min(collisions, key=attrgetter('distance'))
            return [min_distance_point]


    def update_sensor(self, pg):

        super().update_sensor(pg)

        all_collisions = []
        for _, collisions in self.sensor_value.items():
            all_collisions += collisions

        self.sensor_value = {}
        for sensor_angle in self.angles_cone_center:
            self.sensor_value[sensor_angle] = []


        # assign each collision to a cone
        for collision in all_collisions:
            cone_angle = min(self.angles_cone_center, key=lambda x: (x - collision.angle) ** 2)
            self.sensor_value[cone_angle].append(collision)

        # filter for occlusion and duplicates
        if self.remove_occluded:
            for cone_angle, collisions in self.sensor_value.items():

                collisions = self.remove_cone_occlusions(collisions)
                self.sensor_value[cone_angle] = collisions

        if not self.allow_duplicates:

            self.sensor_value = self.remove_duplicates(self.sensor_value)

    @property
    def shape(self):
        return None