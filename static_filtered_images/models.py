
from django.db.models.signals import post_save
from django.contrib import contenttypes

from static_filtered_images.fields import FilteredImageField
from static_filtered_images.fields import _old_src_field_name
from static_filtered_images.fields import run_chain

def register_filtered_image_fields(sender, **kwargs):
	fields = sender._meta.fields
	fields = [f for f in fields if isinstance(f, FilteredImageField)]
	if not fields:
		return
	def handler(sender, instance, **kwargs):
		for f in fields:
			old_src_field_name = _old_src_field_name(f.get_attname())
			old_src = getattr(instance, old_src_field_name)
			cur_src = getattr(instance, f._src_field.get_attname())
			if old_src == cur_src:
				return
			else:
				run_chain(instance, f)
				setattr(instance, old_src_field_name, cur_src)
				instance.save()
	post_save.connect(handler, sender=sender, weak=False)

for ct in contenttypes.models.ContentType.objects.all():
	register_filtered_image_fields(ct.model_class())

