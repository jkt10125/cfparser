#!/usr/bin/env python3

# input: python3 vamos.py <problem_idx>
# output: compiles __.cc and runs it with the input and output of the problem with index problem_idx

import subprocess, argparse, requests
from bs4 import BeautifulSoup
import cfparse

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
ENDC = '\033[0m'

def compile(filename, flags):
    print('Compiling file: ' + filename)
    if flags == '-DDEBUG':
        result = subprocess.run(['g++', '-std=c++20', '-Wall', '-Wextra', '-Wconversion', '-Wfloat-equal', '-Wshadow', '-fsanitize=address', '-fsanitize=undefined', '-g', '-D_GLIBCXX_DEBUG', '-D_GLIBCXX_DEBUG_PEDANTIC', filename, flags])
    else:
        result = subprocess.run(['g++', '-std=c++20', '-Wall', filename, flags])
    if result.returncode != 0:
        print('Compilation error')
        exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-f', help='Filename to compile and use for testing', default='a.cc')
    parser.add_argument('--contest', '-c', help='Contest name', default='0')
    parser.add_argument('--problem', '-p', help='Select problem_idx to test', default='$')
    parser.add_argument('--flags', '-F', help='Flags to pass to the compiler', default='-DDEBUG')
    parser.add_argument('--test', '-t', help='Enter the problem directly to test', default='0')

    args = parser.parse_args()
    filename = args.filename
    contest = args.contest
    problem = args.problem
    flags = args.flags
    test = args.test

    compile(filename, flags)

    inputs = []
    outputs = []

    if test != '0':
        link = 'https://codeforces.com/problemset/problem/' + test
        soup = BeautifulSoup(requests.get(link).content, 'html.parser')
        inputs, outputs = cfparse.get_input_output(soup)

    else:
        if contest == '0':
            print('No contest specified! Running in local mode...')
            # simply run the program on the terminal
            result = subprocess.run(['./a.out'], text=True)
            print(result.stdout)
            return
        try:
            with open(contest + '.txt', 'r') as f:
                lines = f.read().split('\n')
        except FileNotFoundError:
            print('File not found! Run cfparse.py ' + contest + ' first to create the file.')
            print('Running in local mode...')
            # simply run the program on the terminal
            result = subprocess.run(['./a.out'], text=True)
            print(result.stdout)
            return

        target_line = next((i for i, line in enumerate(lines) if line.startswith(problem)), -1) + 1

        for i in range(target_line, len(lines)):
            line = lines[i].split(' : ')
            if not lines[i] or line[0] != str(i - target_line):
                break
            inputs.append(line[1].split('€ '))
            outputs.append(line[2].split('€ '))

    if not inputs:
        print('No test cases found for problem ' + problem + ' Running in local mode...')
        # simply run the program on the terminal
        result = subprocess.run(['./a.out'], text=True)
        print(result.stdout)
        return

    for i in range(len(inputs)):
        print('Running test case ' + str(i))
        result = subprocess.run(['./a.out'], input='\n'.join(inputs[i]), text=True, capture_output=True)
        if result.stdout.strip().split('\n') == outputs[i]:
            print(GREEN + 'Accepted' + ENDC)
        else:
            print('Input:')
            print(YELLOW + '\n'.join(inputs[i]) + ENDC)
            print('Expected:')
            print(GREEN + '\n'.join(outputs[i]) + ENDC)

            if result.returncode != 0:
                print(RED + 'Runtime error' + ENDC)
                print(result.stderr)
            else:
                print(RED + 'Wrong answer on test case ' + str(i) + ENDC)
                print('Got:')
                print(RED + result.stdout.strip() + ENDC)
            
        
if __name__ == "__main__":
    main()