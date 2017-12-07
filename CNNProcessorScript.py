from madmom.processors import IOProcessor, io_arguments
from madmom.audio.signal import SignalProcessor
from madmom.features import ActivationsProcessor
from madmom.features.onsets import CNNOnsetProcessor, OnsetPeakPickingProcessor
import argparse
"""
Detected default arguments
Namespace(combine=0.03, delay=0.0, fps=100, 
    func=<function process_single at 0x7f9793c9c950>, 
    gain=0, infile=<_io.BufferedReader name='/home/axel/Python/madmom/sounds/BassDrumsSax_Single/B1Dr1S2phr1v2BassPick.wav'>, 
    load=False, 
    norm=False, 
    num_threads=4, 
    outfile=<_io.BufferedWriter name='<stdout>'>, 
    post_max=0.01, 
    pre_max=0.01, 
    save=False, 
    sep=None, 
    smooth=0.05, 
    threshold=0.54, 
    verbose=None)
"""
    
def CNNProcess(filename):
    # define parser
    p = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    # input/output options
    io_arguments(p, output_suffix='.onsets.txt')
    ActivationsProcessor.add_arguments(p)
    # signal processing arguments
    SignalProcessor.add_arguments(p, norm=False, gain=0)
    # peak picking arguments
    OnsetPeakPickingProcessor.add_arguments(p, threshold=0.54, smooth=0.05)

    # parse arguments
    args = p.parse_args()
    
    # set immutable defaults
    args.fps = 100
    args.pre_max = 1. / args.fps
    args.post_max = 1. / args.fps
    
    # use a CNN to predict the onsets
    CNNProc = CNNOnsetProcessor(**vars(args))
    processed_by_CNN = CNNProc(filename)
    peak_picker_proc = OnsetPeakPickingProcessor(**vars(args))
    detected_notes_array = peak_picker_proc.process_sequence(processed_by_CNN)
    return detected_notes_array, 'CNNProcess'
    