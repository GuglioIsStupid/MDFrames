#!/usr/bin/env python

import os, subprocess, random, sys, time, math
import tweepy, dotenv

scriptpath = os.path.dirname(os.path.abspath(__file__))

# load the keys and secrets from the .env file
dotenv.load_dotenv(os.path.join(scriptpath, '.env'))

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')

Client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
    bearer_token=BEARER_TOKEN
)

screenshot = None
time_ = None
start = None
end = None

ClientAuth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(ClientAuth)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")
    sys.exit(1)

video_dir = "videos/"

tmpimg = "tmpimg.jpg"
tmpvid = "tmpvid.mp4"

max_attempts = 10
current_attempts = 0

def getVideo():
    # return a video path
    video = random.choice(os.listdir(video_dir))
    # ignore files that dont end with .mp4
    while not video.endswith(".mp4"):
        video = random.choice(os.listdir(video_dir))
    return scriptpath + "/" + video_dir + video, video.split(".")[0]

def getDuration(video):
    # return the duration of a video
    cmd = [
        "ffprobe",
        "-i", video,
        "-show_entries", "format=duration",
        "-v", "quiet",
        "-of", "csv=%s" % ("p=0")
    ]
    #print(" ".join(cmd))

    """ return float(subprocess.check_output(cmd)) """
    try:
        return float(subprocess.check_output(cmd))
    except Exception as e:
        print("Error: ", e)
        return getDuration(video)

def getRandomScreenshot(video, duration):
    screenshot = random.uniform(0, duration)
    cmd = [
        "ffmpeg",
        "-ss", str(screenshot),
        "-i", video,
        "-vframes", "1",
        "-q:v", "2",
        tmpimg
    ]
    #print(" ".join(cmd))
    subprocess.check_output(cmd)
    return tmpimg, screenshot

def getRandomVideoClip(video, duration, clipLength):
    clipStart = random.uniform(0, duration - clipLength)
    cmd = [
        "ffmpeg",
        "-ss", str(clipStart),
        "-i", video,
        "-t", str(clipLength),
        "-r", "24",
        # mp4 encoding
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "ultrafast",
        "-b:v", "2048k",

        tmpvid
    ]
    #print(" ".join(cmd))
    subprocess.check_output(cmd)
    return tmpvid, clipStart, clipStart + clipLength

timer = 1800.0
# one hour max
maxTimer = 1800.0

while True:
    timer += 1.0
    # should post ss?
    if timer >= maxTimer:
        timer = 0.0
        video, videoName = getVideo()
        duration = getDuration(video)
        #50/50 chance for screenshot or video clip
        while True:
            try:
                screenshot = None
                time_ = None
                start = None
                end = None

                if random.randint(0, 1) == 0:
                    screenshot, time_ = getRandomScreenshot(video, duration)
                else:
                    screenshot, start, end = getRandomVideoClip(video, duration, random.uniform(5.0, 15.0))

                tweetText = f"Murder Drones : {videoName}\n"
                if time_ != None: # Convert the time to minutes:seconds
                    seconds = time_ % (24 * 3600)
                    _ = seconds // 3600
                    seconds %= 3600
                    minutes = seconds // 60
                    seconds %= 60
                    tweetText += f"Frame time: {math.floor(minutes)}:{math.floor(seconds)}"
                else:
                    seconds1 = float(start % (24 * 3600))
                    _ = seconds1 // 3600
                    seconds1 %= 3600
                    minutes1 = seconds1 // 60
                    seconds1 %= 60

                    seconds2 = end % (24 * 3600)
                    _ = seconds2 // 3600
                    seconds2 %= 3600
                    minutes2 = seconds2 // 60
                    seconds2 %= 60

                    tweetText += f"Clip: {math.floor(minutes1)}:{math.floor(seconds1)}-{math.floor(minutes2)}:{math.floor(seconds2)}"
                print(tweetText)
                    
                mediaID = api.media_upload(screenshot)
                Client.create_tweet(
                    text = tweetText,
                    media_ids = [mediaID.media_id]
                )
                break
            except Exception as e:
                print("Error: ", e)
                current_attempts += 1
                print("Attempt: ", current_attempts)
                # delete the screenshot if it exists
                if os.path.exists(screenshot or tmpimg or tmpvid):
                    os.remove(screenshot)
                if current_attempts == max_attempts:
                    print("Max attempts reached. Waiting for next tweet.")
                    break
                continue
        current_attempts = 0

                    
        # delete the screenshot
        """ os.remove(screenshot) """
        if os.path.exists(screenshot):
            os.remove(screenshot)
        

    # sleep for 1 second
    time.sleep(1.0)