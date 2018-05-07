"""
Copyright 2018 Jiří Janoušek <janousek.jiri@gmail.com>

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

try:
	from PIL import Image
except ImportError as e:
	Image = e

def combine_images(outer, inner, bounds, fill=None):
	if isinstance(Image, ImportError):
		raise Image
	if not isinstance(outer, Image.Image):
		outer = Image.open(outer)
	if not isinstance(inner, Image.Image):
		inner = Image.open(inner)
	if isinstance(bounds, str):
		bounds = tuple(int(i) for i in bounds.replace('+', ',').split(','))
	result = Image.new('RGB', outer.size, fill)
	x, y, width, height = bounds
	x_offset = int((width - inner.size[0]) / 2)
	y_offset = int((height - inner.size[1]) / 2)
	result.paste(inner, (x + x_offset, y + y_offset), inner if inner.mode == 'RGBA' else None)
	result.paste(outer, (0, 0), outer if outer.mode == 'RGBA' else None)
	return result
