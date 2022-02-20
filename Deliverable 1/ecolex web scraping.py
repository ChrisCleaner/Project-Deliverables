# -*- coding: utf-8 -*-
"""
DOWNLOAD ALL PDF TEATY DECISIONS FROM ECOLEX
Created on Tue Sep  7 9:07:59 2021

@author: chris
"""




from urllib import request
import requests
import re
import os
from pathlib import Path
from fuzzyset import FuzzySet

#to bridge an error when loading the websites
import ssl
ssl._create_default_https_context = ssl._create_unverified_context



DOWNLOAD_TREATIES = True
DOWNLOAD_TREATY_DECISIONS =  False

PAGE_START_TREATY_DECISIONS = 0
PAGE_STOP_TREATY_DECISIONS = 667 #out of 667

PAGE_START_TREATIES = 30
PAGE_STOP_TREATIES = 110 #out of 110


list_of_failed_downloads = []
counter_failed_downloads = 0


def open_website(url_):
    #open main website

    url=url_
    response = request.urlopen(url).read()
    return response



def get_pdf_info(website_content):
    
    """
    Returns List of all the html information from the website on the pdf locations
    """
    web_con = str(website_content) #turn to string
    pdf_information = []
    for _ in range(web_con.count('<h3 class=\"search-result-title\">')): #loop over all the headlines
        posi = web_con.find('<h3 class=\"search-result-title\">') #find the right spot on the side
        web_con = web_con[posi:] #cut beginning until string
        end_of_h3 = web_con.find('</h3>') #find end of string
        pdf_info = web_con[0:end_of_h3] #cut the string
        pdf_information.append(pdf_info)
        web_con = web_con[end_of_h3:]
        
    return pdf_information
    
    
def download_layer_two(website, download_folder, date):
    """
    Receives Website to download from and downloads it
    """
    
    #find pdf link
    website = str(website)
    find_pdf_link = website.find("<dt>Full text</dt>")
    
    
    
    
    #check if the pdf is actually there
    if find_pdf_link != -1: 
        find_pdf_link_start = website[find_pdf_link:].find('\"') + find_pdf_link
        find_pdf_link_end = website[find_pdf_link_start +1:].find('\"')
        pdf_link = website[find_pdf_link_start:find_pdf_link_end + find_pdf_link_start +1] #extract pdf link
        
        
        #check if possible several pdf-links are there (different languages)
        end_link = website[find_pdf_link:].find('</dl>')
        if end_link != -1:
            occurences = website[find_pdf_link:end_link + find_pdf_link].count('<dd>') #check if several links are offered
            
            
            if occurences > 1:
                website_content = website[find_pdf_link:]
                similarity_eng = {}
                for num in range(occurences):
                    #get link
                    
                    link_start = website_content.find('\"') + 1 #plus one to exclude first hash
                    link_end = website_content[link_start:].find('\"')
                    pdf_link = website_content[link_start:link_end + link_start]
                    website_content = website_content[website_content.find(r'</dd>')+4:] #plus four, so it doesn't get stuck on itself
                    
                   
                    
                    
                    
                    #check similarity to english
                    Search_Query = FuzzySet()
                    Search_Query.add('english')
                    outcome = Search_Query.get(pdf_link[-20:]) #only take the end, as it is the place where the languages are stored
                    
                    if outcome is None:
                        similarity_eng[(num*0.00001)] = pdf_link
                    else:    
                        similarity_eng[round(outcome[0][0], 4) + (num*0.00001)] = pdf_link
                        
                #find largest similarity to english
                larg_sim = max(k for k, v in similarity_eng.items())
                pdf_link = 'h' + similarity_eng[larg_sim]
                
                
                    
        
        #get title of the pdf
        begin_title = website.find("<h1>")
        end_title = website.find("</h1>")
        title = website[begin_title + 4 :end_title]
        #strip any possible html tags and non-alphabetic characters
        clean = re.compile('<.*?>')
        title = re.sub(clean, '', title)
        #title = title.replace("\'","").replace("\\","").replace("/","").replace("\"",'') #otherwise it cannot be saved due to name issues
        title = re.sub('[^0-9,^A-Z,^a-z, ]','', title)
        date = re.sub('[^0-9,^A-Z,^a-z, ]','', date)
        full_title = title
        title = date + " " + title
        if len(title) > 120: title = title[0:120] #due to apparent maximum of name length a pdf can have
        #check if it is pdf or docx
        if pdf_link[-3:] == 'pdf':
            save_link = os.path.join("Downloads/", download_folder + title + ".pdf")
        elif pdf_link[-3:] == 'doc':
            save_link = os.path.join("Downloads/", download_folder + title + ".doc")
        else:
            save_link = os.path.join("Downloads/", download_folder + title + ".docx")
        
        #download pdf with correct title
        filename = Path(save_link)
        response = requests.get(pdf_link[1:])
        filename.write_bytes(response.content)

        return 1, title, full_title
    
    #get title of the treaty for the meta data
    begin_title = website.find("<h1>")
    end_title = website.find("</h1>")
    title = website[begin_title + 4 :end_title]
    print(title)
    title = re.sub('[^0-9,^A-Z,^a-z, ]','',title)
    full_title = title
    if len(title) > 120: title = title[0:120] #due to apparent maximum of name length a pdf can have
    save_link = os.path.join("Downloads/", title + ".pdf")
    return 0, title, full_title




def download_pdfs(liste):
    """
    Receives list of all the pdf information, downloads the pdfs
    """
    global list_of_failed_downloads, counter_failed_downloads
    doc_counter = 0
    
    for info in pdf_inf:
        link_posi = info.find('<a href=\"')
        info = info[link_posi+9:] #start after the href
        end_pos = info.find('\"') #find end of link
        link = "https://www.ecolex.org" + info[0:end_pos] #add address to the site 
        
        #download meta data
        web_site = request.urlopen(link).read()
        new_meta_data = download_layer_two_meta(web_site)
        date = new_meta_data["Date"]
        
        #based on meta data determine download folder
        if new_meta_data["Document type"].find("Resolutio") != -1:
            download_folder = "Resolutions/"
        elif  new_meta_data["Document type"].find("Decisio") != -1:
            download_folder = "Decisions/"
        elif new_meta_data["Document type"].find("Official Document") != -1:
            download_folder = "Official Documents/"
        elif new_meta_data["Document type"].find("Recommendatio") != -1:
            download_folder = "Recommendations/"
        elif new_meta_data["Document type"].find("Bilateral") != -1:
            download_folder = "Bilateral Agreements/"
        elif new_meta_data["Document type"].find("Multilateral") != -1:
            download_folder = "Multilateral Agreements/"
        else:
            download_folder = "Other/"
        
        #actually download pdf from the website
        try:
            add, title_of_treaty, full_title = download_layer_two(web_site, download_folder, date) #download and return if one pdf was downloaded (1) or none (0); returns two titles, as one has to be shortened to save as pdf
            doc_counter += add
        except:
            
            
            
            counter_failed_downloads += 1
            #get title of the pdf
            web_site = str(web_site)
            begin_title = web_site.find("<title>")
            end_title = web_site.find("</title>")
            title_of_treaty = "No Text " + web_site[begin_title + 4 :end_title]
            #strip any possible html tags and non-alphabetic characters
            clean = re.compile('<.*?>')
            title = re.sub(clean, '', title_of_treaty)
            #title = title.replace("\'","").replace("\\","").replace("/","").replace("\"",'') #otherwise it cannot be saved due to name issues
            title = re.sub('[^0-9,^A-Z,^a-z, ]','',title)
            full_title = title
            if len(title) > 120: title = title[:120] #shorten name, if saving name is too long
            title_of_treaty = title
            list_of_failed_downloads.append(title_of_treaty)
            print(f'\n \n DOWNLOAD ATTEMPTED FAILED of {title_of_treaty} \n \n')#
            add = 0
        
        #write meta data
        new_meta_data["Title"] = full_title #add title
        new_meta_data["Filename"] = title_of_treaty
        file = open("Downloads/Meta Data Treaty Decisions.txt", "a") #a for append, w for overwrite file
        file.write(str(new_meta_data) + "\n")
        file.close()
        
        #write abstract as treaty decisions text if available
        if ('Abstract' in new_meta_data) and (add == 0):
            #strip html tags
            clean = re.compile('<.*?>')
            text = re.sub(clean, '', str(new_meta_data['Abstract']))
            
            with open(f"Downloads/{download_folder}/{date + ' ' + title_of_treaty}.txt", "w", encoding='utf-8') as f:
                f.write(text)
        
        
    return doc_counter #to assess how many documents were downloaded
        
        
        


def download_layer_two_meta(website):
    """
    Gathers meta data and returns it as a dict
    """
    dict_of_data= {}
    website = str(website)
    meta_data_names = ["Document type", "Reference Number", "Date", "Source", "Status", "Subject", "Meeting", "Treaty","Website", 'Abstract']
    
    for data in meta_data_names:
        find_data = website.find(f"<dt>{data}</dt>")
  
         
        
        if find_data != -1: #check if this data exists for that treaty  decision
            begin_data = website[find_data:].find("<dd>")
            end_data = website[find_data:].find("</dd>")
            extract_data = website[find_data + begin_data + 4:end_data + find_data] #extract the data in between
            
            dict_of_data[data] = extract_data #add to dict
            
    
       
        
    

    #delete hyperlinks from the dict               
    for data_type in dict_of_data:
        dict_of_data[data_type] = re.sub(r'(<.*?>)', ' ', dict_of_data[data_type])
        dict_of_data[data_type] = dict_of_data[data_type].strip("\\n        ") #and new lines 
            
    return dict_of_data



def download_treaties(html_text):
    """
    Receives list of all the pdf information, downloads the pdfs
    """
    doc_counter = 0
    global list_of_failed_downloads, counter_failed_downloads
    
    for info in html_text:
        link_posi = info.find('<a href=\"')
        info = info[link_posi+9:] #start after the href
        end_pos = info.find('\"') #find end of link
        link = "https://www.ecolex.org" + info[0:end_pos] #add address to the site 
        
        #actually download pdf from the website
        web_site = request.urlopen(link).read()
        try:
            #download meta data
            new_meta_data = download_meta_data_treaties(web_site)
            date = new_meta_data["Date"]
            add, title_of_treaty, full_title = download_treaty(web_site, date) #download and return if one pdf was downloaded (1) or none (0) 
            doc_counter += add
        except:
            
            
            
            #get title of the pdf
            counter_failed_downloads += 1
            web_site = str(web_site)
            begin_title = web_site.find("<title>")
            end_title = web_site.find("</title>")
            title_of_treaty = web_site[begin_title + 4 :end_title]
            #strip any possible html tags and non-alphabetic characters
            clean = re.compile('<.*?>')
            title = re.sub(clean, '', title_of_treaty)
            full_title = title
            list_of_failed_downloads.append(title_of_treaty)
            print(f'\n \n DOWNLOAD ATTEMPTED FAILED of {title_of_treaty} \n \n')
            
        
        #download meta data
        new_meta_data = download_meta_data_treaties(web_site)
        new_meta_data["Title"] = full_title #add title
        file = open("Downloads/Meta Data Treaties.txt", "a") #a for append, w for overwrite file
        file.write(str(new_meta_data) + "\n")
        file.close()
        
        
    return doc_counter #to assess how many documents were downloaded


def download_treaty(website, date):
    """
    Receives Website to download from and downloads it
    """
    
    #find pdf link
    website = str(website)
    find_pdf_link = website.find("<dt>Full text</dt>")
    
    #download meta data
    
    
    #check if the pdf is actually there
    if find_pdf_link != -1: 
        find_pdf_link_start = website[find_pdf_link:].find('\"') + find_pdf_link
        find_pdf_link_end = website[find_pdf_link_start +1:].find('\"')
        pdf_link = website[find_pdf_link_start:find_pdf_link_end + find_pdf_link_start +1] #extract pdf link
        
        #get title of the pdf
        begin_title = website.find("<h1>")
        end_title = website.find("</h1>")
        title = website[begin_title + 4 :end_title]
        print(title)
        title = re.sub('[^0-9,^A-Z,^a-z, ]','',title)
        full_title = title
        date = re.sub('[^0-9,^A-Z,^a-z, ]','',date)
        title = date + " " + title
        if len(title) > 120: title = title[0:120] #due to apparent maximum of name length a pdf can have
        save_link = os.path.join("Downloads/Treaties/", title + ".pdf")
        
        #download pdf with correct title
        filename = Path(save_link)
        response = requests.get(pdf_link[1:])
        filename.write_bytes(response.content)

        return 1, title, full_title
    
    #get title of the treaty for the meta data
    begin_title = website.find("<h1>")
    end_title = website.find("</h1>")
    title = website[begin_title + 4 :end_title]
    print(title)
    title = re.sub('[^0-9,^A-Z,^a-z, ]','',title)
    full_title = title
    if len(title) > 120: title = title[0:120] #due to apparent maximum of name length a pdf can have
    save_link = os.path.join("Downloads/Treaties/", title + ".pdf")
    return 0, title, full_title


def download_meta_data_treaties(html_text):
    """
    Gathers meta data and returns it as a dict
    """
    dict_of_data= {}
    website = str(html_text)
    meta_data_names = ["Document type", "Reference Number", "Date", "Source", "Status", "Subject", "Meeting", "Treaty","Website", "Field of application", "Abstract"]
    
    for data in meta_data_names:
        find_data = website.find(f"<dt>{data}</dt>")
  
         
        
        if find_data != -1: #check if this data exists for that treaty  decision
            begin_data = website[find_data:].find("<dd>")
            end_data = website[find_data:].find("</dd>")
            extract_data = website[find_data + begin_data + 4:end_data + find_data] #extract the data in between
            
            dict_of_data[data] = extract_data #add to dict

    #delete hyperlinks from the dict               
    for data_type in dict_of_data:
        dict_of_data[data_type] = re.sub(r'(<.*?>)', ' ', dict_of_data[data_type])
        dict_of_data[data_type] = dict_of_data[data_type].strip("\\n        ") #and new lines 
            
    return dict_of_data

    


if __name__ == "__main__":
      
    
    print("Downloading..")
    document_counter = 0
    if DOWNLOAD_TREATY_DECISIONS:
        for page_num in range(PAGE_START_TREATY_DECISIONS, PAGE_STOP_TREATY_DECISIONS + 1):
            res = open_website(f"https://www.ecolex.org/result/?type=decision&page={page_num}")
            if document_counter != 0 : print(f"Next Page; Page Number: {page_num}")
            pdf_inf = get_pdf_info(res)
            
            counter = download_pdfs(pdf_inf) #downloads the documents, and returns the amount of documents downloaded
            document_counter += counter
            print("\n", "Documents Downloaded: ", document_counter)
        print(" \n Treaty Decisions Downloaded Total: ", document_counter)
            
            
    if DOWNLOAD_TREATIES:
        document_counter_treaties = 0
        for page_num in range(PAGE_START_TREATIES, PAGE_STOP_TREATIES + 1):
            res = open_website(f"https://www.ecolex.org/result/?type=treaty&page={page_num}")
            pdf_inf = get_pdf_info(res)
            
           
            counter = download_treaties(pdf_inf)
            document_counter_treaties += counter
            print("\n", "Treaties Downloaded: ", document_counter_treaties)
            document_counter_treaties += counter
            print(f"Next Page; Page Number: {page_num}")
        print(" \n Treaty Decisions Downloaded Total: ", document_counter )
        print(" \n Treaties Downloaded Total: ", document_counter_treaties)
    print("\n Download Complete")
    
    print("Downloaded failed to download: ", list_of_failed_downloads)






































