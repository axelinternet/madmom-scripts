#!/usr/bin/env python
# encoding: utf-8

"""

****************** TODO ******************

[X] 1. Functionality for more onset detectors.

[ ] 2. Save to big-ass file. (Check the not used
bin scripts that have an args.save if-else thingy)

[X] 3. Talk to the man

[ ] (4. Variable parameters)

******************************************

"""

import csv
import argparse
import os

from pprint import pprint
from tqdm import tqdm

from CNNProcessorScript import CNNProcess
from SuperFluxProcessorScipt import SuperFluxProcess
from ComplexFluxProcessorScript import ComplexFluxProcess
from OnsetDetectorProcessorScript import OnsetDetectorProcess
from clips_list import clips

#TODO: Remove later
from small_result import small_result

from madmom.evaluation.onsets import OnsetEvaluation 

SOUND_FOLDER = 'BassDrumsSax_Single/'

def print_single_result(arr,name, filename):
    j = 0
    print('\nResults for {}:\n'.format(filename))
    for i in arr:
        print(name[j] + ': \n', i)
        j += 1
    
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
    elif track == 'DrR':
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
    
def save_results_to_file(results_list):
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
    nr = 0
    foundPath = False
    while not foundPath:
        if not os.path.exists('output/results_{}.csv'.format(nr)):
            with open('output/results_{}.csv'.format(nr), 'w+') as csvfile:
                foundPath = True
                stats_writer = csv.writer(csvfile)
                # Write header row
                stats_writer.writerow(['filename','num_annotations','num_tp','num_fp','num_fn','precision','recall','fmeasure','mean_error','std_error'])
                for result in results_list:
                    stats_writer.writerow([ str(list(result.keys())[0]).strip('.wav'),
                        list(result.values())[0][0]['num_annotations'],
                        list(result.values())[0][0]['num_tp'],
                        list(result.values())[0][0]['num_fp'],
                        list(result.values())[0][0]['num_fn'],
                        list(result.values())[0][0]['precision'],
                        list(result.values())[0][0]['recall'],
                        list(result.values())[0][0]['fmeasure'],
                        list(result.values())[0][0]['mean_error'],
                        list(result.values())[0][0]['std_error'] ])
        else:
            nr +=1;

def detect_notes(processor, filename):
    # Handle array of processors
    if isinstance(processor, list):
        all_processors_results = {}
        for p in processor:
            stats, processor_name = p(filename)
            try:
                all_processors_results[filename.strip("BassDrumsSax_Single")[1:]].append({processor_name: stats})
            except KeyError:
                all_processors_results[filename.strip("BassDrumsSax_Single")[1:]] = [{processor_name: stats}]
        return all_processors_results
    # or just return the result of the processor
    return processor()

def analyze_clip(sound_folder, filename, verbose=False):
    clip_stats = []
    
    # Detect notes using algorithm (the heavy part)
    processed_notes = detect_notes([SuperFluxProcess, CNNProcess, ComplexFluxProcess, OnsetDetectorProcess], sound_folder + filename)
    
    # Load annotaded data
    annotated_notes = read_annotated_data(filename)
    # Evaluate results and add to total stats 
    for processor in processed_notes[filename]:
        evaluation_result = OnsetEvaluation(list(processor.items())[0][1], annotated_notes)
        # Format result
        formated_result = {}
        formated_result['num_annotations'] = evaluation_result.num_annotations
        formated_result['num_tp'] = evaluation_result.num_tp
        formated_result['num_fp'] = evaluation_result.num_fp
        formated_result['num_fn'] = evaluation_result.num_fn
        formated_result['precision'] = evaluation_result.precision
        formated_result['recall'] = evaluation_result.recall
        formated_result['fmeasure'] = evaluation_result.fmeasure
        formated_result['mean_error'] = evaluation_result.mean_error * 1000
        formated_result['std_error'] = evaluation_result.std_error * 1000
        clip_stats.append(formated_result)
    if verbose: 
        print_single_result(clip_stats, ['SuperFluxProcess', 'CNNProcess', 'ComplexFluxProcess', 'OnsetDetectorProcess (RNN)'])
    
    return clip_stats

if __name__ == '__main__':
    total_stats = []
    current_run = []
    for i in clips:
        if 'SaxMic' in i:
            current_run.append(i)

    for clip in tqdm(clips):
       total_stats.append({clip: analyze_clip(SOUND_FOLDER, clip)})
    
    save_results_to_file(total_stats)
