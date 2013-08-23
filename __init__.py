import threading

from django.db.models import Model, Count
from django.db.models.query import QuerySet

from . import html

##########################################


def _serialize(model):
	return dict(
		(f.name, getattr(model, f.name)) for f in model.__class__._meta._fields()
	)


##########################################

def aggregate_count(qs, field):
	return qs.annotate(count=Count(field))['count']

def annotate_count(qs, field):
	for item in qs.annotate(count=Count(field)).iterator():
		yield item.count

def each(qs, func, threaded=False, daemon=False, *extraargs, **extrakwargs):
	'''
	Calls `func` against all elements within `qs`
	Threading optional
	'''
	def run(*a, **kw):
		for item in qs.iterator():
			func(qs, *a, **kw)

	if threaded:
		thread = threading.Thread(target=func, args=extraargs, kwargs=extrakwargs)
		thread.daemon = daemon
		thread.start()
	else:
		run(*extraargs, **extrakwargs)

def get(qs, latest_field='id', **kwargs):
	'''
	Tries to get a single item from the QuerySet
	If more than one are found, the latest by `latest` is fetched
	'''
	try:
		return qs.get(**kwargs)
	except Model.DoesNotExist:
		return qs.filter(**kwargs).latest(latest_field)

def is_evaluated(qs):
	'''
	Determines whether a QuerySet has been un-lazied yet
	'''
	return bool(getattr(qs, '_result_cache'))

def map(qs, func, *extraargs, **extrakwargs):
	'''
	Returns the result of `func` against all elements within `qs`
	'''
	for item in qs.iterator():
		yield func(qs, *extraargs, **extrakwargs)

def pluck(qs, attr, unique=True):
	'''
	Returns attribute `attr` from each item of the QuerySet
	'''
	return_cls = set if unique else list
	return return_cls(qs.values_list(attr, flat=True))

def product(one, two):
	'''
	Returns the iterable product of two QuerySets
	'''
	for a in one.iterator():
		for b in two.iterator():
			yield a, b

def reduce(qs, func, initializer=None):
	'''
	Reduces a QuerySet
	'''
	return reduce(func, qs.iterator(), initializer=initializer)

def serialize(qs_or_model):
	'''
	Attempts to intelligently build a dictionary for each item
	in a QuerySet, or a Model itself
	'''
	if isinstance(qs_or_model, Model):
		return _serialize(qs_or_model)
	elif isinstance(qs_or_model, QuerySet):
		return qs_or_model.values().iterator()

	raise Exception('Need a Model or QuerySet')

def update_or_create(model, defaults=None, **kwargs):
	defaults = defaults or {}

	item, created = models.objects.get_or_create(defaults=defaults, **kwargs)

	if not created and defaults:
		for key, value in kwargs.iteritems():
			setattr(item, key, value)
		item.save()

	return item, created

