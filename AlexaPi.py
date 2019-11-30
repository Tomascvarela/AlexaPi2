import speech_recognition as sr
import pyaudio
from apiclient.discovery import build
import pafy
from pydub import AudioSegment
from pydub.playback import play
from backports import tempfile

mic = sr.Microphone()
p = pyaudio.PyAudio()
DEVELOPER_KEY = "AIzaSyCwMeC0qniQ180KEaxcTcXct_R9hzla8LI"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Words that sphinx should listen closely for. 0-1 is the sensitivity
# of the wake word.
keywords = [("alexa", 1), ("che", 1), ("an exam", 1), ("exile", 1),("and asap", 1), ("ted", 1), ("jay", 1), ("i sat", 1), ]
source = sr.Microphone()
tempSongDir = tempfile.TemporaryDirectory(dir='Songs')


def startUp():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening')
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        command = r.recognize_sphinx(audio, keyword_entries=keywords)

        # Look for your "Ok Google" keyword in speech_as_text
        if "an exam" in command or "exile" or "and asap" or "ted" or "i sat" or "jay" or "alexa" or "che":
            myCommand()
        else:
            startUp()

    except sr.UnknownValueError:
        print('didnt catch that')
        startUp()

def myCommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        playWakeSound()
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        command = command.lower()
        assistant(command)

    except sr.UnknownValueError:
        playErrorSound()
        myCommand()
    playErrorSound()

def playVideo(path):
    sound = AudioSegment.from_file(path)
    play(sound)


def playWakeSound():
    sound = AudioSegment.from_wav('Resources/ful_ui_wakesound.wav')
    play(sound)


def playEndSound():
    sound = AudioSegment.from_wav('Resources/ful_ui_endpointing.wav')
    play(sound)


def playErrorSound():
    sound = AudioSegment.from_wav('Resources/ful_state_privacy_mode_off.wav')
    play(sound)

def playSuccesSound():
    sound = AudioSegment.from_wav('Resources/ful_ui_wakesound_touch.wav')
    play(sound)


def assistant(command):
    if 'play' in command:
        command = command.split()
        command.remove('play')
        text3 = " ".join(command)
        if not command:
            print('nothing to play')
            playErrorSound()
            myCommand()
        else:
            print('playing ' + text3)
            playSuccesSound()
            url = getUrl(text3)
            title = downloadVideo(url)
            playVideo(tempSongDir.name +'/' + title + '.webm')
            # playVideo('Songs/10 second video FAIL.webm')
            playEndSound()



def getUrl(query):
    youtubeGod = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    videos = []
    search = youtubeGod.search().list(q=query, part="snippet", type='video ', maxResults=1).execute()
    results = search.get("items", [])
    for result in results:
        # video result object
        if result['id']['kind'] == "youtube# video":
            videos.append("% s (% s) (% s) (% s)" % (result["snippet"]["title"],
                                                     result["id"]["videoId"], result['snippet']['description'],
                                                     result['snippet']['thumbnails']['default']['url']))
    return result["id"]["videoId"]


def downloadVideo(path):
    url = "https://www.youtube.com/watch?v=" + path
    video = pafy.new(url)
    song = video.getbestaudio()
    filename = song.download(filepath=tempSongDir.name)
    title = video.title
    realTitle = title.replace("/", "_")
    return realTitle

while True:
    startUp()
