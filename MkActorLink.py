import sys

from pathlib import Path
from xml.etree.ElementTree import parse, ElementTree, SubElement, dump

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):

            elem.tail = i

def MakeLinkEachProduct(root, nfoPath):
    actors = root.findall('actor')
    actorRoot = r'e:\ByActor'

    if len(actors) == 0:
        print('no actors:', nfoPath)

    for actor in actors:
        name = actor.find('name')
#        print('{}:{}'.format(nfoPath, name.text))
#        actorPath = r'{}\{}'.format(actorRoot, name.text)
        actorPath = r'{}\{}\{}'.format(
                actorRoot, name.text.upper()[0], name.text)
        try:
            Path(actorPath).mkdir(parents=True, exist_ok=True)

            linkPath = r'{}\{}'.format(actorPath, nfoPath.split('\\')[-2])
            targetPath = '\\'.join(nfoPath.split('\\')[:-1])
            Path(linkPath).symlink_to(targetPath, target_is_directory=True)
            print('{} -> {}'.format(linkPath, targetPath))
        except Exception as e:
            if 'WinError 183' not in str(e):
                print(e)

def ProcessActorName(tree, nfoPath, argv):
    root = tree.getroot()
    id = root.find('id')
    actors = root.findall('actor')
    for actor in actors:
        name = actor.find('name')
        if name.text != argv[1]:
            continue
        name.text = argv[2] 
        if argv[0] == 'chname':
            try:
                role = actor.find('role')
                role.text = argv[1]
            except:
                role = SubElement(actor, 'role')
                role.text = argv[1]
        elif argv[0] == 'adname':
            role = SubElement(actor, 'role')
            role.text = argv[1]
        elif argv[0] == 'rename':
            pass

        print('{} : {} -> {}'.format(id.text, argv[1], argv[2]))
        indent(root)
        tree.write(nfoPath, encoding='UTF-8', xml_declaration=True)

def IterateEachDrive(javd, argv):
    pathObj = Path(javd)
    for path in pathObj.glob(r'**/*.nfo'):
        try:
            tree = parse(path)
            if len(argv) < 1 or argv[0] == 'mklink':
                MakeLinkEachProduct(tree.getroot(), str(path))
            elif argv[0] == 'chname' or argv[0] == 'adname' or \
                 argv[0] == 'rename':
                ProcessActorName(tree, path, argv)
        except Exception as e:
            print(path, e)


JavDrives = [
    r'd:\JAV',
    r'e:\JAV',
    r'f:\JAV',
    r'g:\JAV',
    r'h:\JAV'
]

# ActorLink.py chname OLD_NAME NEW_NAME
# ActorLink.py rename OLD_NAME NEW_NAME
# ActorLink.py adname NAME NEW_NAME
print(JavDrives)
sys.argv.pop(0)
print(sys.argv)
for drive in JavDrives:
    IterateEachDrive(drive, sys.argv)
