set thresh=45
set numCh=32

goto :startsingle

:startloop

for /D %%G in ("%~1\*") DO ( 
python applyFullLCAR.py "%~1\%%~nxG"
python makePolytrodeSpikes_singleChannel.py "%~1\%%~nxG" A %numCh% %thresh%
python expandCSCFile.py "%~1\%%~nxG\A_%thresh%"
python makeParms.py "%~1\%%~nxG\A_%thresh%"
del "%~1\%%~nxG\A_%thresh%\expandedCSC_A.npy"
python makePolytrodeSpikes_singleChannel.py "%~1\%%~nxG" B %numCh% %thresh%
python expandCSCFile.py "%~1\%%~nxG\B_%thresh%"
python makeParms.py "%~1\%%~nxG\B_%thresh%"
del "%~1\%%~nxG\B_%thresh%\expandedCSC_B.npy"
)

goto :end


:startsingle

python applyFullLCAR.py "%~1"
python makePolytrodeSpikes_singleChannel.py "%~1" A %numCh% %thresh%
python expandCSCFile.py "%~1\A_%thresh%"
python makeParms.py "%~1\A_%thresh%"

del "%~1\A_%thresh%\*.npy"
del "%~1\A_%thresh%\*.npz"
del "%~1\A_%thresh%\*.memmap"

python makePolytrodeSpikes_singleChannel.py "%~1" B %numCh% %thresh%
python expandCSCFile.py "%~1\B_%thresh%"
python makeParms.py "%~1\B_%thresh%"

del "%~1\B_%thresh%\*.npy"
del "%~1\B_%thresh%\*.npz"
del "%~1\B_%thresh%\*.memmap"


goto :end



:startdel




rem del "%~1\B_%thresh%\expandedCSC_B.npy"

goto :end

:end