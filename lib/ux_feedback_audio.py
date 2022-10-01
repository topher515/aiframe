import sys
import os

from .audio import AudioFile

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assets_dir = os.path.join(root_dir, 'assets')

def play_thinking():
    print("Play thinking tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "thinking_1.wav"))
    aud.play()
    aud.close()

def play_interact():
    print("Play interact tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "interact_1.wav"))
    aud.play()
    aud.close()

def play_failure():
    print("Play failure tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "failure_1.wav"))
    aud.play()
    aud.close()

def play_success():
    print("Play success tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "success_1.wav"))
    aud.play()
    aud.close()


def play_refusal():
    print("Play refusal tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "hit-hurt_1.wav"))
    aud.play()
    aud.close()


def play_voicemail_beep():
    print("Play voicemail beep tone", file=sys.stderr)
    aud = AudioFile(os.path.join(assets_dir, "voicemail-beep.wav"))
    aud.play()
    aud.close()
    