import argparse

from madmom.processors import IOProcessor, io_arguments
from madmom.audio.signal import SignalProcessor
from madmom.features import ActivationsProcessor
from madmom.features.onsets import RNNOnsetProcessor, OnsetPeakPickingProcessor


def OnsetDetectorProcess(filename, threshold=0.35, smooth=0.07):
    """OnsetDetector using RNN"""

    # define parser
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)

    io_arguments(p, output_suffix='.onsets.txt')
    ActivationsProcessor.add_arguments(p)

    # signal processing arguments
    SignalProcessor.add_arguments(p, norm=False, gain=0)
    # peak picking arguments
    OnsetPeakPickingProcessor.add_arguments(p, threshold, smooth)

    # parse arguments
    args = p.parse_args()

    # set immutable defaults
    args.fps = 100
    args.pre_max = 1. / args.fps
    args.post_max = 1. / args.fps

    # use a RNN to predict the onsets
    rnn_onsets_proc = RNNOnsetProcessor(**vars(args))
    processed_by_rnn = rnn_onsets_proc(filename)

    # perform peak picking on the onset activations
    peak_picking_proc = OnsetPeakPickingProcessor(**vars(args))

    detected_notes_array = peak_picking_proc.process_sequence(processed_by_rnn)

    return detected_notes_array, 'SuperFluxProcess'

