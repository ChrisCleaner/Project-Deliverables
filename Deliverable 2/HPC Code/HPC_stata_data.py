
# -*- coding: utf-8 -*-
"""
Created on 03.01.2022

@author: chris
"""
import threading
import time
import pandas as pd
from os import listdir
import regex as re
import fuzzyset
import os
import faulthandler
from sys import argv



#Segmentation Fault Handling
faulthandler.enable()
faulthandler.disable()
print(faulthandler.is_enabled())

stopword_list = ['i',
 'me',
 'my',
 'myself',
 'we',
 'our',
 'ours',
 'ourselves',
 'you',
 "you're",
 "you've",
 "you'll",
 "you'd",
 'your',
 'yours',
 'yourself',
 'yourselves',
 'he',
 'him',
 'his',
 'himself',
 'she',
 "she's",
 'her',
 'hers',
 'herself',
 'it',
 "it's",
 'its',
 'itself',
 'they',
 'them',
 'their',
 'theirs',
 'themselves',
 'what',
 'which',
 'who',
 'whom',
 'this',
 'that',
 "that'll",
 'these',
 'those',
 'am',
 'is',
 'are',
 'was',
 'were',
 'be',
 'been',
 'being',
 'have',
 'has',
 'had',
 'having',
 'do',
 'does',
 'did',
 'doing',
 'a',
 'an',
 'the',
 'and',
 'but',
 'if',
 'or',
 'because',
 'as',
 'until',
 'while',
 'of',
 'at',
 'by',
 'for',
 'with',
 'about',
 'against',
 'between',
 'into',
 'through',
 'during',
 'before',
 'after',
 'above',
 'below',
 'to',
 'from',
 'up',
 'down',
 'in',
 'out',
 'on',
 'off',
 'over',
 'under',
 'again',
 'further',
 'then',
 'once',
 'here',
 'there',
 'when',
 'where',
 'why',
 'how',
 'all',
 'any',
 'both',
 'each',
 'few',
 'more',
 'most',
 'other',
 'some',
 'such',
 'no',
 'nor',
 'not',
 'only',
 'own',
 'same',
 'so',
 'than',
 'too',
 'very',
 's',
 't',
 'can',
 'will',
 'just',
 'don',
 "don't",
 'should',
 "should've",
 'now',
 'd',
 'll',
 'm',
 'o',
 're',
 've',
 'y',
 'ain',
 'aren',
 "aren't",
 'couldn',
 "couldn't",
 'didn',
 "didn't",
 'doesn',
 "doesn't",
 'hadn',
 "hadn't",
 'hasn',
 "hasn't",
 'haven',
 "haven't",
 'isn',
 "isn't",
 'ma',
 'mightn',
 "mightn't",
 'mustn',
 "mustn't",
 'needn',
 "needn't",
 'shan',
 "shan't",
 'shouldn',
 "shouldn't",
 'wasn',
 "wasn't",
 'weren',
 "weren't",
 'won',
 "won't",
 'wouldn',
 "wouldn't"]

#possible to run local for debugging
RUN_LOCAL = False
USE_TEMP_MEM = True
ANSWERS = []



def clean_treaty_names(text):
    text = [ n.lower() for n in text.split() if n.lower() not in stopword_list]
    text = re.sub(r'\w*\d\w*', '', ' '.join(text)).strip() #remove mistranslations such as '-' to 'xe23xo0'; basically remove any words that have numbers in it
    text = re.sub(r'\w*\.\w*', '', text).strip()
    text = re.sub("(\\d|\\W)+"," ", text).strip() # remove special characters and digits
    
    text = re.sub("</?.*?>"," ", text) # remove tags
    text = re.sub('\(.\)| .\)', '', text) #remove a) and (b) mentions
    text = re.sub(r'\w*\d\w*', '', text).strip() #remove mistranslations such as '-' to 'xe23xo0'; basically remove any words that have numbers in it
    text = re.sub(r'[^A-Za-z ]', '', text) 
    
    return text


if RUN_LOCAL:
    #get the meta data - webscraped and saved as csv file
    df_meta_treaty = pd.read_csv('Meta_Data_Stata.csv')
    df_meta_treaty_decision = pd.read_csv('Meta Data Treaty Decisions.csv')
elif not USE_TEMP_MEM:
    df_meta_treaty = pd.read_csv('Meta_Data_Stata.csv')
    df_meta_treaty_decision = pd.read_csv('Meta Data Treaty Decisions.csv')
else:
    #get the meta data - webscraped and saved as csv file
    df_meta_treaty = pd.read_csv(os.environ['TMPDIR']+ '/input/meta_data/Meta_Data_Stata.csv')
    df_meta_treaty_decision = pd.read_csv(os.environ['TMPDIR']+ '/input/meta_data/Meta Data Treaty Decisions.csv')
    
#create list with all treaty names / These names in the list will be searched later
treaty_names = list(df_meta_treaty["treatyname"])
treaty_type = list(df_meta_treaty["agreement_type"])
#filter out any amendments
new_treaty_names = []
for name, type_ in zip(treaty_names, treaty_type):
    if type_ != "Amendment":
        new_treaty_names.append(name)
        
treaty_names = list(set(new_treaty_names))

##create list with all treaty names / These names in the list will be searched later
treaty_decision_names = list(set(list(df_meta_treaty_decision["Title"])))




#update treaty names | deletes certain words and numbers, to shorten treaty name length
new_treaty_names = []
for treaty in treaty_names:
    new_treaty_names.append(clean_treaty_names(treaty))
treaty_names_old = treaty_names
treaty_names = new_treaty_names.copy()

#update treaty decision names | deletes certain words and numbers, to shorten treaty name length
new_treaty_decision_names = []
for treaty in treaty_decision_names:
    new_treaty_decision_names.append(clean_treaty_names(treaty))
    
treaty_decision_names_old = treaty_decision_names 
treaty_decision_names = new_treaty_decision_names.copy()



def fuzzy_search_treaty_decision(treaty_decision_text, treaty_decision_name, treaty_names, step_size, added_words):
    
    global ANSWERS
    list_of_outcomes = []
    text = treaty_decision_text
    for treaty in treaty_names: 
        '''
        FUZZY SEARCH
        As fuzzysearch doesn't work well if the string length differ widely,
        the code loops over different overlaping parts of the text and saves the highest score
        '''

        high_score = 0
        high_score_line = ""
        name_len = len(treaty.split()) #see how long the treaty name is
        treaty_specific_step_size = (name_len + added_words) // step_size
        if treaty_specific_step_size == 0:
            treaty_specific_step_size = 1

        #use fuzzy search to see the match for the specific part of the text
        Search_Query = fuzzyset.FuzzySet()
        Search_Query.add(treaty)
        for num  in range(0, len(text) - 2 - name_len, treaty_specific_step_size): #get the length of the text and get a step size that is according to the name length



            
            outcome = Search_Query.get(" ".join(text[num:num + name_len + added_words]))


            if outcome != None: #check if the match is None (None will cause error)
                if outcome[0][0] > high_score: #check if the current score is larger than the highest score
                    high_score = outcome[0][0] #update highscore
                    high_score_line = " ".join(text[num:num + name_len + added_words])
        #uncomment line below, to adjust for treaty length
        #high_score = adjust_to_name_length(treaty, high_score)
        list_of_outcomes.append((high_score, high_score_line))
    ANSWERS.append((treaty_decision_name, list_of_outcomes))
    
    
def fuzzy_search_final(batch_folder, step_size = 4, added_words = 2, search_treaty_names = True, search_treaty_decision_names = False):
    global RUN_LOCAL
    global ANSWERS
    #use cfuzzyset for 15% performance increase
    #check documentation 
    
    start_time = time.time()
    #add df for saving data

    df_treaties = pd.DataFrame(columns = treaty_names_old)
    df_treaty_decisions = pd.DataFrame(columns = treaty_decision_names_old)
    list_of_treaty_decision_texts = []
    list_of_treaty_decision_names = []
    
    if RUN_LOCAL:
        list_of_files = listdir('Decisions/Split Data/' + batch_folder) #get all files
    elif not USE_TEMP_MEM:
        list_of_files = listdir(os.environ['HOME'] + '/' + batch_folder)
    else:
        list_of_files = listdir(os.environ["TMPDIR"] + f'/input/{str(argv[2])}/' + batch_folder) #get all files

    if search_treaty_names:
        threads = []
        for filename in list_of_files: #go through files in subfolder
    
            if filename == "HPC_stata_data.py":
                continue
            if filename[-3:] != "txt":
                continue
    
    
            if RUN_LOCAL:
                with open('Decisions/Split Data/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            elif not USE_TEMP_MEM:
                with open(os.environ["HOME"] + '/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            else:
                with open(os.environ["TMPDIR"] + f'/input/{str(argv[2])}/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            
            list_of_treaty_decision_texts.append(document_text)
            list_of_treaty_decision_names.append(filename[:-3])
            
        
            """
            Clean the text, should be done in the jupyter notebook, saves computing power
            """
            text = " ".join(document_text)
            text = clean_treaty_names(text)
            #add outcomes to df, save df
            
            ANSWERS = []
        
            #add all the texts and names to a list, which will be done parallel in the next step
            t = threading.Thread(target = fuzzy_search_treaty_decision, args = (text.split(), filename[:-4], treaty_names, step_size, added_words))
            threads.append(t)

            
        for t in threads:
            t.start()
        for t in threads:
            t.join()
            
        
        #returns a list of touples with treaty decision name, and a list of the correct values
        for answer in ANSWERS:    
            df_treaties.loc[answer[0]] = answer[1]
        
        if RUN_LOCAL:
            pass
        elif not USE_TEMP_MEM:
            df_treaties.to_csv(os.environ['HOME']+ f"/output/Fuzzy Search Treaty Names {str(argv[2])} Outcomes {batch_folder}.csv")
        else:
            df_treaties.to_csv(os.environ['TMPDIR']+ f"/output/Fuzzy Search Treaty Names Outcomes {str(argv[2])} {batch_folder}.csv")

        print(f'time FuzzySearch Treaty Names for Subfolder  {batch_folder} ', time.time() - start_time)
        with open(os.environ["TMPDIR"] + "/output/Document_texts.txt", "w", encoding = 'utf-8') as text_file:
            text_file.write(" ".join(document_text))
#        with open(os.environ["TMPDIR"] + "/output/Document_texts2.txt", "w", encoding = 'utf-8') as text_file:
#            text_file.write(filename + document_text)
#        with open(os.environ["TMPDIR"] + "/output/Document_texts3.txt", "w", encoding = 'utf-8') as text_file:
#            text_file.write(list_of_treaty_decision_texts)
        
    
    """
    CURRENTLY NOT IN USE
    """
    if search_treaty_decision_names:
         for filename in list_of_files: #go through files in subfolder

            if filename == "HPC_stata_data.py":
                continue
    
    
            if RUN_LOCAL:
                with open('Decisions/Split Data/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            elif not USE_TEMP_MEM:
                with open(os.environ["HOME"] + '/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            else:
                with open(os.environ["TMPDIR"] + f'/input/{str(argv[2])}/' + batch_folder + '/' + filename, encoding = "utf8") as f:
                    document_text = f.readlines()
            
            list_of_treaty_decision_texts.append(document_text)
            list_of_treaty_decision_names.append(filename[:-3])
            
        
            ANSWERS = []
            #add all the texts and names to a list, which will be done parallel in the next step
            t = threading.Thread(target = fuzzy_search_treaty_decision, args = (document_text[0], filename[:-3], treaty_names, step_size, added_words))
            t.start()
            t.join()
                            


           
            #returns a list of touples with treaty decision name, and a list of the correct values
            for answer in ANSWERS:    
                df_treaty_decisions.loc[answer[0][:-3]] = answer[1]
                
            if RUN_LOCAL:
                pass
            elif not USE_TEMP_MEM:
                df_treaty_decisions.to_csv(os.environ['HOME']+ f"/output/Fuzzy Search Treaty Decision Name {str(argv[2])}s Outcomes  {batch_folder}.csv")
            else:
                df_treaty_decisions.to_csv(os.environ['TMPDIR']+ f"/output/Fuzzy Search Treaty Decision Names {str(argv[2])} Outcomes  {batch_folder}.csv")
    
            print(f'time FuzzySearch Treaty Names for  {batch_folder}', time.time() - start_time)
    

    
    return 0 

fuzzy_search_final('Batch ' + str(argv[1]))
    


