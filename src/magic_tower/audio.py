import os
import pygame
import logging

log = logging.getLogger(__name__)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

SFX_NAMES = {
    1: "select",
    2: "cancel",
    4: "walk",
    7: "pickup",
    8: "map_transition",
    10: "battle_hit",
    12: "cutscene",
}

BGM_TRACKS = {
    (0, 0): "A_027XGW.MID",
    (1, 0): "A_027XGW.MID",
    (2, 0): "A_026XGW.MID",
    (3, 0): "A_028XGW.MID",
    (4, 0): "A_023XGW.MID",
    (0, 1): "A_005XGW.MID",
    (1, 1): "A_007XGW.MID",
    (2, 1): "A_008XGW.MID",
    (3, 1): "A_019XGW.MID",
    (4, 1): "A_023XGW.MID",
}

BGM_BY_AREA = {
    0: "A_027XGW.MID",
    1: "A_026XGW.MID",
    2: "A_028XGW.MID",
    3: "A_019XGW.MID",
    4: "A_023XGW.MID",
}


class AudioSystem:
    def __init__(self):
        self.enabled = True
        self.bgm_enabled = True
        self.sfx_volume = 0.5
        self.bgm_volume = 0.3
        self._sfx_cache = {}
        self._current_bgm = None
        self._initialized = False

    def init(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._initialized = True
            self._load_sfx()
        except Exception as e:
            log.warning(f"Audio init failed: {e}")
            self.enabled = False

    def _load_sfx(self):
        wav_dir = os.path.join(ASSETS_DIR, "wav")
        if os.path.exists(wav_dir):
            wav_map = {
                "pickup": "GET.WAV",
                "walk": "OPEN.WAV",
                "battle_hit": "TAISEN.WAV",
                "map_transition": "kai2.wav",
                "cutscene": "ZENO.WAV",
            }
            for name, filename in wav_map.items():
                path = os.path.join(wav_dir, filename)
                if os.path.exists(path):
                    try:
                        self._sfx_cache[name] = pygame.mixer.Sound(path)
                        self._sfx_cache[name].set_volume(self.sfx_volume)
                    except Exception as e:
                        log.warning(f"Failed to load {path}: {e}")

    def play_sfx(self, sfx_id):
        if not self.enabled or not self._initialized:
            return

        name = SFX_NAMES.get(sfx_id)
        if name and name in self._sfx_cache:
            self._sfx_cache[name].play()

    def play_bgm_for_floor(self, floor):
        if not self.bgm_enabled or not self._initialized:
            return

        area = min((floor - 1) // 10, 4) if floor > 0 else 0
        midi_file = BGM_BY_AREA.get(area)
        if midi_file:
            self.play_midi(midi_file)

    def play_midi(self, filename):
        if not self.bgm_enabled or not self._initialized:
            return

        if filename == self._current_bgm:
            return

        self.stop_bgm()

        path = os.path.join(ASSETS_DIR, "midi", filename)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play(-1)
                self._current_bgm = filename
            except Exception as e:
                log.warning(f"Failed to play MIDI {filename}: {e}")

    def stop_bgm(self):
        if self._initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self._current_bgm = None

    def set_sfx_enabled(self, enabled):
        self.enabled = enabled

    def set_bgm_enabled(self, enabled):
        self.bgm_enabled = enabled
        if not enabled:
            self.stop_bgm()

    def toggle_sfx(self):
        self.set_sfx_enabled(not self.enabled)

    def toggle_bgm(self):
        self.set_bgm_enabled(not self.bgm_enabled)
