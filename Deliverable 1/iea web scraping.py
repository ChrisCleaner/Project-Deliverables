# -*- coding: utf-8 -*-
"""
Created on Monday 03-01-2022

@author:
        Christoph Krüger
        christoph.kruger@yahoo.com
        Computational Science MSc student at University of Amsterdam

Add iea_files.txt with the id's to your current directory.
Create another folder called "data_python" in your current directory to save the data there
If you would like to change the folder name to something else than data_python, you also have to change the name in line 58 & 67
"""
from urllib import request
import regex as re
import os
 
def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(clean, '', text)

def remove_multiple_spaces(text):
    return re.sub(" +", " ", text)

def remove_eols(text):
    return text.replace("\n \n", "")

def remove_all_before_title(text):
    """ removes everything before the title (html tags are needed to locate title) """
    title_location = text.find('<h1 class="title"')
    return text[title_location:]


def open_website(url_):
    #open main website
    url=url_
    response = request.urlopen(url, timeout=10).read() #if it takes longer than 10 seconds to load it will time out --> to avoid stalling the download indefinitely 
    return response

#load file
with open("Treaty Texts and Data/IEA/iea_files.txt", "r") as text_file:
    id_list = text_file.read()
  
#split string to list
id_list = id_list.split("\n")


#counters for later analysis
found_counter = 0
not_found_counter = 0
not_found_ids = []

#go over id's
for num, id_ in enumerate(id_list):
    """
    To Skip Files that are already downloaded; uncomment if function to redownload data
    """
    #skip if it's already in list
    if f"{id_}.txt" in os.listdir("Treaty Texts and Data/IEA/Treaty Texts/"):
        continue
    
    try:
        site_content = str(open_website("https://iea.uoregon.edu/treaty-text/" + id_).decode("utf-8")) #download website content & decode it to regular string
        site_content = remove_all_before_title(site_content) #remove unneccesary text from the beginning
        site_content = remove_html_tags(site_content) #remove html tags
        site_content = remove_multiple_spaces(site_content) #remove multiple spaces
        site_content = remove_eols(site_content) #remove end of line tags "\n" - not working properly
        with open(f"Treaty Texts and Data/IEA/Treaty Texts/{id_}.txt", "w", encoding = "utf-8") as f: #save text as txt
            f.write(site_content)
            
        found_counter += 1
        
        
    except:           #if website cannot be loaded, add data to statistics       
        print("Not Found: ", id_)
        not_found_counter += 1
        not_found_ids.append(id_)
        

        
#print statistics
print("Found: ", found_counter, " articles.")
print("Not Found: ", not_found_counter, " articles.")
print(not_found_ids)
        
