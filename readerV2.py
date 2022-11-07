import PyPDF2
import csv
import re


# Return word frequency and occurrence without neighboring sentences


# Return a list of strings representing possible variations of a given word
def get_variations(key_words):
    keywords_map = {}
    lst = []
    suffix = [',', '.', '!', '?', ' ']
    for w in key_words:
        lst.append(w)
        # lst containing the following 3 forms of a word [word, Word, WORD]
        forms = [w, w.capitalize(), w.upper()]
        # Add each suffix to each form of the word
        for f in forms:
            for s in suffix:
                lst.append(f + s)
        keywords_map[w] = lst
        lst = []
    return keywords_map


def scan_pdf(keywords_map, keywords_data):
    blank = re.compile('[^\s]')
    word_map = {}
    pdf = open('mf_guide_full.pdf', 'rb')
    reader = PyPDF2.PdfFileReader(pdf)
    # Load each page thats been parsed from the pdf
    word = ""
    for pg in range(1, reader.numPages + 1):
        i = 0
        for ch in reader.getPage(pg - 1).extract_text():
            # Check end of word
            if (ch == ' '):
                i += 1
                # Check for word then reset variable
                for k in keywords_map.keys():
                    if word in keywords_map.get(k):
                        keywords_data[k].append("page# " + str(pg) + " word number " + str(i))

                word = ""
                continue
            word += ch

    rows = []
    for k in keywords_data.keys():
        total = str(k) + " appears " + str(len(keywords_data.get(k))) + " times"
        rows.append([total])
        for l in keywords_data.get(k):
            rows.append([l])
        rows.append([])

    #output data
    with open("Search_Results.csv", "w", encoding="utf-8", newline='') as my_csv:
        csvWriter = csv.writer(my_csv)
        csvWriter.writerows(rows)
        my_csv.close


# Import keywords text file into list of strings
txt_file = open("keywords.txt", "r")
content = txt_file.read()
parsed_txt = content.split("\n")
key_words = []
keywords_data = {}
for ln in parsed_txt:
    key_words.append(ln)
    keywords_data[ln] = []

keywords_map = get_variations(key_words)
scan_pdf(keywords_map, keywords_data)
