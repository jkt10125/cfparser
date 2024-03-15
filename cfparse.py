#!/usr/bin/env python3

# input: python3 cfparse.py <contest_id>
# output: creates a folder with the name contest_id and saves the input and output of all problems in the folder

import requests, sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup not found. Installing...")
    try:
        import pip
        pip.main(['install', 'beautifulsoup4'])
    except:
        print("Error installing BeautifulSoup. Please install it manually.")
        sys.exit(1)

def get_problem_links(contest_id):
    url = "https://codeforces.com/contest/" + contest_id
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    problems_table = soup.find('table', class_ = 'problems')
    if problems_table:
        problem_links = ["https://codeforces.com" + td.find('a')['href'] for td in problems_table.find_all('td', class_ = 'id')]
        return problem_links
    else:
        print("Couldn't find problems. Check if the website structure has changed.")
        return []

def extract_text(x, content):
    for tag_line in content:
        text = tag_line.find('pre').get_text(separator = '\n')
        x[-1].extend(text.strip().split('\n'))
        x.append([])

def get_input_output(soup):
    inputs = soup.find_all('div', class_ = 'input')
    outputs = soup.find_all('div', class_ = 'output')
    input_list = [[]]
    output_list = [[]]

    if not inputs or not inputs[0].find_all('div', class_ = 'test-example-line'):
        extract_text(input_list, inputs)
    else:
        for input_tag_line in inputs:
            for line in input_tag_line.find_all('div', class_ = 'test-example-line'):
                input_list[-1].append(line.text.strip())
            input_list.append([])

    extract_text(output_list, outputs)

    return input_list[0:-1], output_list[0:-1]

def save_input_output(contest_id):
    with open(contest_id + '.txt', 'w') as ff:
        problem_links = get_problem_links(contest_id)
        for i in range(len(problem_links)):
            problem_idx = problem_links[i].split('/')[-1]
            soup = BeautifulSoup(requests.get(problem_links[i]).content, 'html.parser')
            input, output = get_input_output(soup)

            if len(input) != len(output):
                print("Inconsistent input and output for problem " + problem_idx)
                continue

            if len(input) == 0:
                print("Failed to fetch input and output for problem " + problem_idx)
                continue

            ff.write(problem_idx + '\n')
            print("Saving problem " + problem_idx)

            for j, (inp, out) in enumerate(zip(input, output)):
                ff.write(f"{j} : {'€ '.join(inp)} : {'€ '.join(out)}\n")

def main():
    contest_id = sys.argv[1]
    save_input_output(contest_id)

if __name__ == "__main__":
    main()
