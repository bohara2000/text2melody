#!/bin/sh

# NOTE - if you get the following error:
# SIOD ERROR: wrong type of argument to get_c_val
# then see http://linuxsagas.digitaleagle.net/2013/09/15/synthesizing-an-accapella-song-with-festival-speech-synthesis/
# for a workaround

counter=0
for f in `ls output-?.xml`
do
   voice="(voice_us1_mbrola)" 
   if  [ `expr $counter % 2` -eq 0 ] 
   then
      voice="(voice_rab_diphone)"
   fi
   /usr/bin/text2wave -mode singing "$f" -o "$f".wav -eval "$voice"
   counter=$((counter+1))
done

current_time=$(date "+%Y.%m.%d-%H.%M.%S")

ch_wave -o result-full.$current_time.wav -pc longest output-?.xml.wav
