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

from nuvolasdk.shkit import *

def set_up_git():
	try:
		git_name = getstdout("git config user.name").strip()
	except ExecError:
		git_name = None
	if not git_name:
		while not git_name:
			git_name = input('Type your name for git version control system, e.g. "John Doe". Or press Ctrl-C to abort.\n').strip()
		run('git config --global user.name  %s' % shquote(git_name))
	
	try:
		git_email = getstdout("git config user.email").strip()
	except ExecError:
		git_email = None
	if not git_email:
		while not git_email:
			git_email = input('Type your email for git version control system, e.g. "john@doe.com". Or press Ctrl-C to abort.\n').strip()
		run('git config --global user.email  %s' % shquote(git_email))
	
	return git_name, git_email
