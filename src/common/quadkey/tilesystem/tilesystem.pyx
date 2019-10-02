#!python
#cython: boundscheck=False
#cython: wraparound=False
#cython: nonecheck=False
#cython: cdivision=True
from libc cimport math

cdef long EARTH_RADIUS = 6378137
cdef (double, double) LATITUDE_RANGE = (-85.05112878, 85.05112878)
cdef (double, double) LONGITUDE_RANGE = (-180., 180.)

ctypedef enum tile_anchor:
    ANCHOR_NW
    ANCHOR_NE
    ANCHOR_SW
    ANCHOR_SE
    ANCHOR_CENTER

cdef double clip(const double n, const (double, double) min_max):
    return min(max(n, min_max[0]), min_max[1])

cdef long map_size(const long level):
    cdef unsigned long base = 256
    return base << <unsigned long> level

# Alternative map_size implementation
# Used in:
#  – https://github.com/CartoDB/python-quadkey/blob/a7c53e8e8bd18eb9ba187b345bd2faf525b23ecc/quadkey.c#L194
#  – https://github.com/ethlo/jquad/blob/3c0bed3b0433ef5f67e786a41c56af9cc103d7dd/src/main/java/com/ethlo/quadkey/QuadKey.java#L130
# This one is required for quad ints to work properly. Otherwise they would overflow long for level 31
# However, with this map_size, quadkey strings are not generated properly anymore. Instead, we would probably have to
# derive quadkeys from quadints using https://github.com/n1try/jquad/blob/095bbd0e1b1fc557c94532ec8455191aecf9b913/src/main/java/com/ethlo/quadkey/QuadKey.java#L154 in combination with https://stackoverflow.com/a/699891/3112139

# cdef long map_size(const long level):
#     cdef unsigned long base = 256
#     return (1 << <unsigned long> level) & 0xFFFFFFFF

cpdef double ground_resolution(double lat, const long level):
    lat = clip(lat, LATITUDE_RANGE)
    return math.cos(lat * math.pi / 180) * 2 * math.pi * EARTH_RADIUS / map_size(level)

cpdef (long, long) geo_to_pixel((double, double) geo, const long level):
    cdef double lat, lon, x, y, sin_lat
    cdef long pixel_x, pixel_y, ms
    lat, lon = geo[0], geo[1]
    lat = clip(lat, LATITUDE_RANGE)
    lon = clip(lon, LONGITUDE_RANGE)
    x = (lon + 180) / 360
    sin_lat = math.sin(lat * math.pi / 180)
    y = 0.5 - math.log((1 + sin_lat) / (1 - sin_lat)) / (4 * math.pi)
    ms = map_size(level)
    pixel_x = <long>(clip(x * ms + 0.5, (0, ms - 1)))
    pixel_y = <long>(clip(y * ms + 0.5, (0, ms - 1)))
    return pixel_x, pixel_y

cpdef (double, double) pixel_to_geo((double, double) pixel, const long level):
    cdef double x, y, lat, lon, pixel_x, pixel_y
    cdef long ms
    pixel_x = pixel[0]
    pixel_y = pixel[1]
    ms = map_size(level)
    x = (clip(pixel_x, (0, ms - 1)) / ms) - 0.5
    y = 0.5 - (clip(pixel_y, (0, ms - 1)) / ms)
    lat = 90 - 360 * math.atan(math.exp(-y * 2 * math.pi)) / math.pi
    lon = 360 * x
    return math.round(lat * 1e6) / 1e6, math.round(lon * 1e6) / 1e6

cpdef (long, long) pixel_to_tile(const (long, long) pixel):
    return pixel[0] // 256, pixel[1] // 256

cpdef long pixel_to_quadint(const (long, long) pixel):
    cdef long b[5], s[5]
    cdef long x, y

    b[:] = [0x5555555555555555, 0x3333333333333333, 0x0F0F0F0F0F0F0F0F, 0x00FF00FF00FF00FF, 0x0000FFFF0000FFFF]
    s[:] = [1, 2, 4, 8, 16]

    x = (pixel[0] | pixel[0] << s[4]) & b[4]
    y = (pixel[1] | pixel[1] << s[4]) & b[4]

    x = (x | (x << s[3])) & b[3]
    y = (y | (y << s[3])) & b[3]

    x = (x | (x << s[2])) & b[2]
    y = (y | (y << s[2])) & b[2]

    x = (x | (x << s[1])) & b[1]
    y = (y | (y << s[1])) & b[1]

    x = (x | (x << s[0])) & b[0]
    y = (y | (y << s[0])) & b[0]

    return x | (y << 1)

cpdef (long, long) tile_to_pixel(const (long, long) tile, tile_anchor anchor):
    cdef long pixel[2]
    pixel = [tile[0] * 256, tile[1] * 256]
    if anchor == ANCHOR_CENTER:
        # TODO: should clip on max map size
        pixel = [pixel[0] + 256, pixel[1] + 256]
    elif anchor == ANCHOR_NE:
        pixel = [pixel[0] + 256, pixel[1]]
    elif anchor == ANCHOR_SW:
        pixel = [pixel[0], pixel[1] + 256]
    elif anchor == ANCHOR_SE:
        pixel = [pixel[0] + 256, pixel[1] + 256]

    return <long>pixel[0], <long>pixel[1]

cpdef str quadint_to_quadkey(const long quadint):
    cdef long n, i, char_code
    cpdef str qk, bin_str

    qk = ''
    bin_str = '{0:b}'.format(quadint)
    n = len(bin_str) + (2 - len(bin_str) % 2)

    for i in range(2, n+2, 2):
        char_code = (quadint >> (n-i)) & 0b11
        qk += str(char_code)

    return qk

cpdef str tile_to_quadkey(const (long, long) tile, const long level):
    cdef int i
    cdef long tile_x, tile_y, mask, bit
    cdef char digit
    cdef char qk[level]
    tile_x = tile[0]
    tile_y = tile[1]
    quadkey = ''
    for i in range(level):
        bit = level - i
        digit = 48  # ord('0')
        mask = 1 << (bit - 1)  # if (bit - 1) > 0 else 1 >> (bit - 1)
        if (tile_x & mask) is not 0:
            digit += 1
        if (tile_y & mask) is not 0:
            digit += 2
        qk[i] = digit
    return qk[:level].decode('UTF-8')

cpdef ((long, long), long) quadkey_to_tile(str quadkey):
    cdef long tile_x, tile_y, mask, bit
    cdef int level, i
    tile_x, tile_y = (0, 0)
    level = len(quadkey)
    for i in range(level):
        bit = level - i
        mask = 1 << (bit - 1)
        if quadkey[level - bit] == '1':
            tile_x |= mask
        if quadkey[level - bit] == '2':
            tile_y |= mask
        if quadkey[level - bit] == '3':
            tile_x |= mask
            tile_y |= mask
    return (tile_x, tile_y), level