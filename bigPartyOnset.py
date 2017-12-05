#!/usr/bin/env python
# encoding: utf-8

"""

****************** TODO ******************

1. Functionality for more onset detectors.

2. Save to big-ass file.

3. Talk to the man

(4. Variable parameters)

******************************************

"""
from __future__ import absolute_import, division, print_function

import csv
import argparse

from pprint import pprint
from tqdm import tqdm

from CNNProcessorScript import CNNProcess
from SuperFluxProcessorScipt import SuperFluxProcess
from madmom.evaluation.onsets import OnsetEvaluation 

def print_results(arr):
    for i in arr:
        print(i)
    
def read_annotated_data(filename, print_mode = False):
    """
    Reading csv data and matching rows according to the filename.
    Ignoring right drum track as both left and right corresponds to the same annotaded data.
    """ 
    bassist = filename[1]
    drummer = filename[4]
    phrase = filename[10]
    version = filename[12]
    track = filename[13:-4]
    if track == "BassPick":
        track = "BassTrack"
    elif track == "SaxMic": 
        track = "SaxTrack"
    elif track == "DrL":
        track = 'DrumTrack'
    
    # Print selection
    if print_mode:
        print("## Analyzing ##")
        print("track: ", track)
        print("bassist: ", bassist)
        print("drummer: ", drummer)
        print("phrase: ", phrase)
        print("version: ", version)
    
    with open('jazzData.csv') as csvfile:
        jazz_reader = csv.reader(csvfile)
        annotated_notes = []
        for note in jazz_reader:
            if note[4:-3] == [track, bassist, drummer, phrase, version]:
                #print(note)
                annotated_notes.append(note[1])
    return annotated_notes
    
def save_results_to_file():
    """
    Saves the results for one file using four different onset detectionmethods
    to disk in a csv format.

    These are the things that OnsetEvaluation returns. 
    
    self.num_annotations, self.num_tp, self.num_fp, self.num_fn,
                self.precision, self.recall, self.fmeasure,
                self.mean_error * 1000., self.std_error * 1000.)

    
    A csv structure could look something like this: 
    "annotations", "tp", ...,  
    num_annotations, num_tp, ... , ... 
    num_annotations, num_tp, ... , ... 
    
    """
    pass

def detect_notes(processor):
    # Handle array of processors
    if isinstance(processor, list):
        all_processors_results = {}
        print('Processing audio')
        for p in tqdm(processor):
            stats, filename, processor_name = p()
            try:
                all_processors_results[filename].append({processor_name: stats})
            except KeyError:
                all_processors_results[filename] = [{processor_name: stats}]
        return all_processors_results, filename
    # or just return the result of the processor
    return processor()


if __name__ == '__main__':

    
    total_stats = []
    
    # Detect notes using algorithm (the heavy part)
    processed_notes, loaded_filename = detect_notes([SuperFluxProcess, CNNProcess])
    
    # Load annotaded data
    annotated_notes = read_annotated_data(loaded_filename)

    # Evaluate results and add to total stats
    for processor in processed_notes[loaded_filename]:
        total_stats.append(OnsetEvaluation(list(processor.items())[0][1], annotated_notes))
    
    print_results(total_stats)
    
    
    
    
    