# import numpy as np

from math import ceil, cos, floor, sin

class SparseMap(object):
    def __init__(self, default_probability=0.01, resolution=0.2):
        self.def_prob = default_probability
        self.resolution = resolution
        self.data = {}
        self.rows = {}
        self.cols = {}

    def __collapse_key(self, x, y):
        new_x = int(floor(x / self.resolution))
        new_y = int(floor(y / self.resolution))
        return (new_x, new_y,)

    def __expand_key(self, tuple):
        x = tuple[0] * self.resolution
        y = tuple[1] * self.resolution
        return (x, y,)

    def __getitem__(self, tuple_or_x, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        if self.__collapse_key(x, y) not in self.data:
            return self.def_prob
        return self.data[self.__collapse_key(x, y)]

    def __setitem__(self, tuple_or_x, value, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        self.data[self.__collapse_key(x, y)] = value

    def __delitem__(self, tuple_or_x, y=None):
        if y is None:
            x = tuple_or_x[0]
            y = tuple_or_x[1]
        else:
            x = tuple_or_x

        del self.data[self.__collapse_key(x, y)]

    def __len__(self):
        return len(self.data)


    def keys(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                return [self.__expand_key(k) for k in self.rows[selector]]
        if axis == 1 or axis == 'col':
            if selector is not None:
                return [self.__expand_key(k) for k in self.cols[selector]]
        return [self.__expand_key(k) for k in self.data.keys()]

    def values(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                return [self.data[k] for k in self.rows[selector]]
        if axis == 1 or axis == 'col':
            if selector is not None:
                return [self.data[k] for k in self.cols[selector]]
        return self.data.values()

    def items(self, axis=None, selector=None):
        return list(self.iteritems(axis, selector))

    def iteritems(self, axis=None, selector=None):
        if axis == 0 or axis == 'row':
            if selector is not None:
                for key in self.rows[selector]:
                    yield (self.__expand_key(key), self.data[key],)
        if axis == 1 or axis == 'col':
            if selector is not None:
                for key in self.cols[selector]:
                    yield (self.__expand_key(key), self.data[key],)
        
        for pair in self.data.iteritems():
            yield (self.__expand_key(pair[0]), pair[1])

class BayesBinaryBinaryModel(object):
    def __init__(self, p_true_true, p_true_false):
        # p(hit|obstacle)
        self.ptt = p_true_true
        # p(hit|no obsatcle)
        self.ptf = p_true_false
        # p(no hit|obstacle)
        self.pft = 1.0 - p_true_true
        # p(no hit|no obstacle)
        self.pff = 1.0 - p_true_false

    def posterior_from_true(self, prior):
        '''
        Posterior Probability when getting a true reading
        Ex. p(obstacle|scan hit)
        '''
        p_scan_hit = self.ptt * prior + self.ptf * (1.0 - prior)
        return (self.ptt / p_scan_hit) * prior


    def posterior_from_false(self, prior):
        '''
        Posterior Probability when getting a true reading
        Ex. p(obstacle|scan miss)
        '''
        p_scan_miss = self.pft * prior + self.pff * (1.0 - prior)
        return (self.pft / p_scan_miss) * prior

class HistogramFilter(object):
    def __init__(self, field_x, field_y):
        self.max_x = field_x
        self.min_x = 0.0
        self.max_y = field_y
        self.min_y = 0.0
        self.map = SparseMap(default_probability=0.1, resolution=0.2)
        self.min_prob = 0.0001
        self.max_prob = 1.0000
        self.update_math = BayesBinaryBinaryModel(0.90, 0.01)

    def __unpack_scan(self, last_scan):
        heading_offset = last_scan.angle_min
        heading_step = last_scan.angle_increment
        rays = last_scan.ranges
        return heading_offset, heading_step, rays

    def __unpack_odom(self, last_odom):
        x = last_odom.pose.pose.position.x
        y = last_odom.pose.pose.position.y
        quat = last_odom.pose.pose.orientation
        heading = 0.0
        raise NotImplementedError()
        return x, y, heading

    def update(self, last_odom, last_scan):
        x, y, heading = self.__unpack_odom(last_odom)
        heading_offset, heading_step, rays = self.__unpack_scan(last_scan)
        current_heading = heading + heading_offset
        for ray_length in rays:
            self._clear_with_ray(x, y, current_heading, ray_length)
            self._increase_ray_terminator(x, y, current_heading, ray_length)

    def _clear_with_ray(self, start_x, start_y, heading, length):
        coords = list(self._iterate_ray_trace(start_x, start_y, heading, length))
        for coord in coords[:-1]:
            prior = self.map[coord]
            self.map[coord] = self.update_math.posterior_from_false(prior)
            if self.map[coord] < self.min_prob:
                self.map[coord] = self.min_prob
            if self.map[coord] > self.max_prob:
                self.map[coord] = self.max_prob

    def _increase_ray_terminator(self, start_x, start_y, heading, length):
        coord = self._last_block(start_x, start_y, heading, length)
        self.map[coord] = self.update_math.posterior_from_true(self.map[coord])
        if self.map[coord] < self.min_prob:
            self.map[coord] = self.min_prob
        if self.map[coord] > self.max_prob:
            self.map[coord] = self.max_prob

    def _iterate_ray_trace(self, start_x, start_y, heading, length):
        '''
        Iterate over every block that the ray trace hits

        TODO(buckbaskin): This may double count the original square
        In practice, there shouldn't be an obstacle in the original square
        '''
        x = start_x
        y = start_y
        y_inc = sin(heading)
        x_inc = cos(heading)
        dist_traveled = 0
        while dist_traveled < length and (
            x <= self.max_x and
            x >= self.min_x and
            y <= self.max_y and
            y >= self.min_y):
            yield (x, y,)
            if x_inc == 0:
                next_x = None
            elif x_inc > 0:
                next_x = ceil(x / self.map.resolution) * self.map.resolution
                if next_x <= x:
                    next_x += self.map.resolution
            elif x_inc < 0:
                next_x = floor(x / self.map.resolution) * self.map.resolution
                if next_x >= x:
                    next_x -= self.map.resolution
       
            if y_inc == 0:
                next_y = None
            elif y == 0:
                if y_inc > 0:
                    next_y = self.map.resolution
                else:
                    next_y = -self.map.resolution
            elif y_inc > 0 and y > 0 or y_inc < 0 and y < 0:
                next_y = ceil(y / self.map.resolution) * self.map.resolution
                if next_y <= y:
                    next_y += self.map.resolution
            elif y_inc < 0 and y > 0 or y_inc < 0 and y > 0:
                next_y = floor(y / self.map.resolution) * self.map.resolution
                if next_y >= y:
                    next_y -= self.map.resolution

            if next_x is not None:
                dist_to_next_x = (next_x - x) / x_inc
            if next_y is not None:
                dist_to_next_y = (next_y - y) / y_inc

            if next_x is None or next_y is None:
                if next_x is not None:
                    dist_traveled += dist_to_next_x
                elif next_y is not None:
                    dist_traveled += dist_to_next_y
                else:
                    raise NotImplementedError()
            else:
                small_check = min(dist_to_next_x, dist_to_next_y)
                if (small_check < 0.001):
                    small_check = 0.001
                dist_traveled += small_check
            x = start_x + dist_traveled * cos(heading)
            y = start_y + dist_traveled * sin(heading)

    def _last_block(self, start_x, start_y, heading, length):
        '''
        Jump to the end of the ray trace
        '''
        dx = length * cos(heading)
        dy = length * sin(heading)
        return (start_x + dx, start_y + dy,)

    def threshold(self, threshold=0.5):
        for (x, y), probability in self.data.iteritems():
            print(x, y, probability)
            if probability >= threshold:
                yield x, y, probability