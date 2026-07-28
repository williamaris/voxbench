import numpy as np
from pick import pick
from typing import Tuple
from scipy.io import wavfile
from fractions import Fraction
from scipy.signal import resample_poly


def load_audio(path : str) -> Tuple[np.ndarray, int]:
    """ Load audio from a wav file

    Arguments
    ---------
    path : str
        Path to the input file.

    Returns
    -------
    np.ndarray
        Audio signal in a numpy array of shape [C, N].

    int
        Sample rate in hertz of the signal.
    """
    fs, xs = wavfile.read(path)

    if np.issubdtype(xs.dtype, np.integer):
        info = np.iinfo(xs.dtype)
        xs = xs.astype(np.float32) / max(abs(info.min), info.max)

    else:
        xs = xs.astype(np.float32)

    if len(xs.shape) == 1:
        xs = xs[:, None]

    return xs.T, fs


def resample_signal(xs : np.ndarray, fs_in : int, fs_out : int) -> np.ndarray:
    """ Resample a signal using scipy.signal.resample_poly()

    Arguments
    ---------
    xs : np.ndarray
        Input signal in a numpy array.

    fs_in : int
        Current sample rate in hertz.

    fs_out : int
        Target sample rate in hertz.

    Returns
    -------
    np.ndarray
        Resampled signal.
    """
    if fs_in == fs_out:
        return xs

    ratio = Fraction(fs_out, fs_in).limit_denominator()

    return resample_poly(
        xs,
        up = ratio.numerator,
        down = ratio.denominator,
        axis = -1
    )


def selection_prompt(prompt, options, default = 0):
    option, index = pick(options, prompt, indicator="=>", default_index = default)
    return option, index