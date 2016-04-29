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
        print (solid0)
        expected_solid0 = Solid("test", [f0, f1])
        self.assertEqual(solid0, expected_solid0)

        solid1 = Solid("test", [f1, f0])
        solid1.sort_facets()
        print (solid1)
        expected_solid1 = Solid("test", [f0, f1])
        self.assertEqual(solid1, expected_solid1)

        solid2 = Solid("test", [f1, f0b])
        solid2.sort_facets()
        print (solid2)
        expected_solid2 = Solid("test", [f0, f1])
        self.assertEqual(solid2, expected_solid2)
