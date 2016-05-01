import itertools
import math
import functools
import numpy
import sys


class Solid(object):
    """
    A solid object; the root element of an STL file.
    """

    #: The name given to the object by the STL file header.
    name = None

    #: :py:class:`list` of :py:class:`stl.Facet` objects representing the
    #: facets (triangles) that make up the exterior surface of this object.
    facets = []

    def __init__(self, name=None, facets=None):
        self.name = name
        self.facets = facets if facets is not None else []

    def add_facet(self, *args, **kwargs):
        """
        Append a new facet to the object. Takes the same arguments as the
        :py:class:`stl.Facet` type.
        """
        self.facets.append(Facet(*args, **kwargs))

    @property
    def surface_area(self):
        """
        The sum of the areas of all facets in the object.
        """
        return sum([facet.area for facet in self.facets])

    def write_binary(self, file):
        """
        Write this object to a file in STL *binary* format.

        ``file`` must be a file-like object (supporting a ``write`` method),
        to which the data will be written.
        """
        from stl.binary import write
        write(self, file)

    def write_ascii(self, file):
        """
        Write this object to a file in STL *ascii* format.

        ``file`` must be a file-like object (supporting a ``write`` method),
        to which the data will be written.
        """
        from stl.ascii import write
        write(self, file)

    def sort_facets(self):
        """
        Sort each facet in this solid and then sort the facets list.
        """
        for f in self.facets:
            f.sort_vertices()
        self.facets.sort()

    def remove_planar_edge(self):
        """
        Remove a planar edge that are between facets that are coplanar.

        Facets can only be joined if they have the same normal and
        they share an edge.

        Returns True if an edge was removed.
        """
        for i, j in itertools.product(range(len(self.facets)),
                                      range(len(self.facets))):
            if i == j:
                continue
            joined_facet = self.facets[i].join(self.facets[j])
            if joined_facet:
                sys.stderr.write("joining %d,%d" % (i,j))
                new_facets = [f[1]
                              for f in enumerate(self.facets)
                              if f[0] != i and f[0] != j]
                new_facets.append(joined_facet)
                self.facets = new_facets
                return True
        return False

    def remove_planar_edges(self):
        count = 0
        while self.remove_planar_edge():
            count += 1
        return count

    def __eq__(self, other):
        if type(other) is Solid:
            if self.name != other.name:
                return False
            if len(self.facets) != len(other.facets):
                return False
            for i, self_facet in enumerate(self.facets):
                if self_facet != other.facets[i]:
                    return False
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<stl.types.Solid name=%r, facets=%r>' % (
            self.name,
            self.facets,
        )

    def __iter__(self):
        for f in self.facets:
            yield f


@functools.total_ordering
class Facet(object):
    """
    A facet (triangle) from a :py:class:`stl.Solid`.
    """

    #: Raw binary attribute bytes. According to the STL spec these are unused
    #: and thus this should always be empty, but some modeling software
    #: encodes non-standard data in here which callers may wish to access.
    #:
    #: At present these attribute bytes are populated only when reading binary
    #: STL files (since ASCII STL files have no place for this data) *and*
    #: they are ignored when *writing* a binary STL file, so round-tripping
    #: a file through this library will lose the non-standard attribute data.
    attributes = None

    #: The 'normal' vector of the facet, as a :py:class:`stl.Vector3d`.
    normal = None

    #: 3-element sequence of :py:class:`stl.Vector3d` representing the
    #: facet's three vertices, in order.
    vertices = None

    def __init__(self, normal, vertices, attributes=None):
        self.vertices = list(
            Vector3d(*x) for x in vertices
        )
        if normal:
            self.normal = Vector3d(*normal)
        else:
            self.recalculate_normal()

    def __eq__(self, other):
        if type(other) is Facet:
            return (
                self.normal == other.normal and
                self.vertices == other.vertices
            )
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.vertices < other.vertices

    def __repr__(self):
        return '<stl.types.Facet normal=%r, vertices=%r, area=%r>' % (
            self.normal,
            self.vertices,
            self.area,
        )

    def __iter__(self):
        for v in self.vertices:
            yield v

    @property
    def a(self):
        """
        The length the side of the facet between vertices[0] and vertices[1]
        """
        return math.sqrt(
                pow((self.vertices[0].x - self.vertices[1].x), 2) +
                pow((self.vertices[0].y - self.vertices[1].y), 2) +
                pow((self.vertices[0].z - self.vertices[1].z), 2)
                )

    @property
    def b(self):
        """
        The length of the side of the facet between vertices[0] and vertices[2]
        """
        return math.sqrt(
                pow((self.vertices[0].x - self.vertices[2].x), 2) +
                pow((self.vertices[0].y - self.vertices[2].y), 2) +
                pow((self.vertices[0].z - self.vertices[2].z), 2)
                )

    @property
    def c(self):
        """
        The length of the side of the facet between vertices[1] and vertices[2]
        """
        return math.sqrt(
                pow((self.vertices[1].x - self.vertices[2].x), 2) +
                pow((self.vertices[1].y - self.vertices[2].y), 2) +
                pow((self.vertices[1].z - self.vertices[2].z), 2)
                )

    @property
    def perimeter(self):
        """
        The length of the perimeter of the facet.
        """
        return self.a + self.b + self.c

    @property
    def area(self):
        """
        The surface area of the facet, as computed by Heron's Formula.
        """
        result = 0
        for f in self.split_to_triangles():
            p = f.perimeter / 2.0
            result += abs(math.sqrt(p * (p - f.a) * (p - f.b) * (p - f.c)))
        return result


    def sort_vertices(self):
        """
        Sort the vertices of the facet, maintaining round-robin order.
        """
        swap_enumerated = [(p[1], p[0]) for p in enumerate(self.vertices)]
        index_of_min = min(swap_enumerated)[1]
        reindexed_enumerated = [((p[1]-index_of_min) % 3, p[0])
                                for p in swap_enumerated]
        self.vertices = [p[1] for p in sorted(reindexed_enumerated)]

    def recalculate_normal(self):
        vertices = [numpy.array(x) for x in self.vertices]
        normal = numpy.cross(vertices[1]-vertices[0], vertices[2]-vertices[1])
        length = numpy.linalg.norm(normal)
        if length != 0:
            self.normal = Vector3d(*(normal/length))
        else:
            self.normal = None

    def split_to_triangles(self):
        """
        Return triangular facets.

        If the shape has just 3 vertices, return a list of just the
        original facet.  Otherwise, return a list of triangular
        facets.  The number of returned facets is the number of
        vertices minus 2.

        """
        for vertices in zip(self.vertices[1:], self.vertices[2:]):
            yield Facet(self.normal,
                        [self.vertices[0], vertices[0], vertices[1]])

    def join(self, other):
        """
        Returns a new facet joining if possible, otherwise None.
        """
        if self.normal != other.normal:
            return None
        # If there is at least 1, including
        # wrap-around, then the facets can be joined.
        for i0 in range(len(self.vertices)):
            i1 = (i0 + 1) % len(self.vertices)
            for j0 in range(len(other.vertices)):
                j1 = (j0 + 1) % len(other.vertices)
                if(self.vertices[i0] == other.vertices[j1] and
                   self.vertices[i1] == other.vertices[j0]):
                    # Found a common edge.
                    new_vertices = []
                    i = i1
                    while i != i0:
                        new_vertices.append(self.vertices[i])
                        i = (i + 1) % len(self.vertices)
                    j = j1
                    while j != j0:
                        new_vertices.append(other.vertices[j])
                        j = (j + 1) % len(other.vertices)
                    return Facet(self.normal, new_vertices)
        return None


@functools.total_ordering
class Vector3d(tuple):
    """
    Three-dimensional vector.

    Used to represent both normals and vertices of :py:class:`stl.Facet`
    objects.

    This is a subtype of :py:class:`tuple`, so can also be treated like a
    three-element tuple in (``x``, ``y``, ``z``) order.
    """

    def __new__(cls, x, y, z):
        return tuple.__new__(cls, (x, y, z))

    def __init__(self, x, y, z):
        pass

    @property
    def x(self):
        """
        The X value of the vector, which most applications interpret
        as the left-right axis.
        """
        return self[0]

    @x.setter
    def x(self, value):
        self[0] = value

    @property
    def y(self):
        """
        The Y value of the vector, which most applications interpret
        as the in-out axis.
        """
        return self[1]

    @y.setter
    def y(self, value):
        self[1] = value

    @property
    def z(self):
        """
        The Z value of the vector, which most applications interpret
        as the up-down axis.
        """
        return self[2]

    @z.setter
    def z(self, value):
        self[2] = value

    def map_coordinates(self, fn):
        return Vector3d(*(fn(c) for c in self))
