import subprocess
import argparse
import csv
import os

from tqdm import tqdm
from clips_list import clips
from mixdown_list import mixdown_clips
from madmom.evaluation.onsets import OnsetEvaluation 

"""

    This is a quick testrun that better utilizes the pre-built
    sample scripts that run different methods. We should probably have built
    something like this from the beginning if we would have figured out what
    arguments where available.

"""

def save_results_to_file(results_list, threshold):
    """
    Saves the results for one file using four different onset detectionmethods
    to disk in a csv format.
    """
    nr = 0
    foundPath = False
    while not foundPath:
        if args.instrument:
            path_string = 'output/results_{}_{}_{}.csv'.format(args.method, nr, args.instrument)
            correct_path = os.path.exists(path_string)
        else: 
            path_string = 'output/results_{}_{}.csv'.format(args.method, nr)
            correct_path = os.path.exists(path_string)
        if not correct_path:
            with open(path_string, 'w+') as csvfile:
                foundPath = True
                stats_writer = csv.writer(csvfile, delimiter=',', quotechar='|')

                # Write header row
                stats_writer.writerow(['filename','onset_method', 'num_annotations','num_tp','num_fp','num_fn','precision','recall','fmeasure','mean_error','std_error','threshold'])
                for result in results_list:
                    for i, onset_specific_result in enumerate(list(result.values())[0]):
                        stats_writer.writerow([ str(list(result.keys())[0]).strip('.wav'),
                            args.method,
                            float(onset_specific_result['num_annotations']),
                            float(onset_specific_result['num_tp']),
                            float(onset_specific_result['num_fp']),
                            float(onset_specific_result['num_fn']),
                            float(onset_specific_result['precision']),
                            float(onset_specific_result['recall']),
                            float(onset_specific_result['fmeasure']),
                            float(onset_specific_result['mean_error']),
                            float(onset_specific_result['std_error']),
                            float(threshold) ])
        else:
            nr +=1;

def read_annotated_data(filename):
    """
        Reading csv data and matching rows according to the filename.
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
    
    with open('jazzData.csv') as csvfile:
        jazz_reader = csv.reader(csvfile)
        annotated_notes = []
        for note in jazz_reader:
            if note[4:-3] == [track, bassist, drummer, phrase, version]:
                #print(note)
                annotated_notes.append(note[1])
    return annotated_notes

def analyze_clip(filename, processed_notes, i):
    clip_stats = []
   
    if i:
        if i == 0:
            filename = filename[:-4] + "BassPick.wav"
        elif i == 1:
            filename = filename[:-4] + "SaxMic.wav"
        elif i == 2:
            filename = filename[:-4] + "DrL.wav"
        elif i == 3:
            filename = filename[:-4] + "DrR.wav"
    # Load annotaded data
    annotated_notes = read_annotated_data(filename)
    # Evaluate results and add to total stats 
    evaluation_result = OnsetEvaluation(processed_notes, annotated_notes)
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
    
    return clip_stats

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find some onsets in some jazz')
    parser.add_argument('--method', dest='method', type=str,
                        help='What sort of flux would you like?',
                        default="ComplexFlux")
    parser.add_argument('--test', dest='test', type=int,
                        help='How many clips would you like to test?',
                        default=False)
    parser.add_argument('--save', dest='save', type=bool,
                        help='Save results to file, True/False',
                        default=False)
    parser.add_argument('--verbose', dest='verbose', type=bool,
                        help='Print results, True/False',
                        default=False)
    parser.add_argument('--ignore', dest='ignore', type=bool,
                        help='Do nothing',
                        default=False)
    parser.add_argument('--mixdown', dest='mixdown', type=bool,
                        help='Analyze full mix instead of individual tracks. Put mix in Mixdown/ folder',
                        default=False)
    parser.add_argument('--instrument', dest='instrument', type=str,
                        help='Analyze only this instrument tracks',
                        default=False)

    args = parser.parse_args()
    if args.mixdown:
        PATH = "Mixdown/"
    else:
        PATH = "BassDrumsSax_Single/"
    batch_result = []

    if args.test: 
        clips = clips[0:0+args.test]
    if args.mixdown:
        clips = mixdown_clips
    threshold = 0.1

    if args.instrument:
        instrument_clips = []
        for i, clip in enumerate(clips):
            if args.instrument in clip:
                instrument_clips.append(clip)
        
        clips = instrument_clips


    for q in tqdm(range(10)):
        for clip in tqdm(clips):
            proc_result = subprocess.run(["python",  "env/bin/{}".format(args.method), "-t", str(threshold), "single", "{}{}".format(PATH, clip)],
                stdout=subprocess.PIPE)

            clean_result = proc_result.stdout.decode("utf-8").split("\n")
            for i, result in enumerate(clean_result):
                try:
                    clean_result[i] = float(result)
                except ValueError:
                    clean_result.pop(i)

            if args.mixdown:
                for i in range(4):
                    batch_result.append({
                        clip:
                        analyze_clip(clip, clean_result, i)
                    })
            else:
                batch_result.append({
                    clip:
                    analyze_clip(clip, clean_result, i = False)
                })
            
        save_results_to_file(batch_result, threshold)
        batch_result = []
        threshold = threshold - 0.01
