# misc_scripts
miscellaneous scripts, mainly for research, memorandum or etc.

## regex_test1.py
CIDs in an Adobe OpenType feature file are converted to specified CIDs.

## regex_test2.py
class definitions and CIDs inside them in an Adobe OpenType feature file are detected and shown.  
But currently only very simple descriptions are supported.

## miniufo.sh
extract a subset of UFO file.

## extract_features.rb
extract 'include' statements in a n Adobe OpenType feature file.

## uncompyle_all.rb
uncompile all *.pyc under specified directory by using [uncompyle2](https://github.com/wibiti/uncompyle2).

## randObjectId.rb
generate object IDs for .xib files.

## provide_unicodes.py
provide unicodes to glyphs which has no unicodes according to AGLFN.

## smoothing.py
restore 'smooth' attributes of UFO which are lost during conversion by 'tx'.

## cmap_reader.py
read a CMap file (e.g. UniJIS2004-UTF32-H) and construct dicts which map unicodes to CIDs and CIDs to unicodes.

## check_fonts_unicodes.py
check glyph's unicodes according to specified CMap.

## rename_ufo_by_Glyphs.py
rename a UFO's glyphs names where the UFO is exported by Glyphs.