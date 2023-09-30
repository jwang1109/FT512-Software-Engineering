import sys


def kwic():
    #1.Read data
    words_to_ignore = []
    titles = []
    sig = 0 # When sig = 0, it means these lines are words to ignore. When  sig = 1, it means lines are titles. A string of "::" will change the state of sig
    for line in sys.stdin:
        line = line.strip()
        if line == "::":
            sig = 1
            continue
        if sig != 1:
            words_to_ignore.append(line.lower())
        else:
            titles.append(line.lower())
    #2.process the result, capitalize each time we meet key words
    processed_titles = {}#the key is a list of words from one title  and the value is index of one certain keyword
    if sig == 0:
        raise ValueError("No :: symbol founded")
        
    for title in titles:
        l = title.split(" ")
        for index,word in enumerate(l):
            if word not in words_to_ignore:
                l_c = l.copy()
                l_c[index] = word.upper()
                processed_titles[" ".join(l_c)] = index

    #3.sort and print the result
    sorted_titles = sorted(processed_titles.items(),key = lambda x:x[0].split()[x[1]])# the lambda stuff is just to find what is to be compared. It is the value of the dictionary(aka:x[1]) of a list of words from a title(aka:x[0].split())
    result = []
    for t in sorted_titles:
        sys.stdout.write(t[0]+"\n")
        result.append(t[0])
    return result
