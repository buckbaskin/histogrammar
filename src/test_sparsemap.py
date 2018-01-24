from histogrammar import SparseMap

test_map1 = SparseMap(default_probability=0.01, resolution=0.2)
test_map2 = SparseMap(default_probability=1, resolution=1.0)

for x in range(0, 10):
    for y in range(0, 10):
        x_ = (x + 1) * 0.1
        y_ = (y + 1) * 0.1
        val = x_ / y_
        print(x_, y_, val,)
        test_map1[x_, y_] = val
        test_map2[x_, y_] = val

tests1 = [
    (0, 0, 1),
    (0.0, 1.0, 0.1),
    (0.0, 0.4, 0.2),
    (-1, -1, 0.01),
]

tests2 = [
    (0, 0, 1.0),
    (0.0, 1.0, 0.9 / 1.0),
    (1.0, 0.4, 1.0 / 0.9),
    (-1, -1, 1),
]

print('test map 1 (default)')
for index, value in enumerate(tests1):
    print('%d %s' % (index, test_map1[value[0], value[1]] == value[2]))
    if not test_map1[value[0], value[1]] == value[2]:
        print('Failed: %s vs %s' % (test_map1[value[0], value[1]], value[2],))

print('test map 2')
for index, value in enumerate(tests2):
    print('%d %s' % (index, test_map2[value[0], value[1]] == value[2]))
    if not test_map2[value[0], value[1]] == value[2]:
        print('Failed: %s vs %s' % (test_map2[value[0], value[1]], value[2],))