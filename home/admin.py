from django.contrib import admin
from django.contrib.auth.models import User
from django_summernote.admin import SummernoteModelAdmin
from django_summernote.admin import SummernoteModelAdmin

from .models import Event, Comment, Subscriber, About, Partner, Booking
from .models import Category, ImageGroup, Profile, Image, Location


class ProfileInline(admin.StackedInline):
	model = Profile

class UserAdmin(admin.ModelAdmin):
	inlines = [ProfileInline]
	list_display = (
		'username', "first_name", 'last_name', 'date_joined')
	search_fields = [
		'username', 'first_name', 'last_name', 'email']
	list_filter = ['date_joined']

class ImageInline(admin.TabularInline):
	model = Image
	exclude = ['data', 'description']

class ImageGroupAdmin(admin.ModelAdmin):
	inlines = [ImageInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(ImageGroup, ImageGroupAdmin)
admin.site.register(Category)
admin.site.register(Subscriber)

class AboutAdmin(SummernoteModelAdmin):
	summernote_fields = ('info',)

admin.site.register(About, AboutAdmin)

class EventAdmin(SummernoteModelAdmin):
	list_display = ('title', 'location', 'amount', 'status', 'seats', 'created_on')
	list_filter = ('status', 'location', 'created_on')
	search_fields = ['title', 'location', 'content']
	prepopulated_fields = {'slug': ('title',)}
	actions = ['publish_events', 'draft_events']

	summernote_fields = ('content')

	def publish_events(self, request, queryset):
		queryset.update(status=1)
	
	def draft_events(self, request, queryset):
		queryset.update(status=0)

class CommentAdmin(SummernoteModelAdmin):
	list_display = ('name', 'event', 'created_on', 'active')
	list_filter = ('active', 'created_on')
	search_fields = ('name', 'email', 'body')
	actions = ['approve_comments', 'disapprove_comments']
	
	summernote_fields = ('body', )
	def approve_comments(self, request, queryset):
		queryset.update(active=True)
	
	def disapprove_comments(self, request, queryset):
		queryset.update(active=False)

admin.site.register(Event, EventAdmin)
admin.site.register(Comment, CommentAdmin)

class PartnerAdmin(admin.ModelAdmin):
	list_display = ('name', 'email','phone', 'address', 'created_on')
	search_fields = ['name', 'email', 'phone']
	list_filter = ['created_on', 'active']

admin.site.register(Partner, PartnerAdmin)

admin.site.register(Location)

class BookingAdmin(admin.ModelAdmin):
	list_display = ('FirstName', 'LastName','Email', 'PhoneNumber', 'ticket_no', 'status', 'created_on')
	search_fields = ['FirstName', 'LastName', 'Email', 'PhoneNumber', 'ticket_no']
	list_filter = ['status', 'created_on']
	
admin.site.register(Booking, BookingAdmin)