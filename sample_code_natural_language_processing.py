# This is the last piece of a Natural Language Processing script. It implements
# a number of functions which are not displayed to turn the html file into
# a user-defined RowObject class and then use them to write and populate a CSV. 
#
# Code originally from the Cook County SAO project which converts the
# Illinois Compiled Statutes into a data table.

def RowObject_2_csv_row(row):
    """
    Input: A RowObject
    Output: A dictionary with keys that are row headers and values containing
    data from the RowObject that will populate a single CSV row
    Description: A helper function implemented in the iterative loop below.  
    Strips the relevant information from each RowObject and organizes it
    into a dictionary. 
    """   
    global depth
    global level_names
    global level_text
    global global_list_row_obj
    
    ancestry_list = [None]*depth #Will be filled with RowObjects and Nones
    level = row.get_level()-1
    ancestry_list[level] = row
    while(level > 0):
        ancestry_list[level-1] = ancestry_list[level].get_parent()
        level -= 1   
            
    names = [None if not row else row.get_level_name() for row in ancestry_list]
    this_level_text = [row.get_text() if row else "" for row in ancestry_list]
    headers = ["Chapter", "Act", "Section", "Title", "Rule"] + level_names + ["Text", "History", "Source", "Ancestral-Text", "Descendant-Text"] + level_text + ["Hyphen_Statute_Code"]
    
    if(row.get_level() > 0): #Non-secmain rows
        #New: Next 4 lines of code are a fix for the clerk's data where we needed hyphenated statute codes
        hyphen_statute_code = str(row.get_chapter()) + " ILCS " + str(row.get_act()) + '/' + str(row.get_section())
        for name in names:
            if(name):
                hyphen_statute_code += '-' + str(name)
        values = [row.get_chapter(), row.get_act(),  row.get_section(), row.get_title().replace('“', '').replace('”',''), row.get_rule()] + [name for name in names] + [row.get_text().replace("’", "'").replace('“', '"'), row.get_history(), row.get_source(), row.get_ancestral_text(), row.get_descendant_text(global_list_row_obj)] + this_level_text + [hyphen_statute_code]
    elif(row.get_level() == 0): #Secmain rows
        values = [row.get_chapter(), row.get_act(),  row.get_section(), row.get_title().replace('“', '').replace('”',''), row.get_rule()] + [None]*(depth+2) + [row.get_source(), None, row.get_descendant_text(global_list_row_obj)] 
    return dict(zip(headers, values))

with open('CodifiedTable.csv', 'w', newline='') as csvfile:
    html_tags = tags_of_interest()
    listRowObjects = row_objectify(html_tags)
    fieldnames = ["Index", "Chapter", "Act", "Section", "Title", "Rule"] + level_names + ["Text", "History", "Source", "Ancestral-Text", "Descendant-Text"] + level_text + ["Hyphen_Statute_Code"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    b = {'Index': 1} #Used for indexing the csv
    for row in listRowObjects:
        if(row.get_level() < 10): #We're including SECMAIN rows as blank text (still skip source and history)
            data = {**b, **RowObject_2_csv_row(row)}
            writer.writerow(data)
            b["Index"] += 1
