import pysepm
import numpy as np
from pesq import pesq
from pystoi import stoi
from typing import Tuple

import voxbench.utils as utils


def compute_pesq(
    pred : np.ndarray,
    target : np.ndarray,
    fs : int,
    mode : str = 'wb'
) -> np.ndarray:
    """ Compute PESQ score

    Arguments
    ---------
    pred : np.ndarray
        Predicted signal of shape [N] or [C, N].

    target : np.ndarray
        Target signal of shape [N] or [C, N].

    fs : int
        Sample frequency in hertz of the signals.

    mode : str, optional
        Either 'wb' for wideband mode or 'nb' for narrowband mode.
        Defaults to 'wb'.

    Returns
    -------
    np.ndarray
        Numpy array containing the PESQ score for each channel.
    """
    # Error handling and formatting
    mode = mode.lower().strip()

    if mode not in ('wb', 'nb'):
        raise ValueError("Mode must either be 'wb' or 'nb'.")

    if len(pred.shape) == 1: pred = pred[None, :]
    if len(target.shape) == 1: target = target[None, :]

    if len(pred.shape) != 2 or len(target.shape) != 2:
        raise ValueError("Signals must have shape [N] or [C, N].")

    if pred.shape[0] != target.shape[0]:
        raise ValueError("Signals must have same number of channels.")

    if pred.shape[1] != target.shape[1]:
        raise ValueError("Signals must be of same length.")

    # Resampling if necessary
    if mode == 'wb' and fs != 16000:
        pred = utils.resample_signal(pred, fs, 16000)
        target = utils.resample_signal(target, fs, 16000)
        fs = 16000

    elif mode == 'nb' and fs not in (8000, 16000):
        pred = utils.resample_signal(pred, fs, 8000)
        target = utils.resample_signal(target, fs, 8000)
        fs = 8000

    # Computation for each channel
    result = np.zeros((pred.shape[0],)).astype(np.float32)

    for c in range(pred.shape[0]):
        result[c] = pesq(fs, target[c, :], pred[c, :], mode)

    return result


def compute_stoi(
    pred : np.ndarray,
    target : np.ndarray,
    fs : int
) -> np.ndarray:
    """ Compute STOI score

    Arguments
    ---------
    pred : np.ndarray
        Predicted signal of shape [N] or [C, N].

    target : np.ndarray
        Target signal of shape [N] or [C, N].

    fs : int
        Sample frequency in hertz of the signals.

    Returns
    -------
    np.ndarray
        Numpy array containing the STOI score for each channel.
    """
    # Error handling and formatting
    if len(pred.shape) == 1: pred = pred[None, :]
    if len(target.shape) == 1: target = target[None, :]

    if len(pred.shape) != 2 or len(target.shape) != 2:
        raise ValueError("Signals must have shape [N] or [C, N].")

    if pred.shape[0] != target.shape[0]:
        raise ValueError("Signals must have same number of channels.")

    if pred.shape[1] != target.shape[1]:
        raise ValueError("Signals must be of same length.")

    # Computation for each channel
    n_channels = pred.shape[0]
    result = np.zeros((n_channels,)).astype(np.float32)

    for c in range(n_channels):
        result[c] = stoi(target[c, :], pred[c, :], fs, extended = False)

    return result


def compute_si_snr(
    pred : np.ndarray,
    target : np.ndarray
) -> np.ndarray:
    """ Computes the SI-SNR. Similar to SI-SDR, but this
    function normalizes the mean before computing the components
    for the ratio.

    Arguments
    ---------
    pred : np.ndarray
        Predicted signal of shape [N] or [C, N].

    target : np.ndarray
        Target signal of shape [N] or [C, N].

    Returns
    -------
    np.ndarray
        Numpy array containing the SI-SNR for each channel.
    """
    if len(pred.shape) == 1: pred = pred[None, :]
    if len(target.shape) == 1: target = target[None, :]

    # Zero mean
    pred = pred - np.mean(pred, axis=-1)[:, None]
    target = target - np.mean(target, axis=-1)[:, None]

    # Target component
    alpha = np.sum(pred * target, axis = -1)
    alpha /= (np.sum(target * target, axis = -1) + 1e-20)

    s_target = alpha[:, None] * target

    # Error component
    e_noise = pred - s_target

    # Compute SNR
    num = np.sum(s_target**2, axis=-1)
    den = np.sum(e_noise**2, axis=-1)

    si_snr = 10. * np.log10(num / (den + 1e-20))

    return si_snr


def compute_si_sdr(
    pred : np.ndarray,
    target : np.ndarray
) -> np.ndarray:
    """ Computes the SI-SDR. Similar to SI-SNR, but this
    function DOESN'T normalize the mean before computing the
    components for the ratio.

    Arguments
    ---------
    pred : np.ndarray
        Predicted signal of shape [N] or [C, N].

    target : np.ndarray
        Target signal of shape [N] or [C, N].

    Returns
    -------
    np.ndarray
        Numpy array containing the SI-SDR for each channel.
    """
    if len(pred.shape) == 1: pred = pred[None, :]
    if len(target.shape) == 1: target = target[None, :]

    # Target component
    alpha = np.sum(pred * target, axis = -1)
    alpha /= (np.sum(target * target, axis = -1) + 1e-20)

    s_target = alpha[:, None] * target

    # Error component
    e_noise = pred - s_target

    # Compute SNR
    num = np.sum(s_target**2, axis=-1)
    den = np.sum(e_noise**2, axis=-1)

    si_sdr = 10. * np.log10(num / (den + 1e-20))

    return si_sdr


def compute_composite(
    pred : np.ndarray,
    target : np.ndarray,
    fs : int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """ Compute composite metrics (CSIG, CBAK and COVL).

    Arguments
    ---------
    pred : np.ndarray
        Predicted signal of shape [N] or [C, N].

    target : np.ndarray
        Target signal of shape [N] or [C, N].

    fs : int
        Sample frequency in hertz of the signals.

    Returns
    -------
    np.ndarray
        Numpy array containing the CSIG score for each channel.

    np.ndarray
        Numpy array containing the CBAK score for each channel.

    np.ndarray
        Numpy array containing the COVL score for each channel.
    """
    # Error handling and formatting
    if len(pred.shape) == 1: pred = pred[None, :]
    if len(target.shape) == 1: target = target[None, :]

    if len(pred.shape) != 2 or len(target.shape) != 2:
        raise ValueError("Signals must have shape [N] or [C, N].")

    if pred.shape[0] != target.shape[0]:
        raise ValueError("Signals must have same number of channels.")

    if pred.shape[1] != target.shape[1]:
        raise ValueError("Signals must be of same length.")

    # Resampling if necessary
    if fs not in (8000, 16000):
        pred = utils.resample_signal(pred, fs, 16000)
        target = utils.resample_signal(target, fs, 16000)
        fs = 16000

    # Compute metrics with pysepm
    n_channels = pred.shape[0]

    csig = np.zeros((n_channels,)).astype(np.float32)
    cbak = np.zeros((n_channels,)).astype(np.float32)
    covl = np.zeros((n_channels,)).astype(np.float32)

    for c in range(n_channels):
        csig[c], cbak[c], covl[c] = pysepm.composite(target[c, :], pred[c, :], fs)

    return csig, cbak, covl


if __name__ == '__main__':
    np.random.seed(42)
    n_channels, fs = 2, 8000

    clean = np.random.randn(n_channels, fs * 3, )
    noisy = clean + 1.2 * np.random.randn(n_channels, fs * 3)

    print(compute_pesq(noisy, clean, fs))
    print(compute_stoi(noisy, clean, fs))
    print(compute_si_snr(noisy, clean))
    print(compute_si_sdr(noisy, clean))
    print(compute_composite(noisy, clean, fs)[0])