from django import template
from django.utils.functional import lazy

from . import templates

def table(qs):
	fields = [f.name for f in qs.model._meta.fields]
	headers = [f.title for f in fields]

	def format(qs):
		for item in qs:
			yield [getattr(item, f) for f in fields]

	return template.Template(templates.TABLE)\
		.render(template.Context({
			'qs': format(qs),
			'headers': headers,
		}))

def dl(qs, term, definition):
	def format(qs):
		for item in qs:
			yield getattr(item, term), getattr(item, definition)

	return template.Template(templates.DL)\
		.render(template.Context({
			'qs': format(qs),
		}))