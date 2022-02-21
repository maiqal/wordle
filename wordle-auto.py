#!/bin/python
import re
import copy
from enum import Enum
import time
from dataclasses import dataclass


@dataclass
class Word:
    word: str
    frequency: int


wordLen = 5
maxAttempt = 6

Result = Enum("Result", "correct wrongPosition notExist")


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
def isWordPossible(word: str, nonExistLetterList: [str], wrongPositionLetterList: [str], mustExistLetterList: [str], correctLetterList: [str], wordLen: int) -> bool:
    if len(word)!=wordLen:
        return False

    for c in mustExistLetterList:
        if c not in word:
            return False

    for i in range(len(word)):
        c = word[i]
        if c in nonExistLetterList:
            return False
        if c in wrongPositionLetterList[i]:
            return False
        if correctLetterList[i] and c!=correctLetterList[i]:
            return False

    return True


# Simulate the wordle game and return result
def guess(word, answer) -> []:
    result = [None for i in range(wordLen)]

    for i in range(len(word)):
        if word[i]==answer[i]:
            result[i] = Result.correct
        elif word[i] not in answer:
            result[i] = Result.notExist
        else:
            result[i] = Result.wrongPosition

    return result


def parseResult(guessWord: str, result: Result, nonExistLetterList: [str], wrongPositionLetterList: [str], mustExistLetterList: [str], correctLetterList: [str]) -> bool:
    for i in range(len(result)):
        guessWordLetter = guessWord[i]
        if result[i] == Result.correct:
            correctLetterList[i] = guessWordLetter
        elif result[i] == Result.wrongPosition:
            wrongPositionLetterList[i].append(guessWordLetter)
            mustExistLetterList.append(guessWordLetter)
        elif result[i] == Result.notExist and guessWordLetter not in nonExistLetterList:
            nonExistLetterList.append(guessWordLetter)

    return None not in correctLetterList



def startGame(wordList: [Word], answer: str) -> int:
    nonExistLetterList = []
    wrongPositionLetterList = [[] for i in range(wordLen)]
    correctLetterList = [None for i in range(wordLen)]
    mustExistLetterList = []
    numberOfAttempt = 0
    possibleWordList = copy.deepcopy(wordList)

    while True:
        possibleWordList = list(
            filter(lambda w: isWordPossible(w.word, nonExistLetterList, wrongPositionLetterList, mustExistLetterList, correctLetterList, wordLen),
                   possibleWordList))

        # Put strategy here
        guessWord = immediateGuess(possibleWordList)
        # print("guess={}".format(guessWord))
        # guessWord = maxSimilarityGuess(possibleWordList, correctLetterList)

        result = guess(guessWord, answer)
        numberOfAttempt += 1

        # parse result
        if parseResult(guessWord, result, nonExistLetterList, wrongPositionLetterList, mustExistLetterList, correctLetterList):
            break

    return numberOfAttempt


"""
Strategy that uses the first possible word to make a guess
Benchmark:
[Using words.txt] (with word only)
total attempt=155777
exceed max attempt=14357
word list size=21952
time elapsed=719.5024704933167 seconds
7.096 attempt/word
exceed percentage=65.4%

[Using english.txt] (with sorted frequencies)
total attempt=62439
exceed max attempt=3754
word list size=10293
time elapsed=634.0653598308563 seconds
6.066 attempt/word
exceed percentage=36.47%
"""
def immediateGuess(possibleWordList: [Word]) -> str:
    # When using a list sorted by frequency, this strategy means using the word with highest frequency
    return possibleWordList[0].word


"""
Strategy that uses the possible word, which has the most similarity to other words, to make a guess
Benchmark:
[Using words.txt] (with word only)
total attempt=131113
exceed max attempt=6676
word list size=21952
time elapsed=1257.3181729316711 seconds
5.973 attempt/word
exceed percentage=30.41%

[Using english.txt] (with sorted frequencies)
total attempt=55231
exceed max attempt=1565
word list size=10293
time elapsed=785.3681900501251 seconds
5.3659 attempt/word
exceed percentage=15.205%
"""
def maxSimilarityGuess(possibleWordList: [Word], correctLetterList: [str]) -> str:
    """
    Get the word from possibleWordList that has the letter L at position P,
    where L at P occurs the most among possibleWordList
    """

    """
    letterOccurrenceMap:
    [
        {"a": occurrence, "b": occurrence, "c": occurrence, ...},
        {"a": occurrence, "b": occurrence, "c": occurrence, ...},
        {"a": occurrence, "b": occurrence, "c": occurrence, ...},
        ...
    ]
    """
    letterOccurrenceMap = [{} for i in range(wordLen)]

    """
    occurrenceMap:
    {
        "word-1": sum of word-1 occurrence,
        "word-2": sum of word-2 occurrence,
        "word-3": sum of word-3 occurrence,
        ...
    }    
    """
    occurrenceMap = {}

    # Compute letter occurrence map
    for i in range(len(correctLetterList)):
        # if i-th letter is not confirmed yet
        if not correctLetterList[i]:
            for p in possibleWordList:
                if p.word[i] not in letterOccurrenceMap[i]:
                    letterOccurrenceMap[i][p.word[i]] = 1
                else:
                    letterOccurrenceMap[i][p.word[i]] += 1

    # Compute occurrenceMapList
    for i in range(len(correctLetterList)):
        # if i-th letter is not confirmed yet
        if not correctLetterList[i]:
            for p in possibleWordList:
                if p.word not in occurrenceMap:
                    occurrenceMap[p.word] = letterOccurrenceMap[i][p.word[i]]
                else:
                    occurrenceMap[p.word] += letterOccurrenceMap[i][p.word[i]]


    # Find max similarity word
    maxOccurrence = 0
    maxOccurrenceWord = None
    for w in occurrenceMap:
        if occurrenceMap[w]>maxOccurrence:
            maxOccurrence = occurrenceMap[w]
            maxOccurrenceWord = w

    return maxOccurrenceWord


def main():
    wordList = read_file_frequency("./english.txt")
    totalAttempt = 0
    exceedMaxAttempt = 0

    startTime = time.time()
    for i in range(len(wordList)):
        answer = wordList[i].word
        attempt = startGame(wordList, answer)
        if attempt<0:
            print("{} {} {} === Error".format(i, answer, attempt))
            continue

        totalAttempt += attempt
        print("{} {} {}".format(i, answer, attempt))
        if attempt>maxAttempt:
            exceedMaxAttempt += 1
        break

    endTime = time.time()
    print("total attempt={}".format(totalAttempt))
    print("exceed max attempt={}".format(exceedMaxAttempt))
    print("word list size={}".format(len(wordList)))
    print("time elapsed={} seconds".format(endTime-startTime))


main()
