from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_summernote.fields import SummernoteTextField

STATUS = (
	(0, "Draft"),
	(1, 'Publish')
)

class Category(models.Model):
	"""
	The Categories of the events under which they are made
	"""
	name = models.CharField(max_length=30)
	description = models.TextField()

	class Meta:
		verbose_name_plural = "Categories"


	def __str__(self):
			return self.name

class ImageGroup(models.Model):
	"""
	Stores the image groups forexample:
		1. Users
		2. Events
		3. Questions etc
	"""
	name = models.CharField(max_length=50)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name

class Image(models.Model):
	""" 
	Stores all the images of the System
	"""
	title = models.CharField(max_length=50)
	data = models.TextField(blank=True)
	group = models.ForeignKey(
		ImageGroup, on_delete=models.SET_NULL, null=True, blank=True,
		related_name="images")
	description = models.TextField(blank=True)
	
	def __str__(self):
		return self.title

class Subscriber(models.Model):
	"""
	Store all the Users Who Subscribe for timely updates
	"""
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	email = models.EmailField(max_length=100)
	subscribed = models.BooleanField(default=True)

	def __str__(self):
		return self.email
	
	def name(self):
		return self.first_name + ' ' + self.last_name

class About(models.Model):
	site_title = models.CharField(max_length=200)
	info = models.TextField()
	last_modified = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'About Us'
		verbose_name_plural = 'About Us'

	def __str__(self):
		return "About Us"

class Partner(models.Model):
	name = models.CharField(max_length=200)
	email = models.EmailField(max_length=100)
	phone = models.CharField(max_length=30)
	website = models.CharField(max_length=100)
	address = models.CharField(max_length=400)
	image = models.ForeignKey(
		Image, related_name="partners", on_delete=models.SET_NULL, 
		null=True, blank=True)
	description = SummernoteTextField()
	active = models.BooleanField(default=True)
	created_on = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		ordering = ['-created_on']

	def __str__(self):
		return self.name

class Profile(models.Model):
	"""
	Stores extra information about the user
	"""
	user = models.OneToOneField(
		User, on_delete=models.CASCADE)
	partner = models.ForeignKey(
		Partner, on_delete=models.SET_NULL, blank=True, null=True,
		related_name='users')
	phone = models.CharField(max_length=15, blank=True)
	facebook = models.CharField(verbose_name='Facebook Username',
		max_length=20, blank=True)
	bio = models.TextField(blank=True)
	address = models.CharField(max_length=100, blank=True)
	
	def __str__(self):
		return self.user.first_name + ' ' + self.user.last_name 
	
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()

class Location(models.Model):
	name = models.CharField(max_length=200)
	address = models.CharField(max_length=300)
	email = models.EmailField(max_length=100, blank=True)
	phone = models.CharField(max_length=30, blank=True)
	website = models.CharField(max_length=100, blank=True)
	coordinates = models.CharField(max_length=100, blank=True)
	description = SummernoteTextField(blank=True)
	owner = models.CharField(max_length=100, blank=True)

	def __str__(self):
		return self.name

class Event(models.Model):
	title = models.CharField(max_length=200, unique=True)
	slug = models.SlugField(max_length=200, unique=True)
	author = models.ForeignKey(
		User, on_delete=models.CASCADE, related_name='events')
	updated_on = models.DateTimeField(auto_now=True)
	content = models.TextField(blank=True)
	created_on = models.DateTimeField(auto_now_add=True)
	status = models.IntegerField(choices=STATUS, default=0)
	seats = models.IntegerField(default=0)
	starts_on = models.DateTimeField('Start Date')
	ends_on = models.DateTimeField('End Date')
	amount = models.IntegerField('Amount in UGX', default=0)
	discount = models.IntegerField(
		verbose_name='Percentage Discount', default=0)
	location = models.ForeignKey(
		Location, on_delete=models.CASCADE,
		related_name='events')
	category = models.ForeignKey(
		Category, on_delete=models.SET_NULL, null=True, blank=True,
		related_name='events')
	image = models.ForeignKey(
		Image, on_delete=models.SET_NULL, null=True, blank=True)
	
	class Meta:
		ordering = ['-created_on']
	
	def __str__(self):
		return self.title
	
	def get_absolute_url(self):
		from django.urls import reverse
		return reverse("eventsevents_detail", kwargs={"slug": str(self.slug)})
	
class Comment(models.Model):
	"""
	Coments for Events
	"""
	name = models.CharField( max_length=100)
	email = models.EmailField(max_length=100)
	body = models.TextField()
	created_on = models.DateTimeField(auto_now_add=True)
	event = models.ForeignKey(
		Event, on_delete=models.CASCADE, related_name="comments")
	active = models.BooleanField(default=False)


	class Meta:
		ordering = ['-created_on']

	def __str__(self):
		return 'Comment on {} by {}'.format(self.event, self.name)

PAY_STATUS = (
	(0, 'Unpaid'),
	(1, 'Paid'),
)

CLEARANCE = (
	(0, 'Uncleared'),
	(1, 'Cleared')
)

class Booking(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email = models.EmailField(max_length=100)
	description = SummernoteTextField()
	reference = models.IntegerField()

	amount = models.IntegerField(default=0)
	seats = models.IntegerField(default=1)
	discount = models.IntegerField(default=0)

	payment_status = models.IntegerField(choices=PAY_STATUS, default=0)
	clearance = models.IntegerField(choices=CLEARANCE, default=0)

	ticket = models.CharField(max_length=15, blank=True)
	
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.email