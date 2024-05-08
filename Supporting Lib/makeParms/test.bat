set thresh=120
set numCh=32

python test.py "%~1" B %numCh% %thresh%
python test.py "%~1\B_%thresh%"
python test.py "%~1\B_%thresh%"