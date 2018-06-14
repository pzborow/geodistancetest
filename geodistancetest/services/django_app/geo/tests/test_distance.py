from django.contrib.gis.geos import (
    MultiPolygon,
    Point,
    Polygon,
)
from django.test import TestCase

from geo.models import City
from .factories import (
    CityFactory,
    FlatFactory,
)


def checkerboard(center: Point, size: int) -> MultiPolygon:
    """Generate two squares as multi polygon similar to checkerboard.

    y size is half of x size to get rectangle instead of square to ensure valid order of lat and long in distance calculation
    """

    top_left = Polygon((
        center,  # bottom right
        Point(x=center.x - size, y=center.y),  # bottom left
        Point(x=center.x - size, y=center.y + size / 2),  # top left
        Point(x=center.x, y=center.y + size / 2),  # top right
        center,  # bottom right
    ))
    bottom_right = Polygon((
        center,  # top left
        Point(x=center.x + size, y=center.y),  # top right
        Point(x=center.x + size, y=center.y - size / 2),  # bottom right
        Point(x=center.x, y=center.y - size / 2),  # bottom left
        center,  # top left
    ))
    return MultiPolygon(top_left, bottom_right)


class PartOfAreaDistanceTestCase(TestCase):

    """Test distance between flat and city's area parts.

    Dinstances calculated using http://boulter.com/gps/distance
    """

    def setUp(self):    # pylint: disable=invalid-name
        # City area consitsts of two rectangles, top left and bottom right
        self.city = CityFactory(geo_area=checkerboard(Point(x=0, y=0), 2.0))

    def test_distance_to_city_area_point(self):
        flat = FlatFactory(geo_point=Point(x=2, y=1)) # closest distance is to bottom right rect and top right point

        city_with_distances = City.objects.filter(pk=self.city.pk).distances_to_flat(flat).first()
        self.assertAlmostEqual(city_with_distances.areadistance.km, 110.57, 2)

    def test_distance_to_city_area_edge(self):
        flat = FlatFactory(geo_point=Point(x=1.5, y=1)) # closest distance is to bottom right rect and top edge

        city_with_distances = City.objects.filter(pk=self.city.pk).distances_to_flat(flat).first()
        self.assertAlmostEqual(city_with_distances.areadistance.km, 110.57, 2)

    def test_zero_distance(self):
        flat = FlatFactory(geo_point=Point(x=0, y=1)) # point is located on top left rect, top right corner

        city_with_distances = City.objects.filter(pk=self.city.pk).distances_to_flat(flat).first()
        self.assertAlmostEqual(city_with_distances.areadistance.km, 0, 2)


class CenterAndAreaDistanceTestCase(TestCase):

    """Test distance between flat and city'.

    Distances calculated using http://boulter.com/gps/distance
    """

    def setUp(self):    # pylint: disable=invalid-name
        # City area consists of two rectangles, top left and bottom right
        self.city = CityFactory(geo_area=checkerboard(Point(x=0, y=0), 2.0))

    def test_distances_inside_city_area(self):
        flat = FlatFactory(geo_point=Point(x=0.5, y=-0.5)) # flat is located at bottom right rectangle

        city_with_distances = City.objects.filter(pk=self.city.pk).distances_to_flat(flat).first()
        self.assertAlmostEqual(city_with_distances.centerdistance.km, 78.45, 2)
        self.assertAlmostEqual(city_with_distances.areadistance.km, 0.0, 2)
        self.assertAlmostEqual(city_with_distances.compounddistance.km, 78.45, 2)  # use distance to center of city

    def test_distances_outside_city_area(self):
        flat = FlatFactory(geo_point=Point(x=2, y=1)) # flat is located at absent top right rectangle, so it is not in city area

        city_with_distances = City.objects.filter(pk=self.city.pk).distances_to_flat(flat).first()
        self.assertAlmostEqual(city_with_distances.centerdistance.km, 248.58, 2)
        self.assertAlmostEqual(city_with_distances.areadistance.km, 110.57, 2)
        self.assertAlmostEqual(city_with_distances.compounddistance.km, 110.57, 2)  # use distanc to city area


class CitiesOrderTestCase(TestCase):

    """Test cities order by distance to given to flat'.

    Distances calculated using http://boulter.com/gps/distance
    """

    def setUp(self):    # pylint: disable=invalid-name
        self.cities = {
            'first': CityFactory(geo_area=checkerboard(Point(x=20, y=20), 1.0)),
            'second': CityFactory(geo_area=checkerboard(Point(x=10, y=10), 1.0)),
            'third': CityFactory(geo_area=checkerboard(Point(x=0, y=0), 2.0)),
        }

        self.flats = {
            'flat_near_first_city': FlatFactory(geo_point=Point(x=20, y=20)),
            'flat_near_third_city': FlatFactory(geo_point=Point(x=2, y=1)),
        }

    def test_order_of_cities(self):
        cities = City.objects.distances_to_flat(self.flats['flat_near_first_city'])
        self.assertListEqual(list(cities), [self.cities['first'], self.cities['second'], self.cities['third']])

        cities = City.objects.distances_to_flat(self.flats['flat_near_third_city'])
        self.assertListEqual(list(cities), [self.cities['third'], self.cities['second'], self.cities['first']])

    def test_closest_city(self):
        self.assertEqual(self.flats['flat_near_first_city'].closest_city(), self.cities['first'])
        self.assertEqual(self.flats['flat_near_third_city'].closest_city(), self.cities['third'])

    def test_closest_city_distance(self):
        self.assertAlmostEqual(self.flats['flat_near_third_city'].distance_from_city(), 110.57, 2)
        self.assertAlmostEqual(self.flats['flat_near_first_city'].distance_from_city(), 0, 2)

    def test_no_cities(self):
        City.objects.all().delete()
        self.assertAlmostEqual(self.flats['flat_near_third_city'].distance_from_city(), None, 2)
