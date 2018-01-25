from histogrammar import HistogramFilter
from math import pi

hf = HistogramFilter(field_x = 10.0, field_y=10.0)

start_x = 0.1
start_y = 0.04
heading = 0.05 * pi
length = 5

for coord in hf._iterate_ray_trace(start_x, start_y, heading, length):
    print('coord: (%.2f, %.2f,)' % coord)

coord = hf._last_block(start_x, start_y, heading, length)
print('last coord: (%.2f, %.2f,)' % coord)
