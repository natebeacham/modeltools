import threading

from django.db.models import Model, Count
from django.db.models.query import QuerySet

from . import html, utils

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

def cycle(qs):
	'''
	Alias for `loop`
	'''
	return loop(qs)

def dropwhile(func, qs):
	'''
	Drops elements from the left that match `func`
	then returns a slice
	'''
	index = 0

	for item in qs.iterator():
		if func(item):
			index += 1
			continue
		break

	return qs[index:]

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

def garnish(qs, name, func):
	'''
	Applies `func` against each element in a QuerySet and sets it as `name` on the
	element.
	'''
	for item in qs.iterator():
		setattr(item, key, func(item))
		yield item

def get(qs, latest_field='id', **kwargs):
	'''
	Tries to get a single item from the QuerySet
	If more than one are found, the latest by `latest` is fetched
	'''
	try:
		return qs.get(**kwargs)
	except Model.DoesNotExist:
		return qs.filter(**kwargs).latest(latest_field)

def groupby(qs, field):
	for value in pluck(qs, field):
		yield value, qs.filter(**{field: value}).iterator()

def is_evaluated(qs):
	'''
	Determines whether a QuerySet has been un-lazied yet
	'''
	return bool(getattr(qs, '_result_cache'))

def juice(qs, *fields):
	if len(fields) == 0:
		fields = [f.name for f in qs.model._meta.fields]

	return utils.JuicedDict(qs, *fields)

def loop(qs):
	'''
	Returns an infinitely looping iterable of the QuerySet
	'''
	return utils.LoopIter(qs)

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

def season(qs, **attrs):
	'''
	Adds the properties defined in `attrs` to each element in the QuerySet.
	If a property is a callable, it will be applied against the element.
	'''
	for item in qs.iterator():
		for key, value in attrs.items():
			if callable(value):
				setattr(item, key, value(item))
				continue
			setattr(item, key, value)
		yield item

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

def supplement(qs, replace_value=None, **attrs):
	'''
	Replaces attributes defined in `attrs` with the given values
	if their value is that of `replace_value`
	'''
	for item in qs.iterator():
		for key, value in attrs.items():
			if getattr(item, key, replace_value) == replace_value:
				if callable(value):
					setattr(item, key, value(item))
					continue
				setattr(item, key, value)
		yield item

def takewhile(func, qs):
	'''
	Takes elements from the left that match `func`
	then returns a slice
	'''
	index = 0

	for item in qs.iterator():
		if func(item):
			index += 1
			continue
		break

	return qs[:index]

def update_or_create(model, defaults=None, **kwargs):
	'''
	Gets or creates an element with `kwargs` and `defaults`. If a new
	element is created, updates it with values of `defaults`
	'''
	defaults = defaults or {}

	item, created = models.objects.get_or_create(defaults=defaults, **kwargs)

	if not created and defaults:
		for key, value in kwargs.iteritems():
			setattr(item, key, value)
		item.save()

	return item, created

def values(qs, attr, unique=True):
	'''
	Alias for `pluck`
	'''
	return pluck(qs, attr, unique=unique)
