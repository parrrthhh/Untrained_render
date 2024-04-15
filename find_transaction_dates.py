
import argparse
import pdfplumber
import pandas as pd
import re
from string import ascii_lowercase
from itertools import groupby
import warnings
import os
from datetime import datetime
from itertools import permutations
warnings.filterwarnings("ignore")

# date from : _

# date to : _

# date from : _ to:  _

# Due on _



date_pattern = re.compile(r"(date|Date)[:\s]*", re.IGNORECASE)

date_transaction_patterns = {
    "invoice": re.compile(r"(invoice|Invoice)[:\s]*", re.IGNORECASE),
    "due":re.compile(r"(due|Due)[:\s]*", re.IGNORECASE),
    "delivery": re.compile(r"(delivery|Delivery)[:\s]*", re.IGNORECASE),
    "receipt": re.compile(r"(receipt|Receipt)[:\s]*", re.IGNORECASE),
    "bill": re.compile(r"(bill|Bill)[:\s]*", re.IGNORECASE),
    "order": re.compile(r"(order|Order)[:\s]*", re.IGNORECASE),
    "purchase_order": re.compile(r"(purchase\s+order|Purchase\s+Order|p\.?o\.?|P\.?O\.?)[:\s]*", re.IGNORECASE),
    "payment": re.compile(r"(payment|Payment)[:\s]*", re.IGNORECASE),
}

#pdf_names = ['Vistara 1.pdf','VIP 1.pdf' , 'Vodafone.pdf', 'MCC 1.pdf', 'Walmart PO 1.pdf' , 'DMART PO 1.pdf', 'SMART PO 2.PDF', 'CROMA PO 2.PDF', "ABRL PO 1 VBGR.pdf", "Indigo 1.pdf", "MTNL.pdf"]

#pdf = pdfplumber.open("Vodafone.pdf")

def check_variable_format(variable_type, variable_value):

  
    if variable_type == "transaction_number":
        # Check minimum length
        if len(variable_value) < 3:
             return False
        
        alphanumeric_pattern = re.compile(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$')
        

        numeric_pattern = re.compile(r'^\d+$')
        
        # Validate against patterns
        if alphanumeric_pattern.match(variable_value) or numeric_pattern.match(variable_value):
            return True
        else:
            return False
    else:

        if variable_type == "date":

          return is_date(variable_value)

    return False  



def is_date_old(string):
   # print(" in is date")
    #print(string)
    return not pd.isnull(pd.to_datetime(string, errors='coerce'))



def is_date(date_str):

    #cleaned_string = re.sub(r'\s+', ' ', string)  # Replace multiple spaces with a single space
    #cleaned_string = re.sub(r'[^\w\s]', '', cleaned_string)  # Remove non-alphanumeric characters
    
    cleaned_string = date_str.replace('\xad', ' ')
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string).strip()
    
    
    try:
        # Attempt to convert the cleaned string to a datetime object
        dt = pd.to_datetime(cleaned_string, errors='coerce')
        return not pd.isnull(dt)
    except ValueError:
        # In case any unexpected error occurs during conversion
        return False



def is_day(word):
    try:
        day = int(word)
        return 1 <= day <= 31
    except ValueError:
        return False

def is_month(word):
    try:
        datetime.strptime(word, '%B')
        return True
    except ValueError:
        try:
            datetime.strptime(word, '%b')
            return True
        except ValueError:
            return False

def is_year(word):
    try:
        year = int(word)
        return 1900 <= year <= 2100
    except ValueError:
        return False
    
def clean_date_string(date_str):

    cleaned_str = date_str.replace('\xad', ' ')
    cleaned_str = re.sub(r'\s+', ' ', cleaned_str).strip()
    return cleaned_str


def check_split_date(date_parts):
    """Check if a list of strings can form a date and return the date string."""
   # print(date_parts)
    year_index = None
    potential_date_parts = None
   # print("here")
    # Identify the position of the year in the list
    for i, part in enumerate(date_parts):
       # print("part")
       # print(part)
        if is_year(part):
    #        print(part)
            year_index = i
     #       print("is year")
            break

    # If a year was found, try to form a date string from the elements before and including the year
    if year_index is not None:
        # Extract elements up to and including the year
        potential_date_parts = ' '.join(date_parts[:year_index + 1])
        #print(potential_date_parts)

    return potential_date_parts

def find_date_matches_right(pdf_path, date_pattern, date_transaction_patterns):
    with pdfplumber.open(pdf_path) as pdf:
        results = []  # To store results

        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()  # Extract words with bounding box info
 
            for i, word in enumerate(words):
                #if page_num == 2:

                   #print(word['text'])
                if date_pattern.match(word['text']):
                    match_key = 'date'
                    #print(words[i-1]['text'])
                    #print(words[i]['text'])
                    #print(words[i+1]['text'])
                    #print(words[i+2]['text'])
                    if i > 0 and any(pattern.match(words[i - 1]['text']) for pattern in date_transaction_patterns.values()):
                        match_key = [key for key, pattern in date_transaction_patterns.items() if pattern.match(words[i - 1]['text'])][0] + '_' + match_key

                    date_words_list = []
                   # found_date = False
                    for j in range(i + 1, min(i + 7, len(words))):
                        
                       
                        candidate_date_text = words[j]['text'].lstrip(':').strip()
                       # print(candidate_date_text)
                       # print(is_date(candidate_date_text))
                        if is_date(candidate_date_text):
                            
                           # print(candidate_date_text)
                         #   found_date = True
                            results.append({match_key: clean_date_string(candidate_date_text)})
                            
                            #break
                        date_words_list.append(candidate_date_text)
                    
                  #  print(date_words_list)  
                    checked_date = check_split_date(date_words_list) 
                  #  print(checked_date)
                    if checked_date:
                            results.append({match_key: clean_date_string(checked_date)})
                           # print(results)
                            break  # Stop after finding a valid date

    return results




def parse_date_matches(date_match_list):

   # print(date_match_list)
    values_by_key = {}
    #print(date_match_list)

    for entry in date_match_list:
        for key, value in entry.items():
            values_by_key.setdefault(key, []).append(value)

    #selected_values = {key: Counter(values).most_common(1)[0][0] for key, values in values_by_key.items()}
    selected_values = {key: max(values, key=len) for key, values in values_by_key.items()}

    #print(selected_values)

    specific_date_keys = [key for key in selected_values if key != 'date']

    if specific_date_keys:

        result = {key: value for key, value in selected_values.items() if key in specific_date_keys}
        if not result:  
            result = {'date': selected_values.get('date')}
    else:
        result = {'date': selected_values.get('date')}

    return result




def calculate_heuristic(bbox, cbox):

   vertical_distance =  cbox[1] - bbox[1]

   left_horizontal_diff = abs(cbox[2] - bbox[2])

   right_horizontal_diff = abs(cbox[3] - bbox[3])

   return vertical_distance + left_horizontal_diff + right_horizontal_diff

def find_variable_down_with_closeness_score(pdf, patterns, calculate_score_function):
    results = []  # To store results

    for page in pdf.pages:
        words = page.extract_words()  # Extract words with bounding box info

        for i, word in enumerate(words):
            # Check sequence of patterns
            match_sequence = True
            matched_words = []

            for j, pattern in enumerate(patterns):
                if i + j < len(words) and pattern.match(words[i + j]['text']):
                    matched_words.append(words[i + j])
                else:
                    match_sequence = False
                    break

            if match_sequence and len(matched_words) == len(patterns):
                # Calculate the resultant bounding box
                bbox_coords = [(word['bottom'], word['top'], word['x0'], word['x1']) for word in matched_words]
                resultant_bbox = (
                    max(word[0] for word in bbox_coords),
                    min(word[1] for word in bbox_coords),
                    min(word[2] for word in bbox_coords),
                    max(word[3] for word in bbox_coords),
                )

                # Finding the best candidate based on closeness score
                best_candidate = None
                min_score = float('inf')  
                for candidate in words[i + len(patterns):]:
                    c_box = (candidate['bottom'], candidate['top'], candidate['x0'], candidate['x1'])
                    score = calculate_score_function(resultant_bbox, c_box)
                    if score < min_score:
                        min_score = score
                        best_candidate = candidate['text']

                if best_candidate:
                    results.append({
                        'page': page.page_number,
                        'best_candidate': best_candidate,
                        'matched_sequence': [word['text'] for word in matched_words],
                        'resultant_bbox': resultant_bbox,
                        'score': min_score,
                    })
                    break  

    return results

def find_variable_down_fcfs(pdf, patterns):
    results = []  # Store results from all pages

    for page in pdf.pages:
        words = page.extract_words()  # Extract words with bounding box info
        for i in range(len(words)):
            # Check sequence of patterns
            match_sequence = True
            matched_words = []

            for j, pattern in enumerate(patterns):
                if i + j < len(words) and pattern.match(words[i + j]['text']):
                    matched_words.append(words[i + j])
                else:
                    match_sequence = False
                    break

            if match_sequence and len(matched_words) == len(patterns):
                # Calculate the resultant bounding box from the matched sequence
                bbox_coords = [(word['bottom'], word['top'], word['x0'], word['x1']) for word in matched_words]
                resultant_bbox = (
                    max(word[0] for word in bbox_coords),  # Max bottom
                    min(word[1] for word in bbox_coords),  # Min top
                    min(word[2] for word in bbox_coords),  # Min left (x0)
                    max(word[3] for word in bbox_coords),  # Max right (x1)
                )

                # Finding candidates below this bounding box
                candidates = []
                for candidate in words[i + len(patterns):]:  # Start searching from the word after the matched sequence
                    c_box = candidate['bottom'], candidate['top'], candidate['x0'], candidate['x1']
            
                    if c_box[1] > resultant_bbox[1] and (c_box[2] < resultant_bbox[3] and c_box[3] > resultant_bbox[2]):
                        candidates.append(candidate['text'])
                    if len(candidates) == 3:  
                        break

                if candidates:
                    results.append({
                        'page': page.page_number,
                        'candidates': candidates,
                        'matched_sequence': [word['text'] for word in matched_words],
                        'resultant_bbox': resultant_bbox,
                    })
                    break  

    return results


def find_transcation_match_down_from_pdf_path(pdf_path, down_patterns, variable_name, score_function, check_format_func, check_variable_type):

    with pdfplumber.open(pdf_path) as pdf:
        result = find_variable_down_with_closeness_score(pdf, down_patterns,score_function)
        if result:

            if result[0]['best_candidate'] is not None:

                if check_format_func(check_variable_type, result[0]['best_candidate']):

                    return {variable_name : result[0]['best_candidate']}



def date_main(pdf_name):
   
    verbose=True
    output =  parse_date_matches(find_date_matches_right(pdf_name, date_pattern, date_transaction_patterns))
    
    if output:

       if verbose:
    #     print(pdf_name)
          print(output)
    #     print('\n')
       return output
    

    else:

        output =  find_transcation_match_down_from_pdf_path(pdf_name, [date_pattern], "date", calculate_heuristic, check_variable_format, "date" ) 

    return output


    
