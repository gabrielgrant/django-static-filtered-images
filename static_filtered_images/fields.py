from django.db import models

def _old_src_field_name(name):
	return "_old_image_source_for_%s"%name

class FilteredImageField(models.ImageField):
	def __init__(self, *args, **kwargs): 
		"""
		required kwargs:
		src_field, filter_chain
		"""
		# for South FakeORM compatibility: the frozen version of a
		# FilteredImageField can't try to add an old_src field, because the
		# old_src field itself is frozen as well. See introspection
		# rules below.
		self.add_old_src_field = not kwargs.pop('no_old_src_field', False)
		if not self.add_old_src_field:
			# this doesn't matter, since 
			kwargs['upload_to'] = ''
		else:
			try:
				src_field = kwargs.pop('src_field')
			except KeyError:
				raise TypeError('FilteredImageFields require a "src_field" attribute.')
			try:
				filter_chain = kwargs.pop('filter_chain')
			except KeyError:
				raise TypeError('FilteredImageFields require a "filter_chain" attribute.')
			# check validity of the filter chain 
			for f in filter_chain:
				assert hasattr(f, 'apply_filter')
				assert callable(f.apply_filter)
			self._filter_chain = filter_chain
			self._src_field = src_field
			if not isinstance(src_field, models.ImageField):
				raise ValueError('src_field must be an instance of ImageField')
			kwargs['upload_to'] = src_field.generate_filename
		kwargs['editable'] = False
		return super(FilteredImageField, self).__init__(self, *args, **kwargs)
	
	def contribute_to_class(self, cls, name):
		if self.add_old_src_field:
			upload_to = self._src_field.generate_filename
			old_src_field = models.ImageField(upload_to=upload_to, editable=False)
			cls.add_to_class(_old_src_field_name(name), old_src_field)
		
		# add the field normally
		super(FilteredImageField, self).contribute_to_class(cls, name)
	
	# use this to cascade saves (?)
	#def pre_save(self, model_instance, add):
	#	value = super(FilteredImageField, self).pre_save(model_instance, add)
	#	rendered = render_func(value.raw)
	#	setattr(model_instance, _rendered_field_name(self.attname), rendered)
	#	return value.raw

# allow South to handle FilteredImageField smoothly
# this uses carljm's method of avoiding problems with the extra old_src field
# see http://bitbucket.org/carljm/django-markitup/src/tip/markitup/fields.py#cl-68
rules = [
	(
		[FilteredImageField],
		[],
		{
			#"src_field": ("_src_field", {}),
			#"filter_chain": ("_filter_chain", {}),
			# For a normal FilteredImageField, the add_old_src_field attribute
			# is always True, which means no_rendered_field arg will always be
			# True in a frozen FilteredImageField, which is what we want.
			'no_old_src_field': ('add_old_src_field', {}),
		},
	)
]
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules, ["^static_filtered_images\.fields\.FilteredImageField"])
except ImportError:
    pass

from tempfile import mkstemp
import os.path

from django.core.files import File
	
def run_chain(instance, field):
	src = getattr(instance, field._src_field.get_attname())
	filter_chain = field._filter_chain
	
	# create temp files
	tmp_filenames = [mkstemp()[1] for i in xrange(len(filter_chain))]
	
	zlist = zip(filter_chain, [src.path]+tmp_filenames[:-1], tmp_filenames)
	for filter, src_filename, tmp_dest_filename in zlist:
		filter.apply_filter(instance, src_filename, tmp_dest_filename)
	
	fieldname = field.get_attname()
	dest_basename, dest_ext = os.path.splitext(os.path.basename(src.path))
	dest_name = '%s_%s%s'%(dest_basename, fieldname, dest_ext)
	
	f = open(tmp_dest_filename)
	f = File(f, name=dest_name)
	setattr(instance, fieldname, f)

