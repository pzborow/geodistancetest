from django.contrib.gis.db.models.functions import Distance
from django.db.models import (
    Case,
    F,
    QuerySet,
    When
)


class CitiesQuerySet(QuerySet):

    def distances_to_flat(self, flat) -> QuerySet:
        """Return cities with distance to given flat in order from closest to furthest

        select st_distance(
            st_geomfromtext('POINT (0 0)'),
            st_geomfromtext('POLYGON ((1 1, 2 1, 2 2, 1 2, 1 1))')
        )

        This returns 1.414213, which is the expected value between the point in (0, 0) and the closest part of the polygon at (1, 1).
        Another example, with an edge this time:

        select st_distance(
            st_geomfromtext('POINT (0 0)'),
            st_geomfromtext('POLYGON ((1 1, 2 1, 2 -1, 1 -1, 1 1))')
        )

        This returns 1. Finally, if your point intersects the polygon anywhere, the distance will be zero:

        select st_distance(
            st_geomfromtext('POINT (0 0)'),
            st_geomfromtext('POLYGON ((1 1, 1 -1, -1 -1, -1 1, 1 1))')
        )
        """

        # XXX Turn off spheroid on real environment, it is much slower than sphere,
        # according to https://docs.djangoproject.com/en/2.0/ref/contrib/gis/functions/#length
        # Left turned on for testing and playground purpose.
        # You may use here setting's environments to decide which algorithm to use. f.e. for testing use spheroid and for production don't
        # another solution is to pass parameter to use or not spheroid

        case = Case(When(areadistance=0, then=F('centerdistance')), default=F('areadistance'))
        return (
            self.annotate(areadistance=Distance('geo_area', flat.geo_point, spheroid=True)).
            annotate(centerdistance=Distance('center', flat.geo_point, spheroid=True)).
            annotate(compounddistance=case).
            order_by('compounddistance')
        )
