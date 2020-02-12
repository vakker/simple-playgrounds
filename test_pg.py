from flatland.playgrounds.playground import PlaygroundGenerator, Playground
from flatland.default_parameters.entities import *


@PlaygroundGenerator.register_subclass('david')
class David(Playground):

    def __init__(self, params):
        scenes_params = {
            'scene': {
                'scene_type': 'room',
                'room_shape': [200, 200]
            },
        }

        params = {**scenes_params, **params}

        super(David, self).__init__(params)

        ### Basic entities
        basic_1 = basic_default.copy()
        basic_1['position'] = [150, 160, 0.56]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['shape_rectangle'] = [20, 40]

        basic_2 = basic_default.copy()
        basic_2['position'] = [160, 40, math.pi / 7]
        basic_2['physical_shape'] = 'rectangle'
        basic_2['shape_rectangle'] = [30, 40]
        basic_2['texture'] = {
            'type': 'random_tiles',
            'min': [50, 50, 150],
            'max': [60, 100, 190],
            'size_tiles': 4
        }

        basic_3 = basic_default.copy()
        basic_3['position'] = [60, 170, 0.5]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['radius'] = 20
        basic_3['movable'] = True
        basic_3['texture'] = {
            'type': 'polar_stripes',
            'color_1': [0, 50, 150],
            'color_2': [0, 100, 190],
            'n_stripes': 4
        }

        basic_4 = basic_default.copy()
        basic_4['position'] = [40, 60, 1.3]
        basic_4['physical_shape'] = 'circle'
        basic_4['radius'] = 20
        basic_4['movable'] = True

        for ent in [basic_1, basic_2, basic_3, basic_4]:

            self.add_entity(ent)


        self.starting_position = {
            'type': 'rectangle',
            'x_range': [50, 150],
            'y_range': [50, 150],
            'angle_range': [0, 3.14 * 2],
        }




@PlaygroundGenerator.register_subclass('chest-test')
class ChestTest(Playground):

    def __init__(self, params):
        scenes_params = {
            'scene': {
                'scene_type': 'room',
                'scene_shape': [200, 200]
            },
        }

        params = {**scenes_params, **params}

        super(ChestTest, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] = 50
        self.add_entity(end_zone)

        ### Basic entities
        pod = chest_default.copy()
        pod['position'] = [100, 100, math.pi / 4]
        pod['key_pod']['position'] = [30, 30, 0]

        self.add_entity(pod)

        self.starting_position = {
            'type': 'rectangle',
            'x_range': [50, 150],
            'y_range': [50, 150],
            'angle_range': [0, 3.14 * 2],
        }

@PlaygroundGenerator.register_subclass('basic-test')
class BasicTest(Playground):

    def __init__(self, params):

        scenes_params = {
            'scene': {
                'scene_type': 'room',
                'scene_shape': [200, 200]
            },
        }

        params = {**scenes_params, **params}

        super(BasicTest, self).__init__(params)

        end_zone = end_zone_default.copy()
        end_zone['position'] = [20, self.width - 20, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [20, 20]
        end_zone['reward'] = 50
        self.add_entity(end_zone)

        ### Basic entities
        pod = chest_default.copy()
        pod['position'] = [100, 100, math.pi / 4]
        pod['key_pod']['position'] = [30, 30, 0]

        self.add_entity(pod)

        self.starting_position = {
            'type': 'rectangle',
            'x_range': [50, 150],
            'y_range': [50, 150],
            'angle_range': [0, 3.14 * 2],
        }


@PlaygroundGenerator.register_subclass('all-test')
class AllTest(Playground):

    def __init__(self, params):
        scenes_params = {
            'scene': {
                'scene_type': 'room',
                'room_shape': [600, 800]
            },
        }

        params = {**scenes_params, **params}

        super(AllTest, self).__init__(params)

        ### Basic entities
        basic_1 = basic_default.copy()
        basic_1['position'] = [350, 250, math.pi / 2]
        basic_1['physical_shape'] = 'rectangle'
        basic_1['shape_rectangle'] = [20, 100]

        basic_2 = basic_default.copy()
        basic_2['position'] = [200, 100, math.pi / 2]
        basic_2['physical_shape'] = 'rectangle'
        basic_2['shape_rectangle'] = [30, 100]

        basic_2['texture'] = {
            'type': 'polar_stripes',
            'color_1': [150, 0, 50],
            'color_2': [200, 0, 100],
            'n_stripes': 4
        }
        basic_3 = basic_default.copy()
        basic_3['position'] = [100, 150, 0]
        basic_3['physical_shape'] = 'pentagon'
        basic_3['radius'] = 20
        basic_3['movable'] = True
        basic_3['texture'] = {
            'type': 'polar_stripes',
            'color_1': [0, 50, 150],
            'color_2': [0, 100, 190],
            'n_stripes': 2
        }
        ###### Absorbable
        absorbable_1 = absorbable_default.copy()
        absorbable_1['position'] = [100, 200, 0.2]
        absorbable_2 = absorbable_default.copy()
        absorbable_2['position'] = [100, 250, 0.5]
        ### Edible
        edible_1 = edible_default.copy()
        edible_1['position'] = [100, 300, 0.2]
        edible_1['physical_shape'] = 'rectangle'
        edible_1['shape_rectangle'] = [50, 60]
        edible_1['texture']['type'] = 'polar_stripes'
        edible_1['texture']['color_1'] = [100, 0, 150]
        edible_1['texture']['color_2'] = [0, 0, 250]
        edible_1['texture']['n_stripes'] = 3
        # edible_1['mass'] = 100
        # edible_1['movable'] = True
        # edible_1['graspable'] = True
        ### Dispenser
        dispenser_1 = dispenser_default.copy()
        dispenser_1['position'] = [100, 350, 0]
        dispenser_1['area'] = [[200, 325], [250, 375]]
        dispenser_1['limit'] = 7


        ### Yielder
        yielder_1 = yielder_default.copy()
        yielder_1['area'] = [[100, 400], [200, 500]]

        ### Zone
        end_zone = end_zone_default.copy()
        end_zone['position'] = [500, 50, 0]
        end_zone['physical_shape'] = 'rectangle'
        end_zone['shape_rectangle'] = [50, 50]

        healing_zone = healing_zone_default.copy()
        healing_zone['position'] = [500, 100, 0]
        healing_zone['visible'] = True

        damaging_zone = damaging_zone_default.copy()
        damaging_zone['position'] = [500, 150, 0]

        contact_endzone = contact_endzone_default.copy()
        contact_endzone['position'] = [500, 550, 0]

        ##### Button door
        button_door_1 = button_door_openclose_default.copy()
        button_door_1['position'] = [600, 200, 0]
        button_door_1['door']['position'] = [600, 250, math.pi / 2]

        ##### Button door
        button_door_2 = button_door_opentimer_default.copy()
        button_door_2['position'] = [600, 350, 0]
        button_door_2['door']['position'] = [600, 400, math.pi / 2]
        button_door_2['time_limit'] = 100

        ##### Lock_key door
        lock_key_door = lock_key_door_default.copy()
        lock_key_door['position'] = [600, 500, 0]
        lock_key_door['door']['position'] = [600, 550, math.pi / 2]
        lock_key_door['key']['position'] = [600, 450, math.pi / 2]

        ##### Moving object
        moving_1 = basic_default.copy()
        moving_1['position'] = [500, 500, math.pi / 2]
        moving_1['trajectory'] = {
            'trajectory_shape': 'line',
            'radius': 50,
            'center': [500, 500],
            'speed': 100,
        }
        fireball_1 = fireball_default.copy()
        fireball_1['position'] = [400, 500, math.pi / 2]
        fireball_1['trajectory'] = {
            'trajectory_shape': 'line',
            'radius': 60,
            'center': [400, 100],
            'angle': math.pi / 2,
            'speed': 100,
        }
        fairy_1 = fairy_default.copy()
        fairy_1['position'] = [400, 500, math.pi / 2]
        fairy_1['trajectory'] = {
            'trajectory_shape': 'pentagon',
            'radius': 30,
            'center': [400, 200],
            'speed': 200,
        }

        for ent in [basic_1, basic_2, basic_3, absorbable_1, absorbable_2, edible_1, yielder_1,
                         end_zone, healing_zone, damaging_zone, contact_endzone,
                         button_door_1, button_door_2, lock_key_door,
                         moving_1, fireball_1, fairy_1]:

            self.add_entity(ent)


        self.starting_position = {
            'type': 'rectangle',
            'x_range': [50, 150],
            'y_range': [50, 150],
            'angle_range': [0, 3.14 * 2],
        }

