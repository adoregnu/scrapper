import os, re, sys
import subprocess
from datetime import datetime

ffmpeg = 'd:\\utils\\ffmpeg.exe'
ffprobe = 'd:\\utils\\ffprobe.exe'

print(sys.argv)
if len(sys.argv) != 3:
    print('usage: {} SRC_FILE DST_DIR'.format(sys.argv[0]))
    sys.stdin.read(1)
    sys.exit(0)


avfile = sys.argv[1]
#avfile = 'z:\\Downloads\\msfh-004\\msfh-004.mp4'
target = sys.argv[2]
#target = 'd:\\tmp\\msfh-004.mp4'

if not os.path.exists(avfile):
    print(avfile + ': file not found!')
    sys.exit(-1)

if not os.path.exists(target):
    print(target + ': target path doesn\'t exists!')
    sys.exit(-1)

target = target + os.path.basename(avfile)

print(avfile, target)
#sys.stdin.read(1)
#sys.exit(0)
out = subprocess.check_output([ffprobe, avfile], shell=True,
    stderr=subprocess.STDOUT, encoding='utf-8')

#print(out)
prog = re.compile(r'Duration: ([0-9:]+)')
res = prog.search(out).group(1)
#print(res)
time2cut = datetime.strptime('1:23:11', '%H:%M:%S')
playTime = datetime.strptime(res, '%H:%M:%S')
#print(playTime - time2cut)
if time2cut >= playTime:
    print('too short file')
    sys.exit(-1)

relPlayTime = str(playTime - time2cut)
#print(relPlayTime)
cut = '{} -i {} -to {} -vcodec copy -acodec copy {}'.format(
    ffmpeg, avfile, relPlayTime, target)

#print(cut)
subprocess.run([ffmpeg, '-i', avfile, '-to', relPlayTime,
    '-vcodec', 'copy', '-acodec', 'copy', target], shell=True)
