from django.contrib.gis.db.models import MultiPolygonField, PointField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .managers import CitiesQuerySet


class City(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('geo.models.city.name'))  # TODO run gettext engine with Polish and English language
    geo_area = MultiPolygonField(verbose_name='Obszar na mapie')  # TODO add '_', change analogously to 'name', add translations
    center = PointField(verbose_name='Punkt oznaczający centrum miasta')

    def __str__(self) -> str:
        """Return string representation for city"""
        return self.name

    objects = CitiesQuerySet.as_manager()


class Flat(models.Model):
    geo_point = PointField(verbose_name='Koordynaty mieszkania na mapie')

    def closest_city(self) -> City:
        return City.objects.distances_to_flat(self).first()

    def distance_from_city(self) -> float:
        """
        Get distance to the closest city

        If flat is placed in city area then return distance to center of the city
        otherwise return distance between flat and closest point or edge of city border.
        Unit is in kilometers.
        Return None if no city was found, the only possibility is if there are no cities are in database.
        """

        city = self.closest_city()
        if city:
            return city.compounddistance.km
        return None
