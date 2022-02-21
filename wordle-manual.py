#!/bin/python
import re
from dataclasses import dataclass


@dataclass
class Word:
    word: str
    frequency: int


wordLen = 5


def readFile(filename: str) -> [str]:
    d = []
    with open(filename, "r") as file:
        for line in file:
            line = line.rstrip().lower()
            if len(line)==wordLen:
                d.append(line)

    return d


# Read file consists of words and corresponding frequency
def read_file_frequency(filename: str) -> [Word]:
    wordList = []
    with open(filename, "r") as file:
        for line in file:
            frequency, word = re.split(r"[\t\s]+", line.rstrip().lower())[:2]
            if len(word)==wordLen and word.isalpha() and frequency.isdigit():
                wordList.append(Word(word, int(frequency)))

    wordList.sort(key=lambda w: w.frequency, reverse=True)

    return wordList


# Check whether word is possibly correct
def isWordPossible(word: str, nonExistLetterList: str, wrongPositionLetterDict: dict, mustExistLetterList: str, correctLetterDict: dict, wordLen: int) -> bool:
    if len(word)!=wordLen:
        return False

    for c in mustExistLetterList:
        if c not in word:
            return False

    for i in range(len(word)):
        c = word[i]

        if c in nonExistLetterList:
            return False
        if c in wrongPositionLetterDict[str(i)]:
            return False
        if len(correctLetterDict[str(i)])>0 and c!=correctLetterDict[str(i)]:
            return False

    return True


def main():
    possibleWordList = sorted(read_file_frequency("./english.txt"), key=lambda w: w.frequency, reverse=False)
    nonExistLetterList = ""
    wrongPositionLetterDict = {
        "0": "",
        "1": "",
        "2": "",
        "3": "",
        "4": "",
    }
    correctLetterDict = {
        "0": "",
        "1": "",
        "2": "",
        "3": "",
        "4": "",
    }
    mustExistLetterList = ""
    for pos in wrongPositionLetterDict:
        mustExistLetterList += wrongPositionLetterDict[pos] + correctLetterDict[pos]

    possibleWordList = list(
        filter(
            lambda w: isWordPossible(w.word, nonExistLetterList, wrongPositionLetterDict, mustExistLetterList, correctLetterDict, wordLen),
            possibleWordList))

    for w in possibleWordList:
        print(w.word, w.frequency)


main()
