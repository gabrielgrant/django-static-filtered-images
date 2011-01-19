
from django.db.models.signals import post_save
from django.db.models import get_models

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

for m in get_models():
	register_filtered_image_fields(m)

