import sys
import os
from typing import Dict

from .audio import AudioFile

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
assets_dir = os.path.join(root_dir, 'assets')

SOUND_CACHE: Dict[str, AudioFile] = {}

def _cache(filename):
    SOUND_CACHE[filename] = AudioFile(os.path.join(assets_dir, filename))

def _play(filename):
    SOUND_CACHE[filename].play()


def cache_sounds():
    print("Loading sounds...", file=sys.stderr)
    _cache("thinking_1.wav")
    _cache("interact_1.wav")
    _cache("failure_1.wav")
    _cache("success_1.wav")
    _cache("hit-hurt_1.wav")
    _cache("voicemail-beep.wav")
    

def play_thinking(dummy=False):
    print("Play thinking tone", file=sys.stderr)
    if not dummy:
        _play("thinking_1.wav")

def play_interact(dummy=False):
    print("Play interact tone", file=sys.stderr)
    if not dummy:
        _play("interact_1.wav")

def play_failure(dummy=False):
    print("Play failure tone", file=sys.stderr)
    if not dummy:
        _play("failure_1.wav")

def play_success(dummy=False):
    print("Play success tone", file=sys.stderr)
    if not dummy:
        _play("success_1.wav")


def play_refusal(dummy=False):
    print("Play refusal tone", file=sys.stderr)
    if not dummy:
        _play("hit-hurt_1.wav")


def play_voicemail_beep(dummy=False):
    print("Play voicemail beep tone", file=sys.stderr)
    if not dummy:
        _play("voicemail-beep.wav")
    
