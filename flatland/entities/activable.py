import pymunk, random, pygame

from .basic import  Basic
from .entity import Entity, EntityGenerator
from flatland.utils.config import *
from ..default_parameters.entities import *

@EntityGenerator.register_subclass('dispenser')
class Dispenser(Entity):

    def __init__(self, params):

        params = {**dispenser_default, **params}
        params['visible'] = True
        params['interactive'] = True

        super(Dispenser, self).__init__(params)

        self.pm_interaction_shape.collision_type = collision_types['interactive']

        self.object_produced = params['object_produced']

        self.production_area_shape = params['area_shape']
        self.production_area = params['area']

        self.limit = params['limit']

        self.produced_elements = []

    def activate(self):

        obj = self.object_produced

        if self.production_area_shape == 'rectangle':

            x = random.uniform( self.production_area[0][0],self.production_area[1][0] )
            y = random.uniform( self.production_area[0][1],self.production_area[1][1] )

            obj['position'] = (x,y,0)

        return obj

@EntityGenerator.register_subclass('button_door_openclose')
class ButtonDoorOpenClose(Entity):

    def __init__(self, params):

        params = {**button_door_openclose_default, **params}
        params['visible'] = True
        params['interactive'] = True

        super(ButtonDoorOpenClose, self).__init__(params)

        self.activable = True

        self.door_params = {**door_default, **params['door']}
        self.door_opened = False

        self.door = None


    def activate(self):

        if self.door_opened:
            self.door_opened = False
            self.door.visible = True

        else:
            self.door_opened = True
            self.door.visible = False

@EntityGenerator.register_subclass('button_door_opentimer')
class ButtonDoorOpenTimer(Entity):

    def __init__(self, params):

        params = {**button_door_opentimer_default, **params}
        params['visible'] = True
        params['interactive'] = True

        super(ButtonDoorOpenTimer, self).__init__(params)

        self.activable = True

        self.door_params = {**door_default, **params['door']}
        self.time_open = params['time_open']


        self.timer = self.time_open
        self.door = None
        self.door_opened = False

    def close_door(self):

        self.door_opened = False
        self.reset_timer()

    def activate(self):

        self.door.visible = False
        self.reset_timer()

    def reset_timer(self):

        self.timer = self.time_open

    def update(self):

        if self.door_opened:
            self.timer -= 1

        if self.timer == 0:
            self.door.visible = True


@EntityGenerator.register_subclass('lock_key_door')
class LockKeyDoor(Entity):

    def __init__(self, params):

        params = {**lock_key_door_default, **params}
        params['visible'] = True
        params['interactive'] = True

        super(LockKeyDoor, self).__init__(params)

        self.activable = True

        self.door_params = {**door_default, **params['door']}
        print(self.door_params)
        self.key_params = {**door_default, **params['key']}

        self.door_opened = False

        self.door = None
        self.key = None

    def activate(self):

        self.door_opened = True
        self.door.visible = False
