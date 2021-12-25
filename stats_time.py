import json
import glob
import csv
import re
import datetime
from dateutil import relativedelta
from bs4 import BeautifulSoup

FLASH_HINTS = [".swf", "<embed", "<video", "youtube.com", "youtu.be", ".mp4", "fastswf"]
BBC_TAGS = [r"\[\/?(i|b|u|s|size|spoiler|color|background|url)(=.+?)?\]", r"\[img\](.+?)\[\/img\]"]
FIRST_DATE = datetime.datetime.utcfromtimestamp(1265257812)

private_advs = 0
unique_words_first = {}
unique_words_other = {}
title_wordcount = {
    "stuck": 0,
    "bent": 0,
    "bound": 0,
    "home": 0,
    "house": 0,
    "hive": 0,
    "trapped": 0,
    "locked": 0,
    "room": 0,
    "^2": 0,
    "swap": 0,
    "haunt": 0,
    "switch": 0
}
pannels_flash_total = {}
pannels_reg_total = {}
pannels_wordcount_total = {}
date_flash_total     = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # Feb-Oct 2010, Oct 2010-Feb 2011, ...
date_reg_total       = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
date_wordcount_total = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
date_comicreation    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for filename in glob.glob("*.txt"): 

    with open(filename, mode="r", encoding="utf-8") as f:
        print(filename)
        contents = json.load(f)

        if not "translation" in contents["t"]:
            private_advs += ("l" in contents)

            # Count of words in title (stuck, hive...)
            for key in title_wordcount:
                if key in contents["n"].lower(): title_wordcount[key] += 1

            comic_atual_dist = int(contents["i"] / 1000)
            if not comic_atual_dist in pannels_flash_total:
                pannels_flash_total[comic_atual_dist] = 0
                pannels_reg_total[comic_atual_dist] = 0
                pannels_wordcount_total[comic_atual_dist] = 0

            date_diff = relativedelta.relativedelta(datetime.datetime.utcfromtimestamp(contents["d"] / 1000), FIRST_DATE)
            months_diff = (date_diff.years * 2) + int(date_diff.months / 6)
            date_comicreation[months_diff] += 1

            # Iterate through each page
            for page in contents["p"]:
                date_diff = relativedelta.relativedelta(datetime.datetime.utcfromtimestamp(page["d"] / 1000), FIRST_DATE)
                months_diff = (date_diff.years * 2) + int(date_diff.months / 6)
                
                if ([ele for ele in FLASH_HINTS if (ele in page["b"])]):
                    pannels_flash_total[comic_atual_dist] += 1
                    date_flash_total[months_diff] += 1
                else:
                    pannels_reg_total[comic_atual_dist] += 1
                    date_reg_total[months_diff] += 1

                page_text = re.sub(BBC_TAGS[0], "",(re.sub(BBC_TAGS[1], "", page["b"]))).replace("<!", "")
                words = BeautifulSoup(page_text, "html.parser").text.lower().split()
                # Date distribution 
                pannels_wordcount_total[comic_atual_dist] += len(words)
                date_wordcount_total[months_diff] += len(words)
                
                if page["n"] != [] and page["n"][0] == 2: # Most used words of the first pages
                    for word in words:
                        word = re.sub(r"[^\w]", "", word)
                        if word == "he" or (len(word) >= 3 and len(word) < 27):
                            if not word in unique_words_first: unique_words_first[word] = 0
                            unique_words_first[word] += 1
                else: # Most used word of other pages
                    for word in words:
                        word = re.sub(r"[^\w]", "", word)
                        if len(word) >= 3 and len(word) < 27:
                            if not word in unique_words_other: unique_words_other[word] = 0
                            unique_words_other[word] += 1

output_text = """Private adventures:
%s
Specific words in titles:
%s
Word count, 500s adventures:
%s
Flashes count, 500s adventures:
%s
Reg pannel count, 500s adventures:
%s
New adv creation time, each 6 months:
%s
Word count, each 6 months:
%s
Flashes count, each 6 months:
%s
Reg pannel count, each 6 months:
%s""" % (str(private_advs), str(title_wordcount), str(pannels_wordcount_total), str(pannels_flash_total), str(pannels_reg_total), str(date_comicreation), str(date_wordcount_total), str(date_flash_total), str(date_reg_total))

print("Unique words first page:")
print(unique_words_first)
print("Unique words other pages:")
print(unique_words_other)
print(output_text)

with open("0stats", "w", encoding="utf-8") as f:
    f.write(output_text)
    f.close()

with open("0pagescount_first.csv", "w", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, unique_words_first.keys())
    writer.writeheader()
    writer.writerow(unique_words_first)
with open("0pagescount_other.csv", "w", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, unique_words_other.keys())
    writer.writeheader()
    writer.writerow(unique_words_other)