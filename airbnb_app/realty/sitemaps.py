from django.contrib.sitemaps import Sitemap

from .models import Realty


class RealtySiteMap(Sitemap):
    """SiteMap for Realty objects."""

    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Realty.available.all()

    def lastmod(self, obj: Realty):
        return obj.updated
