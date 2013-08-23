class LoopIter(object):
	def __init__(self, queryset):
		self.__queryset = queryset
		self.__iterator = queryset.iterator()

	def __iter__(self):
		return self

	def next(self):
		try:
			return self.__iterator.next()
		except StopIteration:
			self.__iterator = self.__queryset.iterator()
			return self.__iterator.next()

class JuicedDict(object):
	def __init__(self, qs, *fields):
		self.__qs = qs
		self.__fields = fields

	def __iter__(self):
		for field in self.__fields:
			yield field

	def __getitem__(self, key):
		if key not in self.__fields:
			raise KeyError, key

		from . import pluck

		return pluck(self.__qs, key, unique=False)

	def __setitem__(self, *args):
		raise NotImplementedError
	
	def __delitem__(self, *args):
		raise NotImplementedError

	def items(self):
		for field in self.__fields:
			yield field, self[field]

	def keys(self):
		return list(self.__fields)

	def values(self):
		for field in self.__fields:
			yield self[field]
