import numpy as np
from itertools import chain

from animations import *


# Graph elemenets

class Vertex():

    def __init__(self, pos, neighbors=[], edges=[]):
        self.pos = pos
        self.neighbors = list(neighbors)
        self.edges = list(edges)
        # Polar coordinates
        x,y,z = pos
        xy = x*x + y*y
        self.theta = np.arctan2(z, np.sqrt(xy))
        self.phi = np.arctan2(y,x)

class Edge():

    def __init__(self, v0, v1, leds_per_edge):
        self.v0 = v0
        self.v1 = v1
        v0.neighbors.append(v1)
        v1.neighbors.append(v0)
        v0.edges.append(self)
        v1.edges.append(self)
        self.leds = [LED((1-t)*v0.pos + t*v1.pos) for t in np.linspace(0, 1, leds_per_edge+2)[1:-1]]

    def fill(self, color):
        for led in self.leds:
            led.set_color(color)

    def turn_off(self):
        for led in self.leds:
            led.turn_off()

class Face():

    def __init__(self, normal, vertices, edges):
        self.vertices = [v for v in vertices if np.linalg.norm(v.pos - normal) < 2]
        edges = [e for e in edges if e.v0 in self.vertices and e.v1 in self.vertices]
        # print(len(edges))
        # assert False
        self.edges = edges
        self.leds = list(chain(*[edge.leds for edge in self.edges]))
        self.color = np.zeros(3)

    def fill(self, color):
        for led in self.leds:
            led.set_color(color)

    def turn_off(self):
        for led in self.leds:
            led.turn_off()

class LED():

    def __init__(self, pos, neighbors=[], color=(0.,0.,0.)):
        self.pos = pos
        self.neighbors = list(neighbors)
        self.color = np.array(color)
        # Polar coordinates
        x,y,z = pos
        xy = x*x + y*y
        self.theta = np.arctan2(z, np.sqrt(xy))
        self.phi = np.arctan2(y,x)

    def set_color(self, color):
        np.copyto(self.color, color)

    def turn_off(self):
        self.color.fill(0)


# Main class

class Dodecahedron():

    def __init__(self, leds_per_edge):
        self.leds_per_edge = leds_per_edge

        # Dodecahedron coordinates
        r = (1 + np.sqrt(5)) / 2
        coords = np.array([
            (1, 1, 1),   (1, 1, -1),   (1, -1, 1),   (1, -1, -1),
            (-1, 1, 1),  (-1, 1, -1),  (-1, -1, 1),  (-1, -1, -1),
            (0, r, 1/r), (0, r, -1/r), (0, -r, 1/r), (0, -r, -1/r),
            (1/r, 0, r), (1/r, 0, -r), (-1/r, 0, r), (-1/r, 0, -r),
            (r, 1/r, 0), (r, -1/r, 0), (-r, 1/r, 0), (-r, -1/r, 0)
        ])
        # Icosahedron coordinates
        face_normals = np.array([
            (0, 1, r), (0, 1, -r), (0, -1, r), (0, -1, -r),
            (1, r, 0), (1, -r, 0), (-1, r, 0), (-1, -r, 0),
            (r, 0, 1), (r, 0, -1), (-r, 0, 1), (-r, 0, -1)
        ])

        # Construct dodecahedron graph
        self.vertices = [Vertex(c) for c in coords]
        self.edges = []
        for i in range(len(coords)):
            for j in range(i):
                if 0 < np.linalg.norm(coords[i] - coords[j]) <= 2/r + 0.01:
                    self.edges.append(Edge(self.vertices[i], self.vertices[j], self.leds_per_edge))
        for v in self.vertices:
            e0, e1, e2 = v.edges
            if v is e0.v0: e0.neighbors0 = [e1,e2]
            if v is e0.v1: e0.neighbors1 = [e1,e2]
            if v is e1.v0: e1.neighbors0 = [e0,e2]
            if v is e1.v1: e1.neighbors1 = [e0,e2]
            if v is e2.v0: e2.neighbors0 = [e0,e1]
            if v is e2.v1: e2.neighbors1 = [e0,e1]
        self.faces = [Face(fn, self.vertices, self.edges) for fn in face_normals]

        # Construct separate LED neighborhood graph
        self.leds = list(chain(*[e.leds for e in self.edges]))
        for i in range(len(self.leds)):
            for j in range(i):
                if 0 < np.linalg.norm(self.leds[i].pos - self.leds[j].pos) <= 1.999 * (2/r) / (leds_per_edge + 1):
                    self.leds[i].neighbors.append(self.leds[j])
                    self.leds[j].neighbors.append(self.leds[i])

        # Get animations going
        self.animation_index = -1
        self.next_animation()

    def turn_off(self):
        for led in self.leds:
            led.turn_off()

    def get_leds(self):
        return np.stack([led.pos for led in self.leds])

    def get_colors(self):
        return np.stack([led.color for led in self.leds])

    def next_animation(self):
        self.animation_index = (self.animation_index + 1) % len(ANIMATION_CYCLE)
        self.animation = ANIMATION_CYCLE[self.animation_index](self)
        self.animation.initialize()



if __name__ == '__main__':
    d = Dodecahedron(17)