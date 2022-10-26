import PyPDF2
import csv
import re

def scan_pdf(key_words):
    col = []
    rows = []
    sentance = []
    sentances = []
    blank = re.compile('[^\s]')
    #Hashmap will contain k v pairs that are ("word", [pg, (i, j), (k, l)])
    #Each key will map to a list of (i, j)s of where in the page that word occurs
    word_map = {}
    pdf = open('SamplePDF2.pdf', 'rb')
    reader = PyPDF2.PdfFileReader(pdf)
    #Load each page thats been parsed from the pdf
    for pg in range(1, reader.numPages+1):
        page = reader.getPage(pg-1)
        content = page.extractText()
        line = []
        words_on_page = []
        #Split up lines based on newline character
        for ch in content:
            if ch == ('\n'):
                words_on_page.append(line)
                line = []
                continue
            line.append(ch)
        #Split up words within each line based on ' ' character
        word = ""
        word_count = 0
        for i in range(0, len(words_on_page)):
            for j in range (0, len(words_on_page[i])):
                #Split words on blank space
                if words_on_page[i][j] == ' ':
                   sentance.append(word)
                   #If word exists in map, update the corrdinates list to store the next occurance location
                   if word in word_map.keys():
                       #changed to store which sentance word appears in relation to entire doc instead of local page
                       word_map.get(word).append([pg, len(sentances), word_count])
                   else:
                       word_map[word] = [[pg, i, word_count]]
                   word = ""
                   word_count += 1
                   continue
                word += words_on_page[i][j]
            #Ensure sentance isnt a blank line
            if blank.match("".join(sentance)):
                sentances.append(sentance)
            sentance = []
            word_count = 0
    #Search Words
    for wd in key_words:
        if wd in word_map.keys():
            col.append(str(wd) + " appears " + str(len(word_map[wd])) + " times in the doc at the following locations")
            rows.append(col)
            col = []
            #Record neighboring sentances for each occurance of the word
            for ocr in word_map[wd]:
                col.append("Page " + str(ocr[0]) + " at doc sentance # " + str(ocr[1]+1) + " pg word # " + str(ocr[2]+1))
                #Leading sentance
                if(ocr[1] > 0):
                    col.append("Previous Sentance: " + " ".join(sentances[ocr[1] - 1]))
                #Current sentance  
                col.append("Contained In: " + " ".join(sentances[ocr[1]]))                 
                #Following sentance
                if(ocr[1] < len(sentances)-1):
                    col.append("Following Sentance:  " + " ".join(sentances[ocr[1] + 1]))
                #Add space between words
                rows.append(col)
                #Reset col for storing info on the next occurance
                col = []
        else:
            col.append(str(wd) + " does not exist ")
    pdf.close()
    #Export to CSV
    with open("Search_Results.csv", "w", encoding="utf-8") as my_csv:
        csvWriter = csv.writer(my_csv)
        csvWriter.writerows(rows)
        my_csv.close

key_words = ["test", "this", "notpresent"]
scan_pdf(key_words)
