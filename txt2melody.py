import os, random
# get the nltk modules
from nltk import pos_tag
from nltk.tokenize import word_tokenize, sent_tokenize
# get the cmu pronunciation dictionary
import pronouncing as pr
# get the modules for creating XML
from lxml import etree
# get mobules to build sequences of notes
from mingus.core import progressions, intervals
from mingus.core import chords as ch
from mingus.containers import Note
import mingus.core.scales as scales
import festival
import re
import time
import subprocess

#progression = ["I", "vi", "ii", "iii7", "I7", "viidom7", "iii7", "V7"]
#progression = ["Im", "bIIIm", "IVm", "Im"]
#progression = ["IIm7", "IIm7", "IIm7", "IIm7", "Vm7", "IVm7", "IIm7", "IIm7", "VIM", "VIM", "IIm7", "IIm7"]
#progression = ["I5", "bII5", "bV5", "V5"]
progression = ["I13", "IV11", "III7", "Idom7","IVdom7", "IVdim7", "I13", "VI7","IIm7", "V7#9", "I7", "V7#9"]
#progression.reverse()
wholenotes = ["A", "B", "C", "D", "E", "F", "G"]

def getScale(index, keySig, numberOfOctaves):
    switcher = {
        0: scales.Aeolian(keySig),
        1: scales.Bachian(keySig),
        2: scales.Chromatic(keySig),
        3: scales.Diatonic(keySig, (3,7)),
        4: scales.Dorian(keySig),
        5: scales.HarmonicMajor(keySig),
        6: scales.HarmonicMinor(keySig),
        7: scales.Ionian(keySig),
        8: scales.Locrian(keySig),
        9: scales.Major(keySig),
        10: scales.MelodicMinor(keySig),
        11: scales.MinorNeapolitan(keySig),
        12: scales.Mixolydian(keySig),
        13: scales.NaturalMinor(keySig),
        14: scales.Octatonic(keySig),
        15: scales.Phrygian(keySig),
        16: scales.WholeTone(keySig)
    }
    scale = switcher.get(index, None)

    if scale is  None:
        return None
    else:
        converted_scale = []
        for i in range(numberOfOctaves):
            for note in scale.ascending():
                #print note
                converted_scale.append(str(Note(note,4+i)).replace('-','').replace("'",""))
        return converted_scale

def getNotes(txt, stressPatternList, beatList):
    noteList = []
    for beat in beatList:
        tmp = random.choice(thisScale)
        #print(tmp)
        noteList.append(tmp)
    #print(noteList)
    return noteList


def do_default(word, beats, chord):
    strssptn = pr.stresses_for_word(word.lower())
    print "%s %s" % (word, strssptn)
    
    duration = etree.SubElement(tree, 'DURATION', {'BEATS': ','.join([str(b) for b in beats])})
    pitch = etree.SubElement(duration, 'PITCH', {'NOTE': ','.join([str(n) for n in getNotes(word, strssptn, beats)])})
    pitch.text = word


##We're going to give ourselves permission to
##modify the beats and notes with these rules
def compose_noun(word, beats, chord):
    strssptn = pr.stresses_for_word(word.lower())
    print "%s %s %s" % (word, strssptn, len(beats))
    noteList = []
    tmpOctaveNumber = octaveNumber
    for c in range(0,len(beats)):
        print(chord[c % len(chord)])
        if (c > 0) & (chord[c % len(chord)] < chord[(c % len(chord))-1]):
            tmpOctaveNumber += 1
            
        noteList.append("%s%s" % (chord[c % len(chord)],str(tmpOctaveNumber)) )

    ## if the word only has two syllables,
    ## make the last syllable the highest note in the chord.
    if (len(noteList) == 2) & (strssptn[-1] == 1):
        noteList[-1] = "%s%s" % (chord[-1],str(tmpOctaveNumber)) 
        
    duration = etree.SubElement(tree, 'DURATION', {'BEATS': ','.join([str(b) for b in beats])})
    pitch = etree.SubElement(duration, 'PITCH', {'NOTE':  ','.join(noteList) })
    pitch.text = word


def compose_verb(word, beats, chord):
    strssptn = pr.stresses_for_word(word.lower())
    print "%s %s" % (word, strssptn)
    new_beats = [x*1.5 for x in beats]
    noteList = ["%s%s" % (random.choice(chord),str(octaveNumber)) for b in beats]
    
    duration = etree.SubElement(tree, 'DURATION', {'BEATS': ','.join([str(b) for b in new_beats])})
    pitch = etree.SubElement(duration, 'PITCH', {'NOTE': ','.join(noteList)})
    pitch.text = word


def compose_adj(word, beats, chord):
    strssptn = pr.stresses_for_word(word.lower())
    print "%s %s" % (word, strssptn)
    new_beats = [x*3 for x in beats]
    octaveChange = octaveNumber + random.choice([-1,1])
    noteList = ["%s%s" % (c,str(octaveChange)) for c in chord[:len(new_beats)]]
    
    duration = etree.SubElement(tree, 'DURATION', {'BEATS': ','.join([str(b) for b in new_beats])})
    pitch = etree.SubElement(duration, 'PITCH', {'NOTE': ','.join(noteList)})
    pitch.text = word


def buildMelodyByWord(tag_tuple, chord):
    stresspattern = []

    # remember, tag_tuple is in the form of ([word],[POS tag])
    word, part_of_speech = tag_tuple

    # find all syllables in each word
    strssptn = pr.stresses_for_word(word.lower())

    # assign one or more musical notes to each syllable
    # do something different based on stress pattern
    stresspattern += strssptn
    tmpbeats = []
    if len(strssptn) == 0:
        tmpbeats.append(0.0)
    else:
        tmpbeats = [1*float(x) for x in strssptn[0]]

    beats = []
    for bt in tmpbeats:
        if bt == 0.0:
            beats.append(1.0)
        else:
            beats.append(2/bt)

    if re.match("^\W$", word) is not None:
        rest = etree.SubElement(tree, 'REST', {'BEATS': ','.join([str(b) for b in beats])})
    else:
        print(part_of_speech)
        composition_rules[part_of_speech](word, beats, chord)
        
    pattern = ''.join(stresspattern)

# get scale and number of octaves to use
#thisScale = getScale(random.randint(0,16), random.choice(wholenotes), random.randint(1,2))
thisScale = getScale(4, random.choice(wholenotes), random.randint(1,2))

#thisKey = thisScale[0][0]
#thisKey = random.choice(wholenotes)
thisKey = 'F'
print(thisKey)
#progression.reverse()
chords = progressions.to_chords(progression, thisKey)
octaveNumber = 4

composition_rules = {
	'CC' :  do_default, 
	'CD' :  do_default, 
	'DT' :  do_default, 
	'EX' :  do_default, 
	'FW' :  do_default, 
	'IN' :  do_default, 
	'JJ' :  compose_adj, 
	'JJR' :  compose_adj, 
	'JJS' :  compose_adj, 
	'LS' :  do_default, 
	'MD' :  do_default, 
	'NN' :  do_default, 
	'NNS' :  compose_noun, 
	'NNP' :  compose_noun, 
	'NNPS' :  compose_noun, 
	'PDT' :  do_default, 
	'POS' :  do_default, 
	'PRP' :  do_default, 
	'PRP$' :  do_default,
	'RB' :  do_default, 
	'RBR' :  do_default, 
	'RBS' :  do_default, 
	'RP' :  do_default, 
	'TO' :  do_default, 
	'UH' :  do_default, 
	'VB' :  do_default, 
	'VBD' :  compose_verb, 
	'VBG' :  compose_verb, 
	'VBN' :  compose_verb, 
	'VBP' :  compose_verb, 
	'VBZ' :  compose_verb, 
	'WDT' :  do_default, 
	'WP' :  do_default, 
	'WP$' :  do_default,
	'WRB' :  do_default
}


# get text
#text = "Love is the beginning, the middle, the end. Is there any other way to see things?" 
#text = "We are the hollow men. We are the stuffed men. Leaning together. Head pieces filled with straw. Alas!"
#text = "Our dried voices, when We whisper together. Are quiet - and meaningless - ass wind in dry grass, or rats' feet over broken glass In our dry cellar"
#text = 'Shape without form, shade without color. Paralyzed force. Gesture without motion'
#text = "Those who have crossed. With die wrecked eyes, to deaths other Kingdom, Remember us - if at all - not as lost Vie oh lent souls, but only as the hollow men. The stuffed men."
#text = "Eyes. I. Dare not meet in dreams. In death's dream kingdom. These do not appear: There, the eyes are Sunlight on a broken column There, is a tree swing ing, And voices are In the wind's singing. More distant. and more solemn. Than a fading star."
#text = "Let me be no nearer In deaths dream kingdom. Let me also wear Such deliberate disguises - - Rats coat, crow skin, crossed staves - In a field Behaving as the wend behaves. No nearer. Not that final meeting In the twilight kingdom"
#text = "This is the dead land. This is cactus land. Here the stone images Are raised. Here they receive The sup plick kay shun of a dead mans hand under the twin kill of a fading star."
#text = "Is it like this In deaths other kingdom? Waking alone at the hour when we are Tremble ling with tender ness? Lips that would kiss. form prayers to broken stone."
#text = "The eyes are not here. There are no eyes here. In this valley of dying stars, In this hollow valley. This broken jaw of our lost kingdoms"
#text = "In this last of meeting places, We grope together And avoid speech. Gathered on this beach of the too mid river."
#text = "Sight less. Unless the eyes reappear as the pear pet you all star. Mull tee foe lee et rose of deaths twilight kingdom. The hope only of empty men."
#text = "Here we go round the prickly pear, Prickly pear, prickly pear. Here we go round the prickly pear At five o'clock in the morning."
#text = "Between the idea and the reality, between the motion and the act, falls the Shadow."
#text = "For Thine is the Kingdom"
#text = "Between the conception and the creation, between the emotion and the response, falls the Shadow."
#text = "Life is very long"
#text = "Between the desire and the spasm, between the potency and the existence, between the essence and the descent, falls the Shadow"
#text = "For Thine is the Kingdom"
#text = "For Thine is. Life is. For Thine is the"
text = "This is the way the world ends. This is the way the world ends. This is the way the world ends: Not with a bang, but a whimper."

#initial variables
rootString = """<?xml version="1.0"?>
<!DOCTYPE SINGING PUBLIC "-//SINGING//DTD SINGING mark up//EN" "Singing.v0_1.dtd" []>
<SINGING BPM="%s"/>"""

# set BPM
BPM = 100


# find all words in each sentence
chordIndex = 0
for x in range(0,4):
    melodyXmlDoc = rootString % BPM

    # start building the XML
    tree = etree.fromstring(melodyXmlDoc)
    doc = etree.ElementTree(tree)

    # break up text into sentences
    sent_tokenize_list = sent_tokenize(text)

    for sent in sent_tokenize_list:
        word_tokenize_list = pos_tag(word_tokenize(sent))
        #print(sent)
        
        for word in word_tokenize_list:
            buildMelodyByWord(word, chords[chordIndex % len(chords)])
            chordIndex += 1
                    
    # Save to XML file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fileName = os.path.join(os.getcwd(), 'output-%s.xml' % (x+1) )
    doc.write(fileName, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    #print("done")
    if x % 2 == 0:
        #festival.execCommand("(%s )" % ('voice_us1_mbrola'))
        voice = 'voice_us1_mbrola'
    else:
        #festival.execCommand("(%s )" % ('voice_kal_diphone'))
        voice = 'voice_kal_diphone'

    #print('-eval "(%s )"' % (voice))
    #festival.execCommand("(tts \"%s\" `singing)" % (fileName))
    #p1 = subprocess.Popen(['/usr/bin/text2wave', '-mode', 'singing',  '%s' % (fileName), '-o', 'output-%s.wav' % (x+1), '-eval', '"(%s )"' % (voice)])

    # Run the command
    #output = p1.communicate()[0]
    #print output
 
#p2 = subprocess.Popen(['ch_wave', '-o  result-full.wav', '-pc longest', 'output-?.wav'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['./rendersong.sh'])
# Run the command
#output = p2.communicate()

#print output

