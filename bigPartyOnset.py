#!/usr/bin/env python
# encoding: utf-8

"""

****************** TODO ******************

[X] 1. Functionality for more onset detectors.

[X] 2. Variable parameters
       Add them as parameters from this file instead.

[ ] 3. Save to big-ass file.
       Fix the loop marked TODO.
       Add output of what parameters were used to each row. 

[X] 4. Talk to the man


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
ONSET_METHODS = ['SuperFluxProcess', 'CNNProcess', 'ComplexFluxProcess', 'OnsetDetectorProcess (RNN)']
THRESHOLD = 0.8


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
    
def save_results_to_file(results_list, threshold):
    """
    Saves the results for one file using four different onset detectionmethods
    to disk in a csv format.
    """
    nr = 0
    foundPath = False
    while not foundPath:
        if not os.path.exists('output/results_{}.csv'.format(nr)):
            with open('output/results_{}.csv'.format(nr), 'w+') as csvfile:
                foundPath = True
                stats_writer = csv.writer(csvfile, delimiter=',', quotechar='|')
                # Write header row
                stats_writer.writerow(['filename','onset_method', 'num_annotations','num_tp','num_fp','num_fn','precision','recall','fmeasure','mean_error','std_error','threshold'])
                for result in results_list:
                    for i, onset_specific_result in enumerate(list(result.values())[0]):
                        stats_writer.writerow([ str(list(result.keys())[0]).strip('.wav'),
                            ONSET_METHODS[i],
                            float(onset_specific_result['num_annotations']),
                            float(onset_specific_result['num_tp']),
                            float(onset_specific_result['num_fp']),
                            float(onset_specific_result['num_fn']),
                            float(onset_specific_result['precision']),
                            float(onset_specific_result['recall']),
                            float(onset_specific_result['fmeasure']),
                            float(onset_specific_result['mean_error']),
                            float(onset_specific_result['std_error']),
                            float(threshold)])
        else:
            nr +=1;

def detect_notes(processor, filename, threshold):
    """ 
        ##  Detect onsets using one or many processors. 
        
        Every processor takes a number of arguments. See each processor script file to see what
        parameters can be adjusted. Added threshold as a argument to this function so that is easy
        to adjust. More could be added later in the same manner.

    """
    if isinstance(processor, list):
        all_processors_results = {}
        for p in processor:
            stats, processor_name = p(filename, threshold=threshold)
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
    processed_notes = detect_notes([SuperFluxProcess, 
        CNNProcess, 
        ComplexFluxProcess, 
        OnsetDetectorProcess], sound_folder + filename, THRESHOLD)
    
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
        print_single_result(clip_stats, ONSET_METHODS)
    
    return clip_stats

if __name__ == '__main__':
    threshold_range = (0.1, 0.2)

    THRESHOLD = threshold_range[0]
    while THRESHOLD <= threshold_range[1]:
        total_stats = []
        print('Running onset detection with {} as threshold'.format(THRESHOLD))
        for clip in tqdm(clips[0:2]):
           total_stats.append({clip: analyze_clip(SOUND_FOLDER, clip)})
        
        save_results_to_file(total_stats, THRESHOLD)

        THRESHOLD += 0.1
    