"""
Copyright 2017 Jiří Janoušek <janousek.jiri@gmail.com>

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


_RECOGNIZED_LICENSES = [
	("BSD-2-Clause", "2-Clause BSD-license", "2-Clause BSD"),
	("MIT", "MIT-license"),
	("CC-BY-4.0",),
	("CC-BY-3.0",),
	("CC-BY-SA-4.0",),
	("CC-BY-SA-3.0",),
]

RECOGNIZED_LICENSES = set(i[0] for i in _RECOGNIZED_LICENSES)
LICENSE_ALIASES = {}


def normalize(license):
	return license.strip().lower().replace(" ", "-").replace("_", "-")


for license, *aliases in _RECOGNIZED_LICENSES:
	LICENSE_ALIASES[normalize(license)] = license
	LICENSE_ALIASES.update({normalize(alias): license for alias in aliases})


def get_canonical(license, *, ignore_unknown=False):
	license = license.strip()
	if license in RECOGNIZED_LICENSES:
		return license
	else:
		try:
			return LICENSE_ALIASES[normalize(license)]
		except KeyError as e:
			if ignore_unknown:
				return license.replace(" ", "-")
			else:
				raise ValueError(license) from e


def check_canonical(license_expr):
	for entry in split_licenses(license_expr):
		try:
			canonical = get_canonical(entry)
		except ValueError as e:
			raise ValueError(e.args[0], None) from e
		if entry != canonical:
			raise ValueError(entry, canonical)


def split_licenses(license_expr):
	for entry in license_expr.replace(",", ";").split(";"):
		entry = entry.strip()
		if entry:
			yield entry

	
def get_spdx_expression(licenses, *, ignore_unknown=False):
	return " AND ".join([get_canonical(entry, ignore_unknown=ignore_unknown) for entry in split_licenses(licenses)])
			
			
