from . import views
from django.urls import path
from .feeds import LatestPostsFeed

app_name = 'events'
urlpatterns = [

		# Feeds
    path("feed/rss", LatestPostsFeed(), name='post_feed'),
		
		# index
		path('', views.index, name="index" ),
		path('categories', views.categories, name="categories"),
		path('categories/<int:pk>/', views.category, name='category'),

		path('about', views.about, name='about'),
		path('filter', views.filter, name="filter"),
		path('search', views.search, name="search"),
		path('subscribe', views.subscribe, name="subscribe"),
		path('subscribed/<int:pk>/', views.subscribed, name="subscribed"),
		path('unsubscribe/<int:pk>/', views.unsubscribe, name="unsubscribe"),
		path('unsubscribed/<int:pk>/', views.unsubscribed, name="unsubscribed"),
		path('resubscribe/<int:pk>/', views.resubscribe, name="resubscribe"),
		
		path('admin/images/', views.images, name="images"),
		path('admin/images/group/<int:pk>/', views.images_group, name="images_group"),
		path('admin/images/<int:image_id>/', views.image_detail, name="image_detail"),

		# events
		path("events", views.index, name="events"),
		path("history", views.history, name="history"),
		path("upcoming", views.upcoming, name="upcoming"),
		path('events/<int:pk>/book', views.booking, name="booking"),
		path('events/<slug:slug>/', views.detail, name='detail'),
		path('events/next/<int:days>/', views.next, name='next'),

		path('book', views.book, name="book"),
		path('booking', views.book_status, name="book_status"),
		path('booked', views.booked, name="booked"),
		path('bookfail', views.book_fail, name="book_fail"),

		path('logout', views.logout, name="logout")
]
