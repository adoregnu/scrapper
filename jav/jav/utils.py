
XML_TEMPLATE = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?><movie></movie>'
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
            data[child.tag] = xml2dict(child)
        elif not isinstance(data[child.tag], list):
            tmp = data[child.tag]
            data[child.tag] = [tmp]
            data[child.tag].append(xml2dict(child))
        else:
            data[child.tag].append(xml2dict(child))
    return data

def dict2xml(droot, root):
    import xml.etree.ElementTree as ET
    for key, val in droot.items():
        if isinstance(val, str):
            ET.SubElement(root, key).text = val
        if isinstance(val, list):
            for it in val:
                if isinstance(it, dict):
                    dict2xml(it, ET.SubElement(root, key))
                else:
                    ET.SubElement(root, key).text = it 
        if isinstance(val, dict):
            dict2xml(val, ET.SubElement(root, key))


