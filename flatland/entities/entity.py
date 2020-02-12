import pymunk, math, pygame
from flatland.utils.config import *
from abc import ABC
from flatland.utils import texture

#from flatland.entities.entity_old import Entity


geometric_shapes = {'line':2, 'circle':60, 'triangle':3, 'square':4, 'pentagon':5, 'hexagon':6 }

class Entity():

    def __init__(self, params ):
        """
        Instantiate an obstacle with the following parameters
        :param pos: 2d tuple or 'random', position of the fruit
        :param environment: the environment calling the creation of the fruit
        """

        self.params = params

        self.entity_type = params['entity_type']
        self.physical_shape = params['physical_shape']
        self.texture_params = params['texture']
        self.is_temporary_entity = params['is_temporary_entity']

        if self.physical_shape == 'rectangle':
            self.width, self.length = params['shape_rectangle']
            self.texture_params['radius'] = max(self.width, self.length)
        else:
            self.radius = params['radius']
            self.texture_params['radius'] = self.radius


        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon'] :
            self.visible_vertices = self.compute_vertices(self.radius)


        self.pm_body = None
        self.pm_interaction_shape = None
        self.pm_visible_shape = None

        ##### PyMunk Body
        self.graspable = params.get('graspable', False)
        self.interactive = params.get('interactive', False)
        self.movable = params.get('movable', False)

        if self.graspable:
            self.interactive = True
            self.movable = True

        if self.movable:
            self.mass = params['mass']
            inertia = self.compute_moments()
            self.pm_body = pymunk.Body(self.mass, inertia)

        else:
            self.mass = None
            self.pm_body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.initial_position = params['position']

        self.moving = False

        self.trajectory_params = params.get('trajectory', None)
        if self.trajectory_params is not None:
            self.moving = True
            self.generate_trajectory()
            self.pm_body.position = self.trajectory_points[0]
            self.pm_body.angle = params['position'][2]

        else:

            self.pm_body.position = params['position'][0:2]
            self.pm_body.angle = params['position'][2]

        ##### PyMunk visible shape

        self.visible = params.get('visible', True)
        self.texture_visible_surface = None

        if self.visible:
            self.generate_pm_visible_shape()
            self.visible_mask = self.generate_visible_mask()


        ##### PyMunk sensor shape

        self.texture_interactive_surface = None

        if self.interactive:

            if self.visible :
                self.interaction_range = params['interaction_range']

                if self.physical_shape == 'rectangle':
                    self.width_interaction = self.width + self.interaction_range
                    self.length_interaction = self.length + self.interaction_range

                else:
                    self.radius_interaction = self.radius + self.interaction_range

            elif (not self.visible):

                if self.physical_shape == 'rectangle':
                    self.width_interaction, self.length_interaction = params['shape_rectangle']

                else:
                    self.radius_interaction = params['radius']

            self.generate_pm_interaction_shape()
            self.interaction_mask = self.generate_interaction_mask()

        #### Default interaction:

        self.absorbable = False
        self.activable = False
        self.edible = False


        self.pm_elements = [self.pm_body, self.pm_interaction_shape, self.pm_visible_shape]
        self.pm_elements = [x for x in self.pm_elements if x is not None]





    def generate_trajectory(self):

        self.trajectory_points = []
        self.index_trajectory = 0

        if 'waypoints' not in self.trajectory_params:

            number_sides = geometric_shapes[self.trajectory_params['trajectory_shape']]

            radius = self.trajectory_params['radius']
            center = self.trajectory_params['center']
            angle = self.trajectory_params.get('angle', 0)

            waypoints = []
            for n in range(number_sides):
                waypoints.append([center[0] + radius * math.cos(n * 2 * math.pi / number_sides + angle),
                                 center[1] + radius * math.sin(n * 2 * math.pi / number_sides + angle)])

        else:
            waypoints = self.trajectory_params['waypoints']

        speed = self.trajectory_params['speed']
        n_points = int(1.0*speed / len(waypoints))

        for index_pt in range(-1, len(waypoints)  -1 ):

            pt_1 = waypoints[index_pt]
            pt_2 = waypoints[index_pt + 1]

            pts_x = [ pt_1[0] + x * (pt_2[0] - pt_1[0])/n_points for x in range(n_points)]
            pts_y = [ pt_1[1] + x * (pt_2[1] - pt_1[1])/n_points for x in range(n_points)]

            for i in range(n_points):
                self.trajectory_points.append( [pts_x[i], pts_y[i]])


    def generate_pm_visible_shape(self):

        if self.physical_shape == 'circle':

            self.pm_visible_shape = pymunk.Circle(self.pm_body, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            self.pm_visible_shape = pymunk.Poly(self.pm_body, self.visible_vertices)

        elif self.physical_shape == 'rectangle':

            self.pm_visible_shape = pymunk.Poly.create_box(self.pm_body, (self.width, self.length))

        else:
            raise ValueError

        self.pm_visible_shape.friction = 1.
        self.pm_visible_shape.elasticity = 0.95


    def generate_pm_interaction_shape(self):

        if self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon'] :
            self.interaction_vertices = self.compute_vertices(self.radius_interaction)


        if self.physical_shape == 'circle':

            self.pm_interaction_shape = pymunk.Circle(self.pm_body, self.radius_interaction)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            self.pm_interaction_shape = pymunk.Poly(self.pm_body, self.interaction_vertices)

        elif self.physical_shape == 'rectangle':

            self.pm_interaction_shape = pymunk.Poly.create_box(self.pm_body, (self.width_interaction, self.length_interaction))

        else:
            raise ValueError

        self.pm_interaction_shape.sensor = True
        self.pm_interaction_shape.collision_type = collision_types['interactive']


    def generate_visible_mask(self):

        text = texture.Texture.create(self.texture_params)

        alpha = 255


        if self.physical_shape == 'rectangle':

            width, length = int(self.width), int(self.length)

            if self.texture_visible_surface is None:
                self.texture_visible_surface = text.generate(length, width)
            else:
                self.texture_visible_surface = pygame.transform.scale(self.texture_visible_surface, ((length, width)))

            mask = pygame.Surface((length, width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, alpha), ((0, 0), (length, width)))

        elif self.physical_shape == 'circle':

            radius = int(self.radius)

            if self.texture_visible_surface is None:
                self.texture_visible_surface =  text.generate(radius * 2, radius * 2)
            else:
                self.texture_visible_surface = pygame.transform.scale(self.texture_visible_surface, ((radius * 2, radius * 2)))

            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (radius, radius), radius)


        # TODO: safe guard case other than implemented
        else:

            bb = self.pm_visible_shape.cache_bb()

            length = bb.top - bb.bottom
            width = bb.right - bb.left

            vertices = [[x[1] + length, x[0] + width] for x in self.visible_vertices]

            if self.texture_visible_surface is None:
                self.texture_visible_surface = text.generate(2 * length, 2 * width)
            else:
                self.texture_visible_surface = pygame.transform.scale(self.texture_visible_surface, ((2*length, 2*width)))

            mask = pygame.Surface((2 * length, 2 * width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        # Apply texture on mask
        mask.blit(self.texture_visible_surface, (0, 0), None, pygame.BLEND_MULT)

        return mask


    def generate_interaction_mask(self):

        text = texture.Texture.create(self.texture_params)

        alpha = 50

        if self.physical_shape == 'rectangle':

            width, length = int(self.width_interaction), int(self.length_interaction)

            if self.texture_interactive_surface is None:
                self.texture_interactive_surface = text.generate(length, width)

            mask = pygame.Surface((length, width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.rect(mask, (255, 255, 255, alpha), ((0, 0), (length, width)))

        elif self.physical_shape == 'circle':

            radius = int(self.radius_interaction)

            if self.texture_interactive_surface is None:
                self.texture_interactive_surface =  text.generate(radius * 2, radius * 2)

            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.circle(mask, (255, 255, 255, alpha), (radius, radius), radius)

        else:

            bb = self.pm_interaction_shape.cache_bb()

            length = bb.top - bb.bottom
            width = bb.right - bb.left

            vertices = [[x[1] + length, x[0] + width] for x in self.interaction_vertices]

            if self.texture_interactive_surface is None:
                self.texture_interactive_surface = text.generate(2 * length, 2 * width)

            mask = pygame.Surface((2 * length, 2 * width), pygame.SRCALPHA)
            mask.fill((0, 0, 0, 0))
            pygame.draw.polygon(mask, (255, 255, 255, alpha), vertices)

        # Apply texture on mask
        mask.blit(self.texture_interactive_surface, (0, 0), None, pygame.BLEND_MULT)

        return mask


    def compute_vertices(self, radius):

        number_sides = geometric_shapes[self.physical_shape]

        vertices = []
        for n in range(number_sides):
            vertices.append( [ radius*math.cos(n * 2*math.pi / number_sides), radius* math.sin(n * 2*math.pi / number_sides) ])

        return vertices



    def compute_moments(self):

        if self.physical_shape == 'circle':

            moment = pymunk.moment_for_circle(self.mass, 0, self.radius)

        elif self.physical_shape in ['triangle', 'square', 'pentagon', 'hexagon']:

            moment = pymunk.moment_for_poly(self.mass, self.visible_vertices)

        elif self.physical_shape == 'rectangle':

            moment =  pymunk.moment_for_box(self.mass, (self.width, self.length))

        else:

            raise ValueError('Not implemented')

        return moment

    def draw(self, surface, draw_interaction = False):
        """
        Draw the obstacle on the environment screen
        """

        if draw_interaction and self.interactive:
            mask_rotated = pygame.transform.rotate(self.interaction_mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(mask_rotated, mask_rect, None)

        if self.visible:
            mask_rotated = pygame.transform.rotate(self.visible_mask, self.pm_body.angle * 180 / math.pi)
            mask_rect = mask_rotated.get_rect()
            mask_rect.center = self.pm_body.position[1], self.pm_body.position[0]
            surface.blit(mask_rotated, mask_rect, None)

    def update(self):

        if self.moving :

            self.index_trajectory += 1
            if self.index_trajectory == len(self.trajectory_points):
                self.index_trajectory = 0

            self.pm_body.position = self.trajectory_points[self.index_trajectory]

    def pre_step(self):
        pass


    def reset(self):

        if self.moving:
            self.index_trajectory = 0
            self.pm_body.position = self.trajectory_points[self.index_trajectory]

        else:
            self.pm_body.position = self.initial_position[0:2]
            self.pm_body.angle = self.initial_position[2]

        self.pm_body.velocity = (0, 0)
        self.pm_body.angular_velocity = 0

        if self.is_temporary_entity:
            replace = False
        else:
            replace = True

        return replace


class EntityGenerator():

    subclasses = {}

    @classmethod
    def register_subclass(cls, entity_type):
        def decorator(subclass):
            cls.subclasses[entity_type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, params):
        entity_type = params['entity_type']
        if entity_type not in cls.subclasses:
            raise ValueError('Entity type not implemented:' + entity_type)

        return cls.subclasses[entity_type](params)