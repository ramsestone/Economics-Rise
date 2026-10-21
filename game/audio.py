# ============================================================
#  AUDIO MANAGER – Efectos de sonido y música chiptune 8-bit
# ============================================================
import os
import math
import struct
import pygame

# Frecuencias para notas musicales (Escala estándar)
NOTE_FREQS = {
    'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 'B3': 246.94,
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
    'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 'A5': 880.00, 'B5': 987.77,
    'C6': 1046.50, 'R': 0
}

SAMPLE_RATE = 22050


def _synth_tone(freq, ms, vol=0.15, duty=0.5, decay=True):
    """Sintetiza una onda cuadrada retro de 8-bits."""
    n_samples = int(SAMPLE_RATE * (ms / 1000.0))
    if freq <= 0:
        return pygame.mixer.Sound(buffer=bytes(b'\x00\x00' * n_samples))
    period = SAMPLE_RATE / freq
    buf = bytearray()
    for i in range(n_samples):
        factor = (1.0 - (i / n_samples) * 0.75) if decay else 1.0
        sample = 1.0 if (i % period) < (period * duty) else -1.0
        val = int(sample * 32767 * vol * factor)
        buf.extend(struct.pack('<h', val))
    return pygame.mixer.Sound(buffer=bytes(buf))


def _synth_multitone(tones, vol=0.15, duty=0.25):
    """Concatena tonos para crear arpegios o fanfarrias."""
    buf = bytearray()
    for freq, ms in tones:
        n_samples = int(SAMPLE_RATE * (ms / 1000.0))
        if freq <= 0:
            buf.extend(b'\x00\x00' * n_samples)
            continue
        period = SAMPLE_RATE / freq
        for i in range(n_samples):
            factor = max(0.1, 1.0 - (i / n_samples) * 0.7)
            sample = 1.0 if (i % period) < (period * duty) else -1.0
            val = int(sample * 32767 * vol * factor)
            buf.extend(struct.pack('<h', val))
    return pygame.mixer.Sound(buffer=bytes(buf))


class AudioManager:
    def __init__(self):
        self.muted = False
        self.initialized = False
        self.bg_music_channel = None
        self.procedural_music = None
        self.custom_music_playing = False
        self.sounds = {}
        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(8)
            self.bg_music_channel = pygame.mixer.Channel(0)
            self._create_procedural_sounds()
            self._create_procedural_music()
            self.initialized = True
        except Exception as e:
            print(f"[Audio] No se pudo inicializar mixer: {e}")
            self.initialized = False

    def _create_procedural_sounds(self):
        """Genera efectos de sonido retro auténticos estilo NES/GameBoy."""
        try:
            # 1. Clic estándar
            self.sounds["click"] = _synth_tone(750, 35, vol=0.18, duty=0.5)
            # 2. Deslizador / Slider tick
            self.sounds["slider"] = _synth_tone(900, 16, vol=0.08, duty=0.25)
            # 3. Éxito / Ganancia / Logro (Fanfarria ascendente)
            self.sounds["success"] = _synth_multitone([
                (NOTE_FREQS['C5'], 50),
                (NOTE_FREQS['E5'], 50),
                (NOTE_FREQS['G5'], 70),
                (NOTE_FREQS['C6'], 140)
            ], vol=0.18, duty=0.5)
            # 4. Alerta / Advertencia / Pérdida (Buzzer bajo)
            self.sounds["warning"] = _synth_multitone([
                (180, 80),
                (140, 120)
            ], vol=0.18, duty=0.75)
            # 5. Guía / Modal abrir
            self.sounds["guide"] = _synth_multitone([
                (NOTE_FREQS['D5'], 45),
                (NOTE_FREQS['A5'], 90)
            ], vol=0.15, duty=0.25)
            # 6. Toggle pantalla completa o menú
            self.sounds["toggle"] = _synth_tone(540, 50, vol=0.15, duty=0.5)
        except Exception as e:
            print(f"[Audio] Error creando sonidos procedimentales: {e}")

    def _create_procedural_music(self):
        """Genera una melodía chiptune alegre y nostálgica en bucle infinito."""
        try:
            # Progresión armónica clásica (I - V - vi - IV): C - G - Am - F
            melody = [
                # Compás 1: C major
                (NOTE_FREQS['C4'], 140), (NOTE_FREQS['E4'], 140), (NOTE_FREQS['G4'], 140), (NOTE_FREQS['C5'], 140),
                (NOTE_FREQS['G4'], 140), (NOTE_FREQS['E4'], 140), (NOTE_FREQS['G4'], 140), (NOTE_FREQS['E4'], 140),
                # Compás 2: G major
                (NOTE_FREQS['B3'], 140), (NOTE_FREQS['D4'], 140), (NOTE_FREQS['G4'], 140), (NOTE_FREQS['B4'], 140),
                (NOTE_FREQS['D4'], 140), (NOTE_FREQS['G4'], 140), (NOTE_FREQS['D4'], 140), (NOTE_FREQS['G4'], 140),
                # Compás 3: A minor
                (NOTE_FREQS['A3'], 140), (NOTE_FREQS['C4'], 140), (NOTE_FREQS['E4'], 140), (NOTE_FREQS['A4'], 140),
                (NOTE_FREQS['C4'], 140), (NOTE_FREQS['E4'], 140), (NOTE_FREQS['C4'], 140), (NOTE_FREQS['E4'], 140),
                # Compás 4: F major
                (NOTE_FREQS['F3'], 140), (NOTE_FREQS['A3'], 140), (NOTE_FREQS['C4'], 140), (NOTE_FREQS['F4'], 140),
                (NOTE_FREQS['A3'], 140), (NOTE_FREQS['C4'], 140), (NOTE_FREQS['A3'], 140), (NOTE_FREQS['C4'], 140),
            ]
            self.procedural_music = _synth_multitone(melody, vol=0.06, duty=0.25)
        except Exception as e:
            print(f"[Audio] Error creando música procedimental: {e}")

    def start_music(self):
        """Inicia música de fondo (archivo personalizado o procedimental)."""
        if not self.initialized:
            return

        # Buscar si el usuario colocó algún archivo de audio en assets/audio/ o directorio raíz
        music_file = self._find_custom_music()
        if music_file:
            try:
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0 if self.muted else 0.4)
                pygame.mixer.music.play(-1)
                self.custom_music_playing = True
                print(f"[Audio] Reproduciendo música personalizada: {music_file}")
                return
            except Exception as e:
                print(f"[Audio] Error al cargar archivo de música {music_file}: {e}")

        # Si no hay archivo externo, reproducir chiptune procedimental
        if self.procedural_music and self.bg_music_channel:
            self.bg_music_channel.set_volume(0 if self.muted else 0.5)
            self.bg_music_channel.play(self.procedural_music, loops=-1)
            self.custom_music_playing = False

    def _find_custom_music(self):
        """Busca archivos .mp3, .ogg o .wav en assets/audio o carpeta de juego (compatible con PyInstaller)."""
        import sys
        base_dirs = [os.getcwd()]
        if hasattr(sys, "_MEIPASS"):
            base_dirs.insert(0, getattr(sys, "_MEIPASS"))
        search_dirs = []
        for b in base_dirs:
            search_dirs.extend([
                os.path.join(b, "assets", "audio"),
                os.path.join(b, "assets"),
                os.path.join(b, "sounds"),
                b
            ])
        valid_exts = (".mp3", ".ogg", ".wav")
        for d in search_dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.lower().endswith(valid_exts):
                        return os.path.join(d, f)
        return None

    def play(self, sound_name):
        """Reproduce un efecto de sonido por nombre."""
        if not self.initialized or self.muted:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            snd.play()

    def toggle_mute(self):
        """Alterna silencio on/off."""
        self.muted = not self.muted
        if not self.initialized:
            return self.muted

        if self.custom_music_playing:
            pygame.mixer.music.set_volume(0 if self.muted else 0.4)
        elif self.bg_music_channel:
            self.bg_music_channel.set_volume(0 if self.muted else 0.5)

        for snd in self.sounds.values():
            snd.set_volume(0 if self.muted else 1.0)

        return self.muted


# Instancia global accesible desde cualquier archivo
audio = AudioManager()
