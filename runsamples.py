import requests
from bs4 import BeautifulSoup
import argparse
import subprocess
import threading
import os
import sys
import json

CPP = True

def compileProgram(problemId):
    subprocess.run(f"g++ -Wall -Wextra -g3 -std=c++20 {problemId}.cpp -o {problemId}.exe")

def printCorrect(text):
    print(f'\033[92m{text}\033[0m')   

def printIncorrect(text):
    print(f'\033[91m{text}\033[0m')

## parses input from html for one problem statement
def parseInputs(soup):
    inputs = []
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
    return inputs

def parseOutputs(soup):
    outputs = []
    ## parse output
    for s in soup.find_all(class_="output"):
        outputs.append(s.find("pre").text.strip())
    return outputs

def runSoultion(inputs,problemId):
    outputs_my = []
    for i in inputs:
        command_string = f"{problemId}.exe"
        if (not CPP): command_string = f"python {problemId}.py"

        proc = subprocess.run(command_string, input=i, text=True, capture_output=True, check=True)
        outputs_my.append(proc.stdout.strip())
    return outputs_my

def testSolution(outputs,outputs_my,inputs):
    samples_accepted = True
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

def parseProblems(contestId):
    if (not os.path.isdir("samples")):
        os.mkdir("samples")
    tests = []
    url = f'https://codeforces.com/contest/{contestId}/problems'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        for s in soup.find_all(class_="problemindexholder"):
            tests.append((parseInputs(s),parseOutputs(s),s["problemindex"]))
        printCorrect("Parsed problems")
    else:
        printIncorrect('Failed to retrieve the webpage')
    
    return tests

def saveTests(tests):
    for test in tests:
        data = {
            "inputs": test[0],
            "outputs": test[1]
        }

        file_name = f'{test[2]}.json'.lower()

        with open(os.path.join("samples",file_name), 'w') as json_file:
            json.dump(data, json_file, indent=4)

def getParsedProblem(problemId):
    with open(os.path.join("samples",f'{problemId}.json'), 'r') as json_file:
        data = json.load(json_file)
    
    return data

def run():
    args = parser.parse_args()
    problemId = args.problemId.lower()
    py = args.py

    ## set correct solution file
    if (os.path.exists(f"{problemId}.cpp") and not py): CPP = True
    elif (os.path.exists(f"{problemId}.py")): CPP = False
    else:
        printIncorrect("No solution file")
        sys.exit(0)

    # if cpp start compilation before request
    if (CPP):
        thread = threading.Thread(target=compileProgram, args=(problemId,))
        thread.start()

    # check if parsed already
    if (not os.path.isdir("samples")):
        printIncorrect("Problems weren't parsed")
    
    test_data = getParsedProblem(problemId)
    thread.join()
    outputs_my = runSoultion(test_data['inputs'],problemId)

    testSolution(test_data["outputs"],outputs_my,test_data["inputs"])

def parse():
    args = parser.parse_args()
    contestId = args.contestId
    saveTests(parseProblems(contestId))


parser = argparse.ArgumentParser(description='Run samples for a contest. Runs .cpp by default, searches for .py if cpp not present.')
subparsers = parser.add_subparsers()

parser_parseProblems = subparsers.add_parser('parse', help='Parse all problems for the contest')
parser_parseProblems.add_argument('contestId', type=int, help='id of the contest')
parser_parseProblems.set_defaults(func=parse)

parser_test = subparsers.add_parser('run', help='Test solution on samples. The executable must have the same name as the sample file.')
parser_test.add_argument('problemId', type=str, help='id of the problem (a,b,c...)')
parser_test.add_argument('-py', action='store_true', help='force use python solution')
parser_test.set_defaults(func=run)

args = parser.parse_args()
args.func()