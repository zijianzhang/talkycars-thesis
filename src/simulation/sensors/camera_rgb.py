import weakref

import numpy as np
import pygame

import carla


class CameraRGBSensor(object):
    def __init__(self, parent_actor, hud):
        self.sensor = None
        self._parent = parent_actor
        self.recording = False
        self.surface = None

        world = self._parent.get_world()
        weak_self = weakref.ref(self)

        bp = world.get_blueprint_library().find('sensor.camera.rgb')
        bp.set_attribute('image_size_x', str(hud.dim[0]))
        bp.set_attribute('image_size_y', str(hud.dim[1]))
        bp.set_attribute('gamma', '2.2')

        self.sensor = world.spawn_actor(bp, carla.Transform(carla.Location(x=-6.5, z=2.8), carla.Rotation(pitch=-25)), attach_to=self._parent)
        self.sensor.listen(lambda event: CameraRGBSensor._on_image(weak_self, event))

        calibration = np.identity(3)
        calibration[0, 2] = hud.dim[0] / 2.0
        calibration[1, 2] = hud.dim[1] / 2.0
        calibration[0, 0] = calibration[1, 1] = hud.dim[0] / (2.0 * np.tan(90 * np.pi / 360.0))
        self.sensor.calibration = calibration

    def toggle_recording(self):
        self.recording = not self.recording

    def render(self, display):
        if self.surface is not None:
            display.blit(self.surface, (0, 0))

    @staticmethod
    def _on_image(weak_self, image):
        self = weak_self()
        if not self:
            return
        array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
        array = np.reshape(array, (image.height, image.width, 4))
        array = array[:, :, :3]
        array = array[:, :, ::-1]
        self.surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))

        if self.recording:
            image.save_to_disk('_out/%08d' % image.frame)
