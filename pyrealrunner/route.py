#
# Created by Renatus Madrigal on 02/14/2025
#

# This module contains the Route class, which is used to represent a route.

import math
import random
from copy import deepcopy
from typing import Dict, List
from geopy.distance import geodesic

X_PI = math.pi * 3000.0 / 180.0
PI = math.pi
EARTH_A = 6378245.0  # Long radius
EARTH_EE = 0.00669342162296594323  # Square of Eccentricity
EPS = 1e-6


def hypotenuse(a: float, b: float) -> float:
    return math.sqrt(a**2 + b**2)


def geo_distance(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return geodesic((p1['lat'], p1['lng']), (p2['lat'], p2['lng'])).meters


def smooth(start: float, end: float, factor: float) -> float:
    factor = (factor-start)/(end-start) * PI
    return math.sin(factor) ** 2


def bd09_to_wgs84(p: Dict[str, float]) -> Dict[str, float]:
    wgs84_p = {}

    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y
        ret += 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
                math.sin(2.0 * x * PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * PI) + 40.0 *
                math.sin(y / 3.0 * PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * PI) + 320 *
                math.sin(y * PI / 30.0)) * 2.0 / 3.0
        return ret

    def transform_lon(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x
        ret += 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * PI) + 20.0 *
                math.sin(2.0 * x * PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * PI) + 40.0 *
                math.sin(x / 3.0 * PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * PI) + 300.0 *
                math.sin(x / 30.0 * PI)) * 2.0 / 3.0
        return ret

    x = p['lng'] - 0.0065
    y = p['lat'] - 0.006
    z = hypotenuse(x, y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)

    gcj_lng = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)

    d_lat = transform_lat(gcj_lng - 105.0, gcj_lat - 35.0)
    d_lng = transform_lon(gcj_lng - 105.0, gcj_lat - 35.0)

    rad_lat = gcj_lat / 180.0 * PI
    magic = math.sin(rad_lat)
    magic = 1 - EARTH_EE * magic * magic
    sqrt_magic = math.sqrt(magic)

    d_lng = (d_lng * 180.0) / (EARTH_A /
                               sqrt_magic * math.cos(rad_lat) * PI)
    d_lat = (d_lat * 180.0) / (EARTH_A *
                               (1 - EARTH_EE) / (magic * sqrt_magic) * PI)

    wgs84_p["lat"] = gcj_lat * 2 - gcj_lat - d_lat
    wgs84_p["lng"] = gcj_lng * 2 - gcj_lng - d_lng

    return wgs84_p


class Route:
    def __init__(self, path: List[Dict[str, float]] = []):
        self.path = deepcopy(path)
        self.original_path = deepcopy(path)
        if len(self.path) > 0:
            self.path.append(self.path[0])  # Close the loop
        self.run_path = self.path
        self.center = self.calc_center()

    def calc_center(self):
        if len(self.path) == 0:
            return {"lat": 0, "lng": 0}
        lat = 0
        lng = 0
        for p in self.path:
            lat += p['lat']
            lng += p['lng']
        return {"lat": lat / len(self.path), "lng": lng / len(self.path)}

    def reset(self):
        self.path = deepcopy(self.original_path)

    def extent_path(self, dx: float):
        if len(self.path) == 0:
            return
        result = [self.path[0].copy()]
        for idx in range(1, len(self.path)):
            dis = geo_distance(self.path[idx-1], self.path[idx])
            # assuming that the distance between two points is long enough
            n = int(dis / dx)
            a = self.path[idx-1]
            b = self.path[idx]
            for i in range(1, n):
                lat = a['lat'] + (b['lat'] - a['lat']) * i / n
                lng = a['lng'] + (b['lng'] - a['lng']) * i / n
                result.append({'lat': lat, 'lng': lng})
            result.append(b.copy())
        self.path = result
        self.run_path = self.path
        self.center = self.calc_center()

    def randomize_path(self, factor: float = 0.2, sigma: float = 1.0):
        self.run_path = deepcopy(self.path)
        seed = random.SystemRandom().getrandbits(32)
        random.seed(seed)
        parts = random.randint(5, 8)
        for i in range(parts):
            start = int(len(self.run_path) * i / parts)
            end = int(len(self.run_path) * (i+1) / parts)
            offset = random.normalvariate(0, sigma) * factor
            for j in range(start, end):
                pt = self.run_path[j]
                ct = self.center
                dlat = pt['lat'] - ct['lat']
                dlng = pt['lng'] - ct['lng']
                dis = hypotenuse(dlat, dlng)
                if abs(dis) < EPS:
                    continue
                pt['lat'] += dlat * offset * smooth(start, end, j) / dis
                pt['lng'] += dlng * offset * smooth(start, end, j) / dis

    def generate_path(self, **kwargs):
        self.reset()
        v = kwargs.get("v", 3.0)
        dt = kwargs.get("dt", 0.2)
        self.extent_path(v * dt)
        self.randomize_path(
            kwargs.get("factor", 0.2),
            kwargs.get("sigma", 1.0)
        )
        pass
