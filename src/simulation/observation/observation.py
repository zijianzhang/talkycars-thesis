from datetime import datetime
from typing import Tuple

import numpy as np
from lib import quadkey


class Observation:
    def __init__(self, local_timestamp):
        assert isinstance(local_timestamp, int) or isinstance(local_timestamp, float)

        self.local_timestamp = local_timestamp
        # Caution: Uses local platform time!
        self.timestamp = datetime.now().timestamp()

class GnssObservation(Observation):
    def __init__(self, timestamp, coords: Tuple[float, float, float]):
        assert isinstance(coords, tuple)

        super().__init__(timestamp)
        self.value = coords

    def to_quadkey(self, level=20) -> quadkey.QuadKey:
        return quadkey.from_geo(self.value[:2], level)

    def to_tile(self, level=20):
        return self.to_quadkey(level).to_tile()

    def __str__(self):
        return f'[{self.timestamp}] GPS Position: {self.value}'

class LidarObservation(Observation):
    def __init__(self, timestamp, points: np.ndarray):
        assert isinstance(points, np.ndarray)

        super().__init__(timestamp)
        self.value = points

    def __str__(self):
        return f'[{self.timestamp}] Point Cloud: {self.value.shape}'

class PositionObservation(Observation):
    def __init__(self, timestamp, coords: Tuple[float, float, float]):
        assert isinstance(coords, tuple)

        super().__init__(timestamp)
        self.value = coords

    def __str__(self):
        return f'[{self.timestamp}] World Position: {self.value}'

class CameraRGBObservation(Observation):
    def __init__(self, timestamp, image: np.ndarray):
        assert isinstance(image, np.ndarray)

        super().__init__(timestamp)
        self.value = image

    def __str__(self):
        return f'[{self.timestamp}] RGB Image: {self.value.shape}'