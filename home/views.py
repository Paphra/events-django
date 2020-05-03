import base64
import datetime
import random
import requests

from django.utils import timezone
from django.views import generic
from django.shortcuts import (render, get_object_or_404, HttpResponseRedirect, HttpResponse)
from django.core.paginator import (Paginator, PageNotAnInteger, EmptyPage)
from django.contrib.auth.models import Group, User

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchVector

from .models import Image, ImageGroup, Category, Subscriber, About, Partner, Event, Booking
from .forms import CommentForm

from urllib.parse import quote, urlencode
from oauthlib import oauth1

import xml.etree.ElementTree as etree
from cgi import escape

# Constants given by service provider
CONSUMER_KEY = settings.PESAPAL_CONSUMER_KEY
CONSUMER_SECRET = settings.PESAPAL_CONSUMER_SECRET
CALLBACK = settings.PESAPAL_CALLBACK

# Values that choose client application
IFRAME_LINK = settings.PESAPAL_IFRAME_LINK
QUERY_STATUS = settings.PESAPAL_QUERY_STATUS_LINK

def set_context(request, context, search=True):
	context['user'] = request.user
	context['search'] = search
	context['categories'] = Category.objects.all()
	context['partners'] = Partner.objects.filter(active=True)
	
def about(request):
	about = About.objects.all()
	
	if about:
		about = about[0]

	context = {
			'about': about,
			'atabout': True,
			"title": "About Us"
		}
	set_context(request, context, False)

	return render(	
		request,
		"home/about.html",
		context
	)

def convert_image(file):
	blob = file.read()
	b64 = base64.b64encode(blob)
	img_str = b64.decode('UTF-8')
	return img_str	

def index(request):
	"""
	returns the: 
	1. recent three events
	"""
	now = timezone.now()

	upcoming = Event.objects.filter(
		status=1, ends_on__gte=now).order_by('starts_on')[:10]
	history = Event.objects.filter(
		status=1, ends_on__lt=now).order_by('-starts_on')[:10]

	context = {
			'title': 'Home',
			'upcoming': upcoming,
			'history': history,
			'athome': True,
		}
	set_context(request, context)
	return render(
		request,
		"home/index.html",
		context
	)	


def categories(request):
	template_name = "home/categories.html"
	context = {
		'title': 'Categories',
		'atcategories': True,
	}
	set_context(request, context)

	return render(request, template_name, context)

# START Filter VIEW
def filter(request):
	template = "home/filter.html"

	month = request.GET.get('month')
	year = int(request.GET.get('year'))
	now = timezone.now()
	c_month = now.month
	
	context = {
		'title': 'Filtered Events for ' + str(year) + '/' +str(month),
	}

	items = []
	if month == 'all':
		items = Event.objects.filter(
			ends_on__year=year, status=1).order_by('-starts_on')
		
	else:
		month = int(month)
		
		if month >= c_month:
			context['atupcoming'] = True
		else:
			context['athistory'] = True
	
		items = Event.objects.filter(
			ends_on__year=year, 
			ends_on__month=month, status=1).order_by('-starts_on')
		
	context['f_year'] = year
	context['f_month'] = month
	paginator = Paginator(items, 20) # Show 20 per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	set_context(request, context)

	return render(request, template, context)
# END Filter VIEW

# START Images VIEWS
def SaveImage(request):
	file = request.FILES['image']
	img_str = convert_image(file)
	image = Image(
		title = request.POST['title'],
		data = img_str,
		group = ImageGroup.objects.get(pk=request.POST['group']),
			description = request.POST['description'],
	)
	image.save()
	return HttpResponseRedirect(reverse("events:image_detail", args=(image.id,)))

def images(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/admin')
	if request.method == "POST":
		return SaveImage(request)
	else:
		groups = ImageGroup.objects.all()
		context = {
				"title": "Images",
				"groups": groups,
				'atimages': True,
			}
		set_context(request, context, False)
		return render(
			request,
			'images/index.html',
			context
		)

def images_group(request, pk):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/admin')
	if request.method == "POST":
		return SaveImage(request)
	else:
		template_name = 'images/images_group.html'
		group = get_object_or_404(ImageGroup, pk=pk)
		images = group.images.all()
		context = {
			'title': "Images in " + group.name,
			'group': group,
			'groups': ImageGroup.objects.all(),
		}

		paginator = Paginator(images, 30) # Show 20 per page.
		page_number = request.GET.get('page')
		page_obj = paginator.get_page(page_number)
		context['page_obj'] = page_obj
		set_context(request, context, False)
		return render(request, template_name, context)

def image_detail(request, image_id):
	if not request.user.is_authenticated:
		return HttpResponseRedirect('/admin')
	old_image = get_object_or_404(Image, pk=image_id)
	groups = ImageGroup.objects.all()
	
	context = {
		'title': 'Image',
		'image': old_image,
		'groups': groups,
		'atimages': True,
	} 
	set_context(request, context, False)

	if request.method == "POST":
		old_image.title = request.POST['title']
		old_image.group = groups.get(pk=request.POST['group'])
		old_image.description = request.POST['description']
		if request.FILES:
			old_image.data = convert_image(request.FILES['image'])
		old_image.save()

		return HttpResponseRedirect(reverse('events:image_detail', args=(old_image.id,)))
	else:
		return render(
			request,
			"images/image_detail.html",
			context
		)
#END Images VIEWS

# START Search VIEW
@csrf_exempt
def search(request):
	section = request.GET.get('s')
	phrase = request.GET.get('q')
	query = SearchQuery(phrase)
	items = []

	context = {
		'title': 'Search Results',
		'query': phrase,
		'section': section
	}
	set_context(request, context, True)

	context['atevents'] = True
	event_vector = SearchVector('title') + SearchVector('content')
	items = Event.objects.annotate(
		search=event_vector).filter(search=query, status=1).order_by('-created_on')

	paginator = Paginator(items, 20) # Show 20 per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	
	return render(request, 'home/search.html', context)
	
#END Search VIEW

# START Subscribe VIEWS
def subscribe(request):
	if request.method == "POST":
		# Check for the subscriber to see if already exists
		subscribers = Subscriber.objects.filter(email=request.POST['email'])
		if subscribers: # some subscribers with the email are found
			subscribers[0].subscribed = True # subscribe the first one
			subscribers[0].save()	# save him/her then redirect
			return HttpResponseRedirect(reverse('events:subscribed', args=(subscribers[0].id,)))
		subscriber = Subscriber(
			first_name = request.POST['first_name'],
			last_name = request.POST['last_name'],
			email = request.POST['email'],
			subscribed = True,
		)

		subscriber.save()
		return HttpResponseRedirect(reverse('events:subscribed', args=(subscriber.id,)))
	else:
		return HttpResponseRedirect(reverse('events:index'))

def subscribed(request, pk):
	subscriber = get_object_or_404(Subscriber, pk=pk)
	context = {
		'title': 'Successfully Subscribed',
		'subscriber': subscriber,
		'subscribed': True,
	}
	set_context(request, context, False)

	return render(request, 'home/subscribed.html', context)

@csrf_exempt
def unsubscribe(request, pk):
	if request.method != 'POST':
		return HttpResponseRedirect(reverse('events:index'))
	subscriber = get_object_or_404(Subscriber, pk=pk)
	c_subscriber = get_object_or_404(Subscriber, pk=int(request.POST['subscriber']))
	c_subscriber.subscribed = False
	c_subscriber.save()
	return HttpResponseRedirect(reverse('events:unsubscribed', args=(subscriber.id,)))

def unsubscribed(request, pk):
	subscriber = get_object_or_404(Subscriber, pk=pk)
	context = {
		'title': 'Successfully Unsubscribed',
		'subscriber': subscriber,
		'subscribed': False,
	}
	set_context(request, context, False)
	return render(request, 'home/subscribed.html', context)

def resubscribe(request, pk):
	if request.method != 'POST':
		return HttpResponseRedirect(reverse('events:index'))
	subscriber = get_object_or_404(Subscriber, pk=pk)
	c_subscriber = get_object_or_404(Subscriber, pk=int(request.POST['subscriber']))
	c_subscriber.subscribed = True
	c_subscriber.save()
	return HttpResponseRedirect(reverse('events:subscribed', args=(subscriber.id,)))

# END Subscribe VIEWS
def upcoming(request):
	template_name = "events/index.html"
	time = timezone.now()
	events = Event.objects.filter(
		status=1, ends_on__gte=time).order_by('-starts_on')
	context = {
		'events': events,
		'title': 'Upcoming Events',
		'atupcoming': True,
	}
	
	paginator = Paginator(events, 20) # Show 20 per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	set_context(request, context)
	return render(request, template_name, context)	

def history(request):
	template_name = "events/index.html"
	time = timezone.now()
	events = Event.objects.filter(
		status=1, ends_on__lt=time).order_by('-starts_on')
	context = {
		'events': events,
		'title': 'Events History',
		'athistory': True,
	}
	
	paginator = Paginator(events, 20) # Show 20 per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	set_context(request, context)
	return render(request, template_name, context)	

def detail(request, slug):
	template_name = "events/detail.html"
	event = get_object_or_404(Event, slug=slug)
	atupcoming = False
	athistory = False
	now = timezone.now()

	if event.ends_on >= now:
		atupcoming = True
	else:
		athistory = True

	context = {
		'event': event,
		'title': event.title,
		'atupcoming': atupcoming,
		'athistory': athistory,
	}
	comments = event.comments.filter(active=True).order_by('created_on')
	
	paginator = Paginator(comments, 15)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	set_context(request, context, False)
	new_comment = None

	if request.method == 'POST':
		
		comment_form = CommentForm(data = request.POST)

		# check if there are some comments with the same details
		# email and textmust be unique for every comment
		comments = Comment.objects.filter(
			body=request.POST['body'],
			email=request.POST['email'])

		if comments: # comments are found, redirect
			return HttpResponseRedirect(reverse('events:detail', args=(event.slug,)))

		if comment_form.is_valid():
			new_comment = comment_form.save(commit=False)
			new_comment.event = event
			new_comment.save()
	else:
		comment_form = CommentForm()
		
	context['new_comment'] = new_comment
	context['form'] = comment_form

	return render(request, template_name, context)

def next(request, days):
	template_name = "events/index.html"
	time = timezone.now() - datetime.timedelta(days=days)
	events = Event.objects.filter(
		created_on__gte=time, created_on__lte=timezone.now(),
		status=1
	).order_by('-created_on')
	context = {
		'title': 'Events Within Next ' + str(days) + ' day(s)',
		'atevents': True,
		'atcategories': True,
	}
	paginator = Paginator(events, 20)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	set_context(request, context)
	
	return render(request, template_name, context)

def category(request, pk):
	template_name = "home/category.html"
	category = get_object_or_404(Category, pk=pk)
	context = {
		'category': category,
		'title': category.name,
		'atevents': True,
		'atcategories': True,
	}
	set_context(request, context)
	events = category.events.filter(status=1).order_by('-created_on')
	
	paginator = Paginator(events, 20) # Show 20 per page.
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	context['page_obj'] = page_obj
	
	return render(request, template_name, context)


def booking(request, pk):
	template = "booking/index.html"
	event = get_object_or_404(Event, pk=pk)

	context = {
		'title': 'Event Booking',
		'atevents': True,
		'event': event,
	}

	set_context(request, context, True)

	return render(request, template, context)


def book(request):
	"""
	Booking Zone
	"""
	
	if request.method == 'POST':
		event_id = request.POST.get('event_id', '')
		event = get_object_or_404(Event, id=event_id)
		amount = int(request.POST.get('amount', 0))

		#client = pesapal.PesaPal(oauth_consumer_key, oauth_consumer_secret, True)
		request_data = {
			'Amount': str(amount),
			'FirstName': request.POST.get('first_name', 'First Name'),
			'LastName': request.POST.get('last_name', 'Last Name'),
			'PhoneNumber': request.POST.get('phone', '+2567000004444'),
			'Description': 'Booking event: %s' % event.title,
			'Reference': str(datetime.datetime.now()),
			'Email': request.POST.get('email', 'mail@example.com'),

		}
		bookings = Booking.objects.filter(
			Email=request_data['Email'], Description=request_data['Description'],
			PhoneNumber=request_data['PhoneNumber'], FirstName=request_data['FirstName'],
			LastName=request_data['LastName'], event=event)

		if bookings:
			booking = bookings[0]
			request_data['Reference'] = booking.Reference			
		else:
			booking = Booking(**request_data)
			booking.event = event
			booking.discount = event.discount
			booking.seats = request.POST.get('seats', 1)

			booking.save()
	
		request_data['Type'] = 'MERCHANT'
		request_data['Currency'] = ''
		request_data['LineItems'] = [
			{
				'UniqueId': str(event.id),
				'Particulars': event.title,
				'Quantity': str(booking.seats),
				'UnitCost': str(event.amount),
				'SubTotal': str(booking.Amount)
			}
		]

		root_xml = etree.Element('PesapalDirectOrderInfo')
		root_xml.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
		root_xml.attrib['xmlns:xsd'] = 'http://www.w3.org/2001/XMLSchema'
		root_xml.attrib['xmlns:xs'] = 'http://www.w3.org/2001/XMLSchema'
		root_xml.attrib['xmlns'] = 'http://www.pesapal.com'

    # populate line items
		line_items = request_data.pop('LineItems')
		if len(line_items) > 0:
			line_items_xml = etree.SubElement(root_xml, 'LineItems')
			for item in line_items:
				item_xml = etree.SubElement(line_items_xml, 'LineItem')
				item_xml.attrib.update(item)

    # populate info
		root_xml.attrib.update(request_data)
		pesapal_request_data = etree.tostring(root_xml)

		# Note, no auth token is present
		params = [
			('oauth_callback', CALLBACK),
			('pesapal_request_data', pesapal_request_data)
		]

		url = "?".join((IFRAME_LINK, urlencode(params)))
		client = oauth1.Client(
			CONSUMER_KEY, CONSUMER_SECRET, 
			signature_type = oauth1.SIGNATURE_TYPE_QUERY)
		uri, header, body = client.sign(url)
		
		#print(uri)
		template = "booking/checkout.html"
		context = {
			'title': 'Booking An Event',
			'amount': amount,
			'event': event,
			'booking': booking,
			'iframe_url': uri
		}

		set_context(request, context, False)
		return render(request, template, context)

	else:
		return HttpResponseRedirect(reverse('events:index'))

def book_status(request):
	"""
	Handle the callback from pesapal
	"""
	tracking_id = request.GET.get('pesapal_transaction_tracking_id', '')
	reference = request.GET.get('pesapal_merchant_reference', '')
	booking = Booking.objects.filter(Reference=reference)[0]
	
	params = None
	if tracking_id and reference:
		params = (
			('pesapal_merchant_reference', reference),
			('pesapal_transaction_tracking_id', tracking_id)
		)
		
	url = "?".join((QUERY_STATUS, urlencode(params)))
	client = oauth1.Client(
		CONSUMER_KEY, CONSUMER_SECRET, 
		signature_type = oauth1.SIGNATURE_TYPE_QUERY)
	uri, header, body = client.sign(url)
	res = requests.get(uri)
	status = res.text.split('=')[1].split(',')[2]
	
	if booking:
		ticket = ''
		if booking.ticket_no:
			ticket = booking.ticket_no
		else:
			for i in range(0, 15):
				ticket += str(random.randint(0, 9))

		booking.tracking_id = tracking_id
		booking.status = status
		booking.ticket_no = ticket
		booking.save()

		if booking.seats_effected == False:
			booking.event.seats -= booking.seats
			booking.event.save()
		booking.seats_effected = True
		booking.save()

	template = 'booking/status.html'
	context = {
		'title': 'Booking Status',
		'booking': booking
	}

	set_context(request, context, False)
	return render(request, template, context)

def booked(request):
	return HttpResponse(request)

def book_fail(request):
	return HttpResponse(request)

# logout
def logout(request):
	return HttpResponseRedirect('/admin/logout')