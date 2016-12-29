"""
Copyright 2016 Jiří Janoušek <janousek.jiri@gmail.com>

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

from xml.etree import ElementTree


def indent_tree(elm, indent="  ", level=0):
    i = "\n" + level * indent
    if len(elm):
        if not elm.text or not elm.text.strip():
            elm.text = i + indent
        if not elm.tail or not elm.tail.strip():
            elm.tail = i
        for subelm in elm:
            indent_tree(subelm, indent, level + 1)
        if not subelm.tail or not subelm.tail.strip():
            subelm.tail = i
    else:
        if level and (not elm.tail or not elm.tail.strip()):
            elm.tail = i
    return elm
    i = "\n" + level * indent
    j = "\n" + (level - 1) * indent
    if len(elm):
        if not elm.text or not elm.text.strip():
            elm.text = i + indent
        if not elm.tail or not elm.tail.strip():
            elm.tail = i
        for subelm in elm:
            indent_tree(subelm, indent, level + 1)
        if not elm.tail or not elm.tail.strip():
            elm.tail = j
    else:
        if level and (not elm.tail or not elm.tail.strip()):
            elm.tail = j
    return elm

        
class TreeBuilder(ElementTree.TreeBuilder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__root = None
        
    def __call__(self, _tag, _attrs=None, **kwargs):
        assert _attrs is None or isinstance(_attrs, dict)
        if kwargs:
            if _attrs:
                _attrs.update(kwargs)
            else:
                _attrs = kwargs
        elm = self.start(_tag, _attrs)
        if  self.__root is None:
            self.__root = elm
        return TreeBuilder.Cursor(self, _tag, elm)
    
    def add(self, _tag, _data=None, _attrs=None, **kwargs):
        assert _attrs is None or isinstance(_attrs, dict)
        if isinstance(_data, dict):
            _data = None
            _attrs = data
        if kwargs:
            if _attrs:
                _attrs.update(kwargs)
            else:
                _attrs = kwargs
        elm = self.start(_tag, _attrs)
        if _data is not None:
            self.data(_data)
        self.end(_tag)
        return elm
    
    def __str__(self):
        if self.__root is None:
            return ""
        return ElementTree.tostring(self.__root, encoding="unicode", method="xml")
    
    def close(self, pretty=0):
        elm = super().close()
        if elm and pretty:
            elm = indent_tree(elm, pretty * " ")
        return elm
    
    def dump(self, pretty=4, xml_declaration=True):
        elm = self.close(pretty=pretty)
        if elm:
            xml = ElementTree.tostring(elm, encoding="unicode", method="xml")
            if xml_declaration:
                xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml
            return xml
        return ""
    
    class Cursor:
        def __init__(self, builder, tag, elm):
            self.builder = builder
            self.tag = tag
            self.elm = elm
        
        def __enter__(self):
            return self.elm
        
        def __exit__(self, type, value, traceback):
            self.builder.end(self.tag)
