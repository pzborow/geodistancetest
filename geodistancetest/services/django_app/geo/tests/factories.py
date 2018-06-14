"""Test factories for the models from the geo application."""
import random

import factory
import faker
from factory.fuzzy import BaseFuzzyAttribute

from django.contrib.gis.geos import (
    MultiPolygon,
    Point,
    Polygon,
)


faker_instance = faker.Faker()


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(
            x=random.uniform(-180.0, 180.0),
            y=random.uniform(-90.0, 90.0)
        )


def square(top_left: Point, bottom_right: Point) -> Polygon:
    return Polygon((
        top_left,
        Point(x=bottom_right.x, y=top_left.y),  # top right
        bottom_right,
        Point(x=top_left.x, y=bottom_right.y),  # bottom left
        top_left,  # and again top left to close polygon
    ))


class FuzzySquareArea(BaseFuzzyAttribute):
    def fuzz(self) -> MultiPolygon:
        size = random.uniform(1, 2)
        base = Point(
            x=random.uniform(-180.0 + size, 180.0 - size),
            y=random.uniform(-90.0 + size, 90.0 - size)
        )

        return MultiPolygon(square(
            Point(x=base.x-size, y=base.y+size),
            Point(x=base.x+size, y=base.y-size),
        ))


class CityFactory(factory.django.DjangoModelFactory):

    """A factory for the City model."""

    name = factory.LazyFunction(faker_instance.city)
    geo_area = FuzzySquareArea()
    center = factory.LazyAttribute(lambda obj: obj.geo_area.centroid)

    class Meta:

        """Options for the factory."""

        model = 'geo.City'


class FlatFactory(factory.django.DjangoModelFactory):

    """A factory for the Flat model."""

    geo_point = FuzzyPoint()

    class Meta:

        """Options for the factory."""

        model = 'geo.Flat'
