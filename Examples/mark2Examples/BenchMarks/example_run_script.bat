:: The term %0 refers to this bat file name. 
:: "~" gets rid of quotes.
:: The "p" is for path name.
:: The n for file name only (with no extention or path).
:: SET _base_file=%~n0 can be used instead and is safer if gauranteed to be run locally.
SET _base_file=randomised_schreier_sims_stress_test_pre_caching
SET _profile_file="%_base_file%.prof"
snakeviz %_profile_file%
pause