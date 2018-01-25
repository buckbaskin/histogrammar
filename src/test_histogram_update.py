from histogrammar import HistogramFilter
from math import pi

hf = HistogramFilter(field_x = 10.0, field_y=10.0)

start_x = 0.1
start_y = 0.1
heading = 0.0 * pi
length = 1

print('original values')
for coord in hf._iterate_ray_trace(start_x, start_y, heading, length + 1):
    # print('coord: (%.2f, %.2f,)' % coord)
    print('     -> %.4f' % (hf.map[coord],))

last_odom = (start_x, start_y, heading,)
last_scan = (0.0, 0.01, [length])

hf.update(last_odom, last_scan)

print('---\nnew values')
for coord in hf._iterate_ray_trace(start_x, start_y, heading, length + 1):
    # print('coord: (%.2f, %.2f,)' % coord)
    print('     -> %.4f' % (hf.map[coord],))

last_scan = (0.0, 0.01, [length + 0.2])
hf.update(last_odom, last_scan)

print('---\n1 update values')
for coord in hf._iterate_ray_trace(start_x, start_y, heading, length + 1):
    # print('coord: (%.2f, %.2f,)' % coord)
    print('     -> %.4f' % (hf.map[coord],))

hf.update(last_odom, last_scan)

print('---\n2 update values')
for coord in hf._iterate_ray_trace(start_x, start_y, heading, length + 1):
    # print('coord: (%.2f, %.2f,)' % coord)
    print('     -> %.4f' % (hf.map[coord],))

hf.update(last_odom, last_scan)

print('---\n3 update values')
for coord in hf._iterate_ray_trace(start_x, start_y, heading, length + 1):
    # print('coord: (%.2f, %.2f,)' % coord)
    print('     -> %.4f' % (hf.map[coord],))
