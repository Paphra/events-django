from django.contrib.sitemaps import Sitemap
from .models import Event

class PostSitemap(Sitemap):
	changefreq = "daily"
	priority = 0.9

	def items(self):
		return Event.objects.filter(status=1)
	
	def lastmod(self, obj):
		return obj.updated_on