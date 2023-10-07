import os
import shutil
import sys

import cv2
from PIL import Image, ImageDraw, ImageFont
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

###############################################################
f = input("Filepath: ")
color = input("Color (standard #DDDDDD): ")
if color == "":
    color = "#DDDDDD"

folder = "tempFiles"

greyscale = list("QRVILr:'.- ")  # 11 tonal ranges of 24 pixels each
# greyscale = list(" -.':rLIVXRMWQ@") #15 tonal ranges of 18 pixels each
# greyscale = list("@&B9#SGHMh352AXsri;:~,. ") #24 tonal ranges of ~11 pixels each
h, r = 72, 2.5

###############################################################

path = "./%sImages" % f

try:
    os.mkdir(path)
    os.makedirs(folder)
except OSError:
    print("Creation of the directories %s failed" % (path + " and ./" + folder))
else:
    print("Successfully created the directories %s " % (path + " and ./" + folder))

###############################################################

vidcap = cv2.VideoCapture(f)
success, image = vidcap.read()
count = 0
total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

with tqdm(total=total_frames, desc="Extracting Frames") as pbar:
    while success:
        cv2.imwrite(path + "/frame%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vidcap.read()
        count += 1
        pbar.update(1)

def generateAscii(f, h, r, breite, höhe):
    img = Image.open(path + "/" + f)
    img = img.convert("L")  # convert to greyscale

    (x, y) = img.size
    newsize = (int(x / y * h * r), h)  # width is r*height, image aspect-ratio is kept
    img = img.resize(newsize, Image.LANCZOS)

    str = ""
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            lum = 255 - img.getpixel((x, y))
            str += greyscale[(lum // 24)]  # 24 pixels per tonal range
        str += "\n"
    ascii_art_in_jpg_speichern(str, folder + "/" + f, breite, höhe)


def ascii_art_in_jpg_speichern(ascii_art, dateiname, breite, höhe):
    bild = Image.new('RGB', (breite, höhe), color='black')
    zeichner = ImageDraw.Draw(bild)
    schriftart = ImageFont.load_default()
    zeichner.text((0, 0), ascii_art, fill=color, font=schriftart)
    bild.save(dateiname, 'JPEG', quality=95)


def video_info(pfad_zum_video):
    try:
        video = cv2.VideoCapture(pfad_zum_video)
        #breite = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        #höhe = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        framerate = int(video.get(cv2.CAP_PROP_FPS))
        video.release()

        return framerate
    except Exception as e:
        print(f"Error retrieving video information: {str(e)}")
        return None


def bilder_zu_video(input_ordner, ausgabedatei, bildrate):
    try:
        bilder = [bild for bild in os.listdir(input_ordner) if bild.endswith(".jpg")]
        bilder.sort(key=lambda x: int(x.split("frame")[1].split(".jpg")[0]))

        if not bilder:
            print("No JPG images found in the specified folder.")
            return

        erstes_bild = cv2.imread(os.path.join(input_ordner, bilder[0]))
        höhe, breite, _ = erstes_bild.shape

        video = cv2.VideoWriter(ausgabedatei, cv2.VideoWriter_fourcc(*'mp4v'), bildrate, (breite, höhe))

        for bildname in tqdm(bilder, desc="Converting Frames to Video"):
            bildpfad = os.path.join(input_ordner, bildname)
            bild = cv2.imread(bildpfad)
            video.write(bild)

        video.release()
    except Exception as e:
        print(f"Error creating video: {str(e)}")


breite, höhe, bildrate = 1920,1080,video_info(f)

for filename in tqdm(os.listdir(path), desc="Generating ASCII-Frames"):
    if filename.endswith(".jpg"):
        generateAscii(filename, h, r, breite, höhe)
    else:
        continue

bilder_zu_video(folder, f[:-4] + "_ascii.mp4", bildrate)
shutil.rmtree(folder)
shutil.rmtree(f + "Images")

def replace_audio(video1_path, video2_path, output_path):
    class NullOutput:
        def write(self, text):
            pass
    video1 = VideoFileClip(video1_path)
    video2 = VideoFileClip(video2_path)
    video2 = video2.set_audio(video1.audio)

    print("Adding Audio...", end='', flush=True)
    original_stdout = sys.stdout
    sys.stdout = NullOutput()
    video2.write_videofile(output_path, codec='libx264',bitrate="50000k",logger=None)
    sys.stdout = original_stdout
    print("\rAudio added   ")

    os.remove(video2_path)
    os.rename(output_path,video2_path)
    print("Video generated: "+video2_path)

replace_audio(f, f[:-4] + "_ascii.mp4", f[:-4] + "_ascii_audio.mp4")
