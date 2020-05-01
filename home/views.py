import base64
import datetime

from django.utils import timezone
from django.views import generic
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.core.paginator import (Paginator, PageNotAnInteger, EmptyPage)
from django.contrib.auth.models import Group, User

from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.utils import timezone
from django.contrib.postgres.search import SearchQuery, SearchVector

from .models import Image, ImageGroup, Category, Subscriber, About, Partner, Event
from .forms import CommentForm


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

from django_pesapal.views import PaymentRequestMixin

class PaymentView(PaymentRequestMixin):

  def get_pesapal_payment_iframe(self):
    '''
    Authenticates with pesapal to get the payment iframe src
    '''
    order_info = {
      'first_name': self.request.POST['first_name'],
      'last_name': self.request.POST['last_name'],
  	  'amount': self.request.POST['amout'],
      'description': self.request.POST['description'],
      'reference': self.request.POST['event'],  # some object id
      'email': self.request.POST['email'],
    }

    iframe_src_url = self.get_payment_url(**order_info)
    return iframe_src_url

def booking(request, pk):
	template = "events/booking.html"
	event = get_object_or_404(Event, pk=pk)

	context = {
		'title': 'Event Booking',
		'atevents': True,
		'event': event,
	}

	set_context(request, context, True)

	return render(request, template, context)

def book(request):
	return HttpResponse(request)

def booked(request):
	return HttpResponse(request)

def book_fail(request):
	return HttpResponse(request)

# logout
def logout(request):
	return HttpResponseRedirect('/admin/logout')