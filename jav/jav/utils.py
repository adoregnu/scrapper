import os
import xml.etree.ElementTree as ET

XML_TEMPLATE = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><movie></movie>'

def adjust_actor(name):
    from .actor_map import ACTOR_MAP
    if ACTOR_MAP.get(name):
        return ACTOR_MAP[name]
    else:
        return name

def indent_xml(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def xml2dict(elem):
    if len(elem) == 0:
        return elem.text

    data = {}
    for child in elem:
        if not data.get(child.tag):
            if xml2dict(child): data[child.tag] = xml2dict(child)
        elif not isinstance(data[child.tag], list):
            tmp = data[child.tag]
            data[child.tag] = [tmp]
            if xml2dict(child): data[child.tag].append(xml2dict(child))
        else:
            if xml2dict(child): data[child.tag].append(xml2dict(child))
    return data

def nfo2dict(file):
    tree = ET.parse(file)
    return xml2dict(tree.getroot())

def dict2xml(droot, root, path=None):
    skip = ['path', 'poster', 'fanart']
    for key, val in droot.items():
        if key in skip: continue
        if isinstance(val, list):
            for it in val:
                if isinstance(it, dict):
                    dict2xml(it, ET.SubElement(root, key), path)
                else:
                    ET.SubElement(root, key).text = str(it)
        elif isinstance(val, dict):
            dict2xml(val, ET.SubElement(root, key), path)
        else: #isinstance(val, str):
            ET.SubElement(root, key).text = str(val)

def dict2nfo(dic, file):
    from xml.etree.ElementTree import fromstring
    root = fromstring(XML_TEMPLATE)
    dict2xml(dic, root, os.path.dirname(file))
    indent_xml(root)
    ET.ElementTree(root).write(file)

from PIL import Image
class AvImage:
    _image = None
    _stored = True
    def __init__(self, url, image=None):
        self.url = url
        if image:
            self._image = image
            self._stored = False
            return

        import requests
        from io import BytesIO
        try:
            if url.startswith('http'):
                blob = requests.get(url, timeout=10).content
                self._image = Image.open(BytesIO(blob))
                self._stored = False
            else:
                self._image = Image.open(url)
        except:
            #self.blob = None
            self._image = None

    def __str__(self):
        return self.url

    def ext(self):
        return self.url.split('.')[-1]

    def image(self):
        return self._image

    def rotate(self, degree = Image.ROTATE_90):
        return AvImage(self.url, self._image.transpose(degree))

    def cropLeft(self, ratio=0.474):
        w, h = self._image.size
        return AvImage(self.url, self._image.crop((w - int(w*ratio), 0, w, h)))

    def save(self, path):
        if not self._image or self._stored: return
        self._image.save(path)