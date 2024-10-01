import soundfile as sf
import os
import subprocess
import datetime
from PIL import Image, ImageDraw
import shutil
import time
import tkinter
from tkinter import filedialog
from tkinter import colorchooser

def clamp_amp(x):
    if (x < -2):
        return -2
    if (x > 2):
        return 2
    return x

rootdirectory = os.path.dirname(os.path.realpath(__file__))

ampstrength = 40
centerx = 1748//2
centery = int(1080*0.8) # center of the little waves, mind you
breadth = 1748//4

root = tkinter.Tk()
root.withdraw()

filename = filedialog.askopenfilename(title="Select a song", filetypes=[("Audio files", "*.flac *.wav")])
filenameimage = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.png *.jpg")])
background = colorchooser.askcolor(title="Choose background color")[0]
fg1 = colorchooser.askcolor(title="Choose foreground color 1")[0]
fg2 = colorchooser.askcolor(title="Choose foreground color 2")[0]
saveplace = filedialog.asksaveasfile(defaultextension='.mp4', filetypes = [("Video files", "*.mp4")]).name
if (not saveplace.endswith(".mp4")):
    saveplace += ".mp4"

print("Preparing stuff")
def docolor(dif): #interpolate between fg1 and fg2 using max-min
    w2 = dif*0.25
    w1 = 1-dif*0.25
    return (int(fg1[0]*w1+fg2[0]*w2), int(fg1[1]*w1+fg2[1]*w2), int(fg1[2]*w1+fg2[2]*w2))

data, samplerate = sf.read(filename)
data = [clamp_amp(data[i][0] + data[i][1]) for i in range(len(data))]

framerate = 60
samplesperframe = samplerate/framerate

if samplesperframe % 1 != 0:
    print("Cannot do it")
    raise SystemError
samplesperframe = int(samplesperframe)
samplesperframewindow = int(samplerate * 6) # show this many seconds in every frame
framesneeded = len(data)//samplesperframe

if os.path.exists(rootdirectory + "/frames"):
    shutil.rmtree(rootdirectory + "/frames")
os.mkdir(rootdirectory + "/frames")

# stuff for the photo
photo = Image.open(filenameimage)
old_width, old_height = photo.size
old_width, old_height = int(old_width/old_height*540), 540
photo = photo.resize((old_width, old_height))
x1 = int(((1748 - old_width) // 2))
y1 = int(((1080 - old_height) // 2) - 100)
x2 = x1 + old_width
y2 = y1 + old_height

replace_box = (centerx-breadth, centery-ampstrength*2.5, centerx+breadth, centery+ampstrength*2.5)

starttime = time.time()

minbuckets = [None for i in range(breadth*2+1)]
maxbuckets = [None for i in range(breadth*2+1)]
samplesperbucket = samplesperframewindow / (breadth*2+1)
lastsampleconsidered = 0
lastsampleconsideredgoal = 0

lastpercentagereported = None
im = Image.new('RGB', (1748, 1080), background)
draw = ImageDraw.Draw(im) 
im.paste(photo, (x1, y1, x2, y2))
for framenumber in range(framesneeded):
    draw.rectangle(replace_box, fill=background, outline=None)
    # remove stuff from buckets, add back to
    lastsampleconsideredgoal += samplesperframe
    while (lastsampleconsidered < lastsampleconsideredgoal):
        # consider data[lastsampleconsidered] to data[lastsampleconsidered+samplesperbucket]
        domain = data[int(lastsampleconsidered):int(lastsampleconsidered+samplesperbucket+1)]
        del minbuckets[0]
        del maxbuckets[0]
        minbuckets.append(min(domain))
        maxbuckets.append(max(domain))
        lastsampleconsidered += samplesperbucket
    # draw the buckets
    for x in range(0, breadth*2+1):
        if (minbuckets[x] == None):
            continue
        draw.line((
            centerx - breadth + x,
            centery + ampstrength * minbuckets[x],
            centerx - breadth + x,
            centery + ampstrength * maxbuckets[x]
        ), fill=docolor(maxbuckets[x]-minbuckets[x]))
    im.save(rootdirectory + "/frames/f"+str(framenumber).zfill(8)+".bmp")
    percentage = 20*framenumber//framesneeded
    if lastpercentagereported != percentage:
        lastpercentagereported = percentage
        timetakensofar = time.time()-starttime
        approximatetimeleft = int(timetakensofar / framenumber * framesneeded - timetakensofar) if framenumber>0 else 0
        print(str(5*percentage)+"%" + ", "+str(datetime.timedelta(seconds=approximatetimeleft))+" left")

subprocess.run('ffmpeg -y -r '+str(framerate)+' -s 1748x1080 -i "frames/f%08d.bmp" -vcodec libx264 -crf 18 -pix_fmt yuv420p noaudio.mp4', cwd = rootdirectory)
subprocess.run('ffmpeg -y -i "'+rootdirectory+'/noaudio.mp4" -i "'+filename+'" -c:v copy -b:a 192k "'+saveplace+'"')
os.remove(rootdirectory + "/noaudio.mp4")
shutil.rmtree(rootdirectory + "/frames")