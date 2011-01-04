import os
import subprocess

# define reusable filter chains in filter_chains.py (by convention only)

class BaseFilter(object):
	def apply_filter(self, src_filename, dest_filename):
		raise NotImplementedError('apply_filter() must be over-ridden')
	def run(self, src_filename):
		# create dest file
		
		return dest_filename
		

class ImageMagickFilter(BaseFilter):
	def apply_filter(self, instance, src_filename, dest_filename):
		if not os.path.exists(src_filename):
			raise RuntimeError('source file does not exist')
		args = ['convert', src_filename]
		args.extend(self.get_args(instance))
		args.append(dest_filename)
		subprocess.check_call(args)


#TODO allow choosing location and direction (vertical or horizontal)
class TextWatermarkFilter(ImageMagickFilter):
	def __init__(self, field_name):
		self.field_name = field_name
	def get_args(self, instance):
		watermark = getattr(instance, self.field_name)
		args = ['-gravity', 'southeast',]
		args.extend(['-stroke', "#0009", '-strokewidth', '2',
		             '-pointsize', '11', '-annotate', '0'])
		args.append(watermark)
		args.extend(['-stroke', 'none', '-fill', 'white',
		             '-pointsize', '11', '-annotate', '0'])
		args.append(watermark)
		
		return args
		
		"""-gravity southeast \
    -stroke '#0009' -strokewidth 2 -pointsize 11 -annotate 0 '%(watermark)s' \
    -stroke  none   -fill white  -pointsize 11  -annotate 0 '%(watermark)s'"""%{'watermark':getattr(instance, self.field_name)}

class ResizeFilter(ImageMagickFilter):
	def __init__(self, height=None,  # height_type='<=',
	                   width=None,  # width_type='<='):
	                   style='<=', *args, **kwargs):
		if width is None and height is None:
			raise ValueError('at least one of width or height must be supplied')
		resize_styles = ['<=', '==', '>=']
		if style not in resize_styles:
			raise ValueError("style must be '<=', '==' or '>='")
		if height:
			height = int(height)
		self.height = height
		#self.height_type = height_type
		if width:
			width = int(width)
		self.width = width
		#self.width_type = width_type
		self.style = style
		ImageMagickFilter.__init__(self, *args, **kwargs)
		
	def get_args(self, instance):

		dims = []
		if self.width:
			dims.append('%s'%self.width)
		if self.height:
			dims.append('x%s'%self.height)
		dims = ''.join(dims)
		
		args = ['-resize']
		if self.style == '<=' or not self.height or not self.width:
			args.append(dims)
		else:
			args.append(dims + '^')
			if self.style == '==':
				args.append('-gravity')
				args.append('center')
				args.append('-extent')
				args.append(dims)
		return args

