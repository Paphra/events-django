from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from django.urls import reverse

from .models import Event

class LatestPostsFeed(Feed):
	title = 'Events'
	link =""
	description = "Latest Events."

	def items(self):
		return Event.objects.filter(status=1)
	
	def item_title(self, item):
		return item.title
	
	def item_description(self, item):
		return truncatewords(item.content, 30)