#!/bin/python

import sys
import getopt
import subprocess
import os
import datetime

from datetime import timedelta
from scipy.io import wavfile
from os.path import splitext


def findToneMillis( samples, sampleRate, offsetMillis, frequencyThreshold, amplitudeThreshold, signalLengthThreshold ):
  windowMillis = 10 # ms
  windowLength = round(windowMillis*sampleRate/1000.0)

  windowOffset = offsetMillis//windowMillis
  n = int( len(samples)/windowLength )
  signalStartMillis = -1

  for i in range(windowOffset, n):
    window = samples[i*windowLength: (i+1)*windowLength]
    frequency = calculateFrequency(window, sampleRate)
    amplitude = calculateAmplitude(window)
    millis = round(i*windowMillis)

    if frequency >= frequencyThreshold and amplitude >= amplitudeThreshold:
      if signalStartMillis == -1:
        signalStartMillis = millis
    elif signalStartMillis != -1:
      if millis - signalStartMillis >= signalLengthThreshold:
        return signalStartMillis, millis
      else:
        signalStartMillis = -1

  return -1, -1

def calculateFrequency( samples, sampleRate ):
  s_prev = float(samples[0])
  count = 0
  n = len(samples)
  for i in range(1, n):
    s_i = float(samples[i])
    if s_prev*s_i <= 0 : count += 1
    s_prev = s_i

  return 0.5*count*sampleRate/n


def calculateAmplitude( samples ):
  s_prev = float(samples[0])
  maxValue = abs(s_prev)
  count = 0
  sumMax = 0
  n = len(samples)
  for i in range(n):
    s_i = float(samples[i])
    maxValue = max(maxValue, abs(s_i))
    if s_prev * s_i < 0:
      sumMax += maxValue
      count += 1
      maxValue = 0
    s_prev = s_i
  return sumMax/count if count > 0 else 0


def convertAndReadWavFile(audioFile):
  if audioFile.endswith('.wav'):
    wavFile = audioFile
  else:
    print(f"Converting {audioFile} to WAV format")
    wavFile = splitext(audioFile)[0] + '.wav'
    if not os.path.isfile(wavFile):
      subprocess.run(
        ['ffmpeg', '-y', '-i', f'{audioFile}', f'{wavFile}'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.STDOUT,
        check = True
      )

  sampleRate, samples = wavfile.read(wavFile)
  return wavFile, sampleRate, samples

def writeSectionToWavFile( srcFilename, sampleRate, samples, startMillis, endMillis=-1 ):
  i_start = round(startMillis*sampleRate/1000.0)
  i_end = round(endMillis*sampleRate/1000.0) if endMillis != -1 else len(samples)
  toneStartMoment = datetime.datetime.fromtimestamp(startMillis / 1000.0, tz=datetime.timezone.utc)
  sectionWavFile = splitext(srcFilename)[0] + ' - ' + toneStartMoment.strftime('%H_%M_%S')  + '.wav'
  section = samples[i_start : i_end]
  wavfile.write(sectionWavFile, sampleRate, section)

if __name__ == '__main__':
  try:
    audioFile = sys.argv[1]
    print(f"Loading {audioFile}")
  except IndexError:
    print('Missing input file!')
    sys.exit(2)

  wavFile, sampleRate, samples = convertAndReadWavFile(audioFile)
  print(f"Sample rate = {sampleRate}Hz")
  length = samples.shape[0] / sampleRate
  print("Length = {:.2f}s".format(length))

  if samples.shape[1] == 2:
    samples = samples[:,0]

  offsetMillis = 0
  prevToneStartMillis = -1
  print("Looking for tones")
  while True:
    toneStartMillis, toneEndMillis = findToneMillis( samples, sampleRate, offsetMillis, 800, 10000, 500 )
    if toneStartMillis == -1:
      if prevToneStartMillis != -1:
        writeSectionToWavFile( wavFile, sampleRate, samples, prevToneStartMillis )
      break

    if prevToneStartMillis != -1:
      writeSectionToWavFile( wavFile, sampleRate, samples, prevToneStartMillis, toneStartMillis )

    toneStartMoment = str(timedelta(milliseconds=toneStartMillis))[:-3]
    print(f"Found tone at {toneStartMoment}")
    prevToneStartMillis = toneStartMillis
    offsetMillis = toneEndMillis

  if prevToneStartMillis == -1:
    print("No tones found")
