:: The term %0 refers to this bat file name. 
:: "~" gets rid of quotes.
:: The "p" is for path name.
:: The n for file name only (with no extention or path).
:: SET _base_file=%~n0 can be used instead and is safer if gauranteed to be run locally.
SET _python_arguments=
SET _base_file=%~p0%~n0
SET _python_file="%_base_file%.py"
SET _profile_file="%_base_file%.prof"
python -m cProfile -o %_profile_file% %_python_file% %_python_arguments%
snakeviz %_profile_file%
pause