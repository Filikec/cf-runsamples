import requests
from bs4 import BeautifulSoup
import argparse
import subprocess
import threading
import os

PROMENNA = "g++ -Wall -Wextra -g3 -std=c++20"
CPP = True

def compileProgram(problemId):
    subprocess.run(PROMENNA + f" {problemId}.cpp -o {problemId}.exe")

def printCorrect(text):
    print(f'\033[92m{text}\033[0m')   

def printIncorrect(text):
    print(f'\033[91m{text}\033[0m')

## parse arguments
parser = argparse.ArgumentParser(description='Run samples for a contest. Runs .cpp by default, searches for .py if cpp not present.')
parser.add_argument('contestId', type=int, help='id of the contest')
parser.add_argument('problemId', type=str, help='id of contest (a,b,c...)')
parser.add_argument('-py', action='store_true', help='force python solution')

args = parser.parse_args()
problemId = args.problemId.lower()
contestId = args.contestId
py = args.py

if (py): CPP = False
else:
    if (os.path.exists(f"{problemId}.cpp")): CPP = True
    elif (os.path.exists(f"{problemId}.py")): CPP = False
    else:
        printIncorrect("No solution file")
        exit(0)

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

    for s in soup.find_all(class_="input"):
        sample_input = ""
        for t in s.find_all("div"):
            if (t["class"].count("test-example-line")): sample_input += t.text.strip() + '\n'
        inputs.append(sample_input)

    for s in soup.find_all(class_="output"):
        outputs.append(s.find("pre").text.strip())

    if (CPP): thread.join()

    for i in inputs:
        command_string = f"{problemId}.exe"
        if (not CPP): command_string = f"python {problemId}.py"

        proc = subprocess.run(command_string, input=i, text=True, capture_output=True, check=True)
        outputs_my.append(proc.stdout.strip())
    
    for i in range(len(outputs)):
        b = outputs[i] != outputs_my[i]
        if (b): samples_accepted = False
        if (b): printIncorrect(f'Test case: {i+1}')
        else: printCorrect(f'Test case: {i+1}')
        print("Output:")
        print(outputs[i])
        print("Actual output")
        print(outputs_my[i])
        print("シシシシシシシシシシシシシシシシシシ")

    if (samples_accepted): printCorrect("CORRECT")
    else: printIncorrect("INCORRECT")

else:
    print('Failed to retrieve the webpage')