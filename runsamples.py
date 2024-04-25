import requests
from bs4 import BeautifulSoup
import argparse
import subprocess
import threading
import os
import sys

CPP = True

def compileProgram(problemId):
    subprocess.run(f"g++ -Wall -Wextra -g3 -std=c++20 {problemId}.cpp -o {problemId}.exe")

def printCorrect(text):
    print(f'\033[92m{text}\033[0m')   

def printIncorrect(text):
    print(f'\033[91m{text}\033[0m')

## parse arguments
parser = argparse.ArgumentParser(description='Run samples for a contest. Runs .cpp by default, searches for .py if cpp not present.')
parser.add_argument('contestId', type=int, help='id of the contest')
parser.add_argument('problemId', type=str, help='id of the problem (a,b,c...)')
parser.add_argument('-py', action='store_true', help='force use python solution')

args = parser.parse_args()
problemId = args.problemId.lower()
contestId = args.contestId
py = args.py

## set correct solution file
if (os.path.exists(f"{problemId}.cpp") and not py): CPP = True
elif (os.path.exists(f"{problemId}.py")): CPP = False
else:
    printIncorrect("No solution file")
    sys.exit(0)

## if cpp start compilation before request
if (CPP):
    thread = threading.Thread(target=compileProgram, args=(problemId,))
    thread.start()

url = f'https://codeforces.com/contest/{contestId}/problem/{problemId}'

response = requests.get(url)
samples_accepted = True

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    inputs = []
    outputs = []
    outputs_my = []

    ## parse input
    for s in soup.find_all(class_="input"):
        sample_input = ""
        got = False # at least on input parsed
        for t in s.find_all("div"):
            if (t["class"].count("test-example-line")):
                sample_input += t.text.strip() + '\n'
                got = True
        # if no input parsed, html is slightly different
        if (got): inputs.append(sample_input[:-1])
        else: inputs.append(s.find("pre").text.strip())
    
    ## parse output
    for s in soup.find_all(class_="output"):
        outputs.append(s.find("pre").text.strip())

    ## if cpp make sure compilation finishes
    if (CPP): thread.join()

    ## run solution
    for i in inputs:
        command_string = f"{problemId}.exe"
        if (not CPP): command_string = f"python {problemId}.py"

        proc = subprocess.run(command_string, input=i, text=True, capture_output=True, check=True)
        outputs_my.append(proc.stdout.strip())
    
    ## test correctness
    for i in range(len(outputs)):
        if (outputs[i] != outputs_my[i]): 
            samples_accepted = False
            printIncorrect(f'Test case: {i+1}')
        else: printCorrect(f'Test case: {i+1}')
        print("Input:")
        print(inputs[i])
        print("Example output:")
        print(outputs[i])
        print("Actual output")
        print(outputs_my[i])
        print("シシシシシシシシシシシシシシシシシシ")
    ## verdict 
    if (samples_accepted): printCorrect("CORRECT")
    else: printIncorrect("INCORRECT")
else:
    print('Failed to retrieve the webpage')