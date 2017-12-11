import argparse

from madmom.processors import IOProcessor, io_arguments
from madmom.audio.signal import SignalProcessor, FramedSignalProcessor
from madmom.audio.filters import FilterbankProcessor, LogarithmicFilterbank
from madmom.audio.spectrogram import (LogarithmicSpectrogramProcessor,
                                      SpectrogramDifferenceProcessor)
from madmom.features import ActivationsProcessor
from madmom.features.onsets import (SpectralOnsetProcessor,
                                    OnsetPeakPickingProcessor)


def SuperFluxProcess(filename, threshold=1.1, pre_max=0.01,
                                            post_max=0.05, pre_avg=0.15,
                                            post_avg=0, combine=0.03, delay=0):
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)

    io_arguments(p, output_suffix='.onsets.txt')

    ActivationsProcessor.add_arguments(p)

    SignalProcessor.add_arguments(p, norm=False, gain=0)
    FramedSignalProcessor.add_arguments(p, fps=200)
    FilterbankProcessor.add_arguments(p, num_bands=24, fmin=30, fmax=17000,
                                      norm_filters=False)
    LogarithmicSpectrogramProcessor.add_arguments(p, log=True, mul=1, add=1)
    SpectrogramDifferenceProcessor.add_arguments(p, diff_ratio=0.5,
                                                 diff_max_bins=3,
                                                 positive_diffs=True)
    OnsetPeakPickingProcessor.add_arguments(p, threshold, pre_max,
                                            post_max, pre_avg,
                                            post_avg, combine, delay)

    args= p.parse_args()
    # set immutable defaults
    args.num_channels = 1
    args.onset_method = 'superflux'
    args.filterbank = LogarithmicFilterbank

    spectral_proc = SpectralOnsetProcessor(**vars(args))
    processed_by_spectral = spectral_proc(filename)
    peak_picking_proc = OnsetPeakPickingProcessor(**vars(args))
    detected_notes_array = peak_picking_proc.process_sequence(processed_by_spectral)

    return detected_notes_array, 'SuperFluxProcess'
