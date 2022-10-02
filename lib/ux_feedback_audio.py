import sys
import os

from .audio import AudioFile

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assets_dir = os.path.join(root_dir, 'assets')

def play_thinking(dummy=False):
    print("Play thinking tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "thinking_1.wav"))
        aud.play()
        aud.close()

def play_interact(dummy=False):
    print("Play interact tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "interact_1.wav"))
        aud.play()
        aud.close()

def play_failure(dummy=False):
    print("Play failure tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "failure_1.wav"))
        aud.play()
        aud.close()

def play_success(dummy=False):
    print("Play success tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "success_1.wav"))
        aud.play()
        aud.close()


def play_refusal(dummy=False):
    print("Play refusal tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "hit-hurt_1.wav"))
        aud.play()
        aud.close()


def play_voicemail_beep(dummy=False):
    print("Play voicemail beep tone", file=sys.stderr)
    if not dummy:
        aud = AudioFile(os.path.join(assets_dir, "voicemail-beep.wav"))
        aud.play()
        aud.close()
    