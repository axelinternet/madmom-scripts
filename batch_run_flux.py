import subprocess
import argparse
from tqdm import tqdm
from clips_list import clips

"""

    This is a quick testrun that better utilizes the pre-built
    sample scripts that run different methods. We should probably have built
    something like this from the beginning if we would have figured out what
    arguments where available.

"""

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

""" NEW FUNKY SCRIPTS """

PATH = "BassDrumsSax_Single/"

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

args = parser.parse_args()

if not args.ignore:
    batch_result = []

    if args.test: 
        clips = clips[:args.test]

    for clip in tqdm(clips):
        proc_result = subprocess.run(["python",  "env/bin/{}".format(args.method), "single", "{}{}".format(PATH, clip)],
            stdout=subprocess.PIPE)

        clean_result = proc_result.stdout.decode("utf-8").split("\n")
        for i, result in enumerate(clean_result):
            try:
                clean_result[i] = float(result)
            except ValueError:
                clean_result.pop(i)

        batch_result.append({
                clip: clean_result
            })

    if args.verbose:
        print(batch_result)