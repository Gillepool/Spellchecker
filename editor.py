#!/usr/bin/env python3
import sys, os
import threading
from nltk.corpus import words
import difflib
import re
from collections import Counter
import queue

threadLock = threading.Lock()

def words(text): return re.findall(r'\w+', text.lower())

WORDS = Counter(words(open('big.txt').read()))

def Probability(word): 
	"Probability of a word"
    N = sum(WORD.values())
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

class Editor():
	def __init__(self):
		self.q = queue.Queue()

	def spellCheck(self, word, queue):
		#print("Current thread = " + threading.current_thread().name)
		threadLock.acquire()
		newWord = word
		if not word.lower() in WORDS:
			print("Did you spell " + word + " correctly?")
			print("Did you mean " + str(candidates(word)) + "?")
			choice = input("Input the number of the element in the list(0 is the first element) is corrent or any other key to skip")
			if choice.isdigit():
				if (int(choice) < len(candidates(word))) and (int(choice) >= 0):
					newWord = str(list((candidates(word)))[int(choice)])
					print("New word: " + newWord)
					self.q.put(newWord)
				else:
					print("You entered an invalid index")
			else:
				self.q.put(word)
			
		else:
			self.q.put(word)

		threadLock.release()

	def write(self, file):
		threads = []
		
		try:
			f = open(file, 'a')
		except:
			print("Something went wrong")
			sys.exit()

		with f:
			while True:
				line = input("> ")
				if(line == 'exit'):
					f.close()
					break
				words = line.split()
				#print("Words " ,  words)
				for i, word in enumerate(words):
					thread = threading.Thread(target=self.spellCheck, name=word, args=[word, queue])
					thread.start()
					try:
						words[i] = self.q.get()
					except queue.Empty:
						print("Queue was empty")
				for thread in threads:
					thread.join()
				
				f.write(" ".join(words))
				f.write('\n')
				

	def deleteFile(self, filename):
		try:
			os.unlink(filename)
		except:
			print("Could not delete the file")
			sys.exit()
	
	def read(self, file):
		try:
			f = open(file, 'r')
		except:
			print("File not found")
			sys.exit()

		with f:
			print("File: " + str(file))
			print("".join(f.readlines()))
			f.close()

if __name__ == "__main__":
	editor = Editor()
	while True:
		choice = input("Woudl you like to read, write or delete file? ")
		if(choice.lower() == 'write'):
			filename = input("Enter a filename to write: ")
			editor.write(filename)
		elif(choice.lower() == 'read'):
			filename = input("Enter a filename to read: ")
			editor.read(filename)
		elif(choice.lower() == 'delete'):
			filename = input("Enter a filename to delete: ")
			editor.deleteFile(filename)
	