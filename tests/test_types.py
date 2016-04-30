import unittest
import itertools
from stl.types import *


class TestTypes(unittest.TestCase):

    def test_facet_geometry(self):
        facet = Facet(
            (1, 0, 0),
            [
                (0, 0, 0),
                (1, 0, 0),
                (0, 1, 0),
            ],
        )
        self.assertEqual(facet.a, 1.0)
        self.assertEqual(facet.b, 1.0)
        self.assertAlmostEqual(facet.c, 1.4142135623730951)

        self.assertAlmostEqual(
            facet.perimeter,
            1.0 + 1.0 + 1.4142135623730951,
        )

        self.assertAlmostEqual(facet.area, 0.5)

    def test_solid_geometry(self):
        solid = Solid(
            "test",
            [
                Facet(
                    (1, 0, 0),
                    [
                        (0, 0, 0),
                        (1, 0, 0),
                        (0, 1, 0),
                    ],
                ),
                Facet(
                    (1, 0, 0),
                    [
                        (0, 0, 0),
                        (1, 0, 0),
                        (0, 0, 1),
                    ],
                ),
            ],
        )

        self.assertAlmostEqual(solid.surface_area, 0.5 + 0.5)

    def test_vector3d_sort(self):
        v1 = Vector3d(1, 2, 3)
        v2 = Vector3d(4, 5, 6)
        v3 = Vector3d(7, 8, 9)
        for vertex_permutation in itertools.permutations([v1, v2, v3]):
            self.assertEqual(sorted(vertex_permutation), [v1, v2, v3])

    def test_facet_sort(self):
        v1 = (1, 2, 3)
        v2 = (4, 5, 6)
        v3 = (7, 8, 9)

        facet = Facet([0, 0, 0], [v1, v2, v3])
        facet.sort_vertices()
        self.assertEqual(facet, Facet([0, 0, 0], [v1, v2, v3]))

        facet = Facet([0, 0, 0], [v3, v1, v2])
        facet.sort_vertices()
        self.assertEqual(facet, Facet([0, 0, 0], [v1, v2, v3]))

        facet = Facet([0, 0, 0], [v3, v2, v1])
        facet.sort_vertices()
        self.assertEqual(facet, Facet([0, 0, 0], [v1, v3, v2]))

    def test_solid_sort(self):
        f0 = Facet(
            (1, 0, 0),
            [
                (0, 0, 0),
                (1, 0, 0),
                (0, 0, 1),
            ],
        )
        f0b = Facet(
            (1, 0, 0),
            [
                (1, 0, 0),
                (0, 0, 1),
                (0, 0, 0),
            ],
        )
        f1 = Facet(
            (1, 0, 0),
            [
                (0, 0, 0),
                (1, 0, 0),
                (0, 1, 0),
            ],
        )

        solid0 = Solid("test", [f0, f1])
        solid0.sort_facets()
        expected_solid0 = Solid("test", [f0, f1])
        self.assertEqual(solid0, expected_solid0)

        solid1 = Solid("test", [f1, f0])
        solid1.sort_facets()
        expected_solid1 = Solid("test", [f0, f1])
        self.assertEqual(solid1, expected_solid1)

        solid2 = Solid("test", [f1, f0b])
        solid2.sort_facets()
        expected_solid2 = Solid("test", [f0, f1])
        self.assertEqual(solid2, expected_solid2)

    def test_map_coordinates(self):
        v = Vector3d(1.1, 2.1, 3.1)
        self.assertEqual(v.map_coordinates(round), Vector3d(1, 2, 3))

    def test_recalculate_normal(self):
        f = Facet([0, 0, 0], [[0, 0, 0], [5, 0, 0], [0, 5, 0]])
        f.recalculate_normal()
        self.assertEqual(f.normal, Vector3d(0, 0, 1))

        f = Facet([0, 0, 0], [[0, 0, 0], [0, 2, 0], [5, 0, 0]])
        f.recalculate_normal()
        self.assertEqual(f.normal, Vector3d(0, 0, -1))

    def test_map_vertices(self):
        facet = Facet([0, 0, -1], [[0, 0, 0], [0, 2, 0], [5, 0, 0]])
        f_new = Facet(None, [Vector3d(*(coord+1 for coord in vertex))
                             for vertex in facet])
        f_new.recalculate_normal()
        self.assertEqual(f_new, Facet([0, 0, -1],
                                      [[1, 1, 1], [1, 3, 1], [6, 1, 1]]))

    def test_split_to_triangles(self):
        facet = Facet(None, [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        f_new = facet.split_to_triangles()
        self.assertEqual(list(f_new),
                         [Facet([0, 0, 1], [[0, 0, 0], [1, 0, 0], [1, 1, 0]]),
                          Facet([0, 0, 1], [[0, 0, 0], [1, 1, 0], [0, 1, 0]])])

    def test_join_facets(self):
        facet = Facet(None, [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
        f_split = list(facet.split_to_triangles())
        f_join = f_split[1].join(f_split[0])
        self.assertEqual(f_join,
                         Facet([0, 0, 1],
                               [[1, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0]]))
