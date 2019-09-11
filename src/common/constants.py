OBS_LIDAR_POINTS = 'lidar_points'
OBS_CAMERA_RGB_IMAGE = 'camera_image'
OBS_POSITION = 'player_pos'
OBS_ACTOR_EGO, OBS_ACTORS_RAW = 'ego_actor', 'all_dynamic_actors'
OBS_GRID_LOCAL, OBS_GRID_COMBINED = 'local_occupancy_grid', 'occupancy_grid'
OBS_GNSS_PREFIX = 'pos_gnss_'

ALIAS_EGO = 'ego'

INCREMENTAL_GRIDS = False  # because buggy
GRID_TTL_SEC = 3

OCCUPANCY_RADIUS_DEFAULT = 5  # (5 and 15 or 10 and 9)
OCCUPANCY_TILE_LEVEL = 24
OCCUPANCY_BBOX_OFFSET = 0.1
OCCUPANCY_BBOX_HEIGHT = 3.5

LIDAR_ANGLE_DEFAULT = 15  # Caution: Choose Lidar angle depending on grid size
LIDAR_MAX_RANGE = 100
LIDAR_Z_OFFSET = 2.8

GNSS_Z_OFFSET = 2.8

RES_X, RES_Y = 840, 480

N_PEDESTRIANS = 50

TOPIC_GRAPH_RAW_IN = '/graph_raw_in'
TOPIC_PREFIX_GRAPH_FUSED_OUT = '/graph_fused_out'

EDGE_DISTRIBUTION_TILE_LEVEL = 16
REMOTE_GRID_TILE_LEVEL = 19

FUSION_DECAY_LAMBDA = .05

REMOTE_PSEUDO_ID = -1

RECORDING_RATE = 10  # Hz
RECORDING_FILE_TPL = 'data/recordings/<id>_%Y-%m-%d_%H-%M-%S.csv'
