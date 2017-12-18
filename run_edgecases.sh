python batch_run.py --instrument DrL --method=SuperFlux
python batch_run.py --instrument DrL --method=ComplexFlux
python batch_run_backwards.py --instrument BassPick --method=CNNOnsetDetector
python batch_run_backwards.py --instrument SuperFlux --method=CNNOnsetDetector
python batch_run_backwards.py --instrument SaxMic --method=CNNOnsetDetector

