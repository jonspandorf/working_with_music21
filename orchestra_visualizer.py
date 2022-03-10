#!/usr/bin/env python
# coding: utf-8

# In[132]:


from music21 import *
import numpy as np
import seaborn as sns
import matplotlib as plt
from fractions import Fraction
import pandas as pd
import math


# In[133]:


class Beat():
    def __init__(self,numOfDivisions,current_beat,measureNumber,idx=0):
        self.pitches = np.zeros(numOfDivisions)
        self.points_in_time = np.linspace(current_beat,current_beat+1,numOfDivisions)
#         maybe instead using np.arange(1,numOfDivisions) -> add as a string <measureNumber> + '.' + <beat> + '.' + 'div' > to binary
        if numOfDivisions > 1:
            self.points_in_time = self.points_in_time[:-1]
        self.idx = idx
        self.measureNumber = measureNumber
    
    def AddOneNoteToBeat(self,pitch,div):
        self.pitches[self.idx] =  pitch
        self.idx = div
    
    
    def AddSinglePointInTime(self):
        beat,loc = divmod(self.points_in_time[self.idx],1)
        if loc:
            point = str(int(beat))+str(int(loc))
            point = int(point)
        else: 
            point = int(beat)
        current_point = str(self.measureNumber) + '.' + str(point)
        current_point = np.float32(current_point)
        self.points_in_time[self.idx] = current_point
    
    def GetPitches(self):
        return self.pitches
    
    def GetPointsInTime(self):
        return self.points_in_time
    
    def GetBeatLength(self):
        return self.pitches.size
    
    def GetLastInsertedIdx(self):
        return self.idx


# In[134]:


def IsTheBeatDivided(beat):
    if beat.quarterLength >= 1:
        return math.ceil(beat.quarterLength), False
    else:
        return Fraction(beat.quarterLength).denominator, True


# In[135]:


def BeatDividedByHow(beat):
    return Fraction(beat.quarterLength).numerator


# In[136]:


def GetPitch(note):
    p = pitch.Pitch(note)
    return p.freq440


# In[137]:


def GetClassName(element):
    the_type = type(element)
    return the_type.__name__


# In[138]:


def IsNowDownBeat(idx, divs):
    if idx == divs:
        return True
    else:
        return False


# In[139]:


def AddLongerThanBeat(numOfDivs,measureNumber,currentBeat,element,className):
    if className == 'Note':
        pitch = GetPitch(element.nameWithOctave)
    else:
        pitch = 0
    beat = Beat(numOfDivs,currentBeat,measureNumber)
    if pitch:
        beat.AddOneNoteToBeat(pitch,0)
    beat.AddSinglePointInTime()
    return beat.GetPitches(), beat.GetPointsInTime()


# In[140]:


def HandleSingleBeat(beat,isDivided,isDownBeat,divs,element,className):
    pitch = 0
    if className == 'Note':
        pitch = GetPitch(element.nameWithOctave)
    if isDownBeat:
        if isDivided:
            for div in range(divs-1):
                beat.AddOneNoteToBeat(pitch,div)
                beat.AddSinglePointInTime()        
        else:
            beat.AddOneNoteToBeat(pitch,0)
            beat.AddSinglePointInTime()
        nextIsDownBeat = IsNowDownBeat(beat.GetLastInsertedIdx()+1,beat.GetBeatLength())
    else:
        div = beat.GetLastInsertedIdx()
        if isDivided:
            while div < beat.GetBeatLength():
                beat.AddOneNoteToBeat(pitch,div)
                beat.AddSinglePointInTime()
        nextIsDownBeat = IsNowDownBeat(beat.GetLastInsertedIdx()+1,beat.GetBeatLength())  
    return nextIsDownBeat, beat


# In[141]:


def HandleMeasure(measure):
    isDownBeat = True
    current_beat = 1
    longerThanQuarterValue = 0
    pitches = []
    points_in_time =  []
    init = True
    next_is_downbeat = False
    divs = 1
    for element in measure.flatten().getElementsByClass(['Note','Rest']):
        className = GetClassName(element)
        smallestDiv = 1
        isDivided = False
        if isDownBeat:
            smallestDiv,isDivided = IsTheBeatDivided(element)
            if not isDivided and smallestDiv > 1:
                longerThanQuarterValue = smallestDiv
            elif isDivided:
                divs = BeatDividedByHow(element)
        if longerThanQuarterValue:
            current_pitches = []
            current_points = []
            for num in range(longerThanQuarterValue):
                pitch, point = AddLongerThanBeat(1,measure.measureNumber,current_beat,element,className)
                if num == 0:
                    current_pitches = pitch
                    current_points = point
                else:
                    current_pitches = np.concatenate((current_pitches,pitch))
                    current_points = np.concatenate((current_points,point))
                current_beat +=1
            if init:
                pitches = current_pitches
                points_in_time = current_points
                init = False
            else:
                pitches = np.concatenate((pitches, current_pitches))
                points_in_time = np.concatenate((points_in_time,current_points))
        else:
            if isDownBeat:
                beat = Beat(divs,current_beat,measure.measureNumber)
                next_is_downbeat,beat = HandleSingleBeat(beat,isDivided,isDownBeat,divs,element,className)
            if not next_is_downbeat:
                next_is_downbeat,beat= HandleSingleBeat(beat,isDivided,isDownBeat,divs,element,className)
            else:
                beat_pitches,beat_points = beat.GetPitches(),beat.GetPointsInTime()
                if init:
                    pitches = beat_pitches
                    points_in_time = beat_points
                    init = False
                else:
                    pitches = np.concatenate((pitches,beat_pitches))
                    points_in_time = np.concatenate((points_in_time,beat_points)) 
            isDownBeat = next_is_downbeat
            current_beat+=1
        
    return pitches, points_in_time 


# In[142]:


if __name__ == '__main__':
    y_axes = []
    x_axes = []
    s = converter.parse("C:\\Users\\jonathansp\\Downloads\Beethoven_Symphony_No._1_in_C_Op._21_Full_Score.mxl")
    vln_counter = 1
    for part in s.parts.measures(187,190):
        inst = part.getInstrument().partAbbreviation
        is_init = True
        if inst == 'Vlns.':
            inst = inst + f'{vln_counter}'
            vln_counter +=1 
        pitches = []
        timeline = []
        for measure in part.getElementsByClass('Measure'):
            pitches_in_measure, timeline_of_measure = HandleMeasure(measure)
            if is_init:
                pitches = pitches_in_measure
                timeline = timeline_of_measure
                is_init = False
            else:
                pitches = np.concatenate((pitches, pitches_in_measure))
                timeline = np.concatenate((timeline, timeline_of_measure))
        y_axes.append({inst:pitches})
        x_axes.append(timeline)
        


# In[ ]:





# In[143]:


df = ''

for idx,inst in enumerate(y_axes):
    cur_df = pd.DataFrame(data=inst,index=x_axes[idx])
    if idx > 0:
        df = df.join(cur_df)
    else:
        df = cur_df

df


# In[144]:


sns.set(rc={'figure.figsize':(15,8)})

plot = sns.scatterplot(data=df)

plot


# In[96]:


fig = plot.get_figure()
fig.savefig('example.png')


# In[37]:


#


# In[95]:


# this is from the longerthan beat iteration
#                 if init:
#                     pitches = np.asarray(current_pitches)
#                     points_in_time = np.asarray(current_points)
#                     init = False
#                 else:
#                     print('returning')
#                     pitches = np.concatenate((pitches,pitch))
#                     points_in_time = np.concatenate((points_in_time,np.array(point)))


# In[113]:


arr = np.linspace(3,4,4)
print(arr)


# In[ ]:




