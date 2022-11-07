import PyPDF2
import textract
import pdfplumber
import pdfminer
import csv
import re

def get_text():
   # PDF_read = textract.process('C:/Users/coolk/GithubProjects/PDFReaders/SamplePDF2.pdf')
    with pdfplumber.open("SamplePDF2.PDF") as temp:
        pages = temp.pages
        first_page = pages[0].extract_text()
    print(first_page)

# Return a list of strings representing possible variations of a given word
def get_variations(word):
    lst = []
    suffix = [',', '.', '!', '?', ' ']
    # lst containing word, Word, WORD
    forms = [word, word.capitalize(), word.upper()]
    # Add each suffix to each form of the word
    for f in forms:
        for s in suffix:
            lst.append(f + s)
    return lst


def scan_pdf(key_words):
    row = []
    rows = []
    sentence = []
    sentences = []
    blank = re.compile('[^\s]')
    # Hashmap will contain k v pairs that are ("word", [pg, (i, j), (k, l)])
    # word, pg, doc sentence number, word number in sentence
    # Each key will map to a list of (i, j)s of where in the page that word occurs
    word_map = {}
    # -- pdf = open('mf_guide_full.pdf', 'rb')
    # -- reader = PyPDF2.PdfFileReader(pdf)
    with pdfplumber.open("mf_guide_full.pdf") as temp:
        # Load each page thats been parsed from the pdf
        for pg in range(1, len(temp.pages) + 1):
            page = temp.pages[pg-1].extract_text()
            # -- content = page.extractText()
            line = []
            words_on_page = []
            # Split up lines based on newline character or period
            for ch in page:
                if ch == '\n':
                    words_on_page.append(line)
                    line = []
                    continue
                line.append(ch)
            # Split up words within each line based on ' ' character
            word = ""
            word_count = 0
            for i in range(0, len(words_on_page)):
                for j in range(0, len(words_on_page[i])):
                    # Split words on blank space
                    if words_on_page[i][j] == ' ':
                        sentence.append(word)
                        # If word exists in map, update the coordinates list to store the next occurrence location
                        if word in word_map.keys():
                            # changed to store which sentence word appears in relation to entire doc instead of local page
                            word_map.get(word).append([pg, len(sentences), word_count])
                        else:
                            word_map[word] = [[pg, i, word_count]]
                        word = ""
                        word_count += 1
                        continue
                    word += words_on_page[i][j]
                # Ensure sentence isnt a blank line
                if blank.match("".join(sentence)):
                    sentences.append(sentence)
                sentence = []
                word_count = 0
    # Search Words
    for wd in key_words:
        # Search if any variations of wd appear in word_map
        wd_variations = get_variations(wd)
        total_occurrences = 0
        for wd_var in wd_variations:
            if wd_var in word_map.keys():
                total_occurrences += len(word_map[wd_var])
                # Record neighboring sentences for each occurrence of the word
                for ocr in word_map[wd_var]:
                    row.append(
                        "Page " + str(ocr[0]) + " at doc sentence # " + str(ocr[1] + 1) + " pg word # " + str(ocr[2] + 1))
                    # Leading sentence
                    if ocr[1] > 0:
                        row.append("Previous Sentence: " + " ".join(sentences[ocr[1] - 1]))
                    # Current sentence
                    row.append("Contained In: " + " ".join(sentences[ocr[1]]))
                    # Following sentence
                    if ocr[1] < len(sentences) - 1:
                        row.append("Following Sentence:  " + " ".join(sentences[ocr[1] + 1]))
                    # Add space between words
                    rows.append(row)
                    # Reset row for storing info on the next occurrence
                    row = []

        # Check if word DNE
        if total_occurrences == 0:
            rows.append([str(wd) + " does not exist "])
            row = []
            continue
        row.append(str(wd) + " appears " + str(total_occurrences) + " times in the doc")
        # Insert report on top of all occurrences on csv form
        if len(rows)-total_occurrences >= 0:
            rows.insert(len(rows)-total_occurrences, row)
        # rows.append(row)
        rows.append([])
        row = []
    # pdf.close()
    # Export to CSV
    with open("Search_Results.csv", "w", encoding="utf-8", newline='') as my_csv:
        csvWriter = csv.writer(my_csv)
        csvWriter.writerows(rows)
        my_csv.close


# Import keywords text file into list of strings
txt_file = open("keywords.txt", "r")
content = txt_file.read()
parsed_txt = content.split("\n")
key_words = []
for ln in parsed_txt:
    key_words.append(ln)

#get_text()
scan_pdf(key_words)
