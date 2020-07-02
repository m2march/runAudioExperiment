import pydub
import numpy as np

DEFAULT_SR = 48000

def extend_stimulus(stimulus_path, duration):
    '''
    Creates a copy of the stimulus with added silence onto a temporary file.

    Args:
        * stimulus_path: path of the audio file used as stimulus
        * duration: milliseconds added as silence to the stimulus

    Returns:
        path to the temporary file
    '''
    sti_segment = pydub.AudioSegment.from_file(stimulus_path)
    silence_segment = pydub.AudioSegment.silent(
        duration=duration, frame_rate=sti_segment.frame_rate
    )
    with tempfile.NamedTemporaryFile() as f:
        wavfile.write(f.name, sr, a)
        seg = AudioSegment.from_file(f.name)
    return seg


def create_separator_sound(dur, f=354.0,
                           noise_sigma=0.1, sr=48000, channels=2,
                           volume=0.1, fn=None):
    '''
    Creates a tone of frequency _f_ with gaussian noise of _dur_ ms.

    Returns a (sr * dur, channels) numpy array
    '''
    fd = (volume * np.sin(2 * np.pi *
                np.arange(int(sr * dur / 1000.0)) * f/sr)).astype(np.float32)

    if noise_sigma and noise_sigma != 0.0:
        noise = np.random.normal(0, volume * noise_sigma, fd.size)
        fd = fd + noise

    fd = (np.zeros((channels, 1)) + fd).astype(np.float32)

    return fd.T


def create_separator_sound_data(dur):
    if dur == 0:
        return None

    data = create_separator_sound(dur, sr=DEFAULT_SR)
    return AudioData(data, DEFAULT_SR)


def extend_stimulus_w_silence(stimulus_path, dur):
    seg = pydub.AudioSegment.from_file(stimulus_path)
    silence = pydub.AudioSegment.silent(dur, seg.frame_rate)
    joined = seg + silence
    data = np.array(joined.get_array_of_samples()).reshape((-1, seg.channels))
    return AudioData(data, seg.frame_rate)


class AudioData:
    '''
    Represents preloaded audio data. 
    
    Stores samples (self.data) and frame rate (self.sr) to be used 
    for playback.
    '''

    def __init__(self, data, sr):
        self.data = data
        self.sr = sr
