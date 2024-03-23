import pdfplumber
import pandas as pd
import re
from string import ascii_lowercase
import os
from datetime import datetime
from itertools import permutations
import warnings
warnings.filterwarnings("ignore")

# date from : _

# date to : _

# date from : _ to:  _

# Due on _


def is_date(string):
    return not pd.isnull(pd.to_datetime(string, errors='coerce'))

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



def is_date(string):
    return not pd.isnull(pd.to_datetime(string, errors='coerce'))

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

def find_date_matches_beta(pdf_path, date_pattern, date_transaction_patterns):
    with pdfplumber.open(pdf_path) as pdf:
        results = []  # To store results

        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()  # Extract words with bounding box info

            for i, word in enumerate(words):
                if date_pattern.match(word['text']):
                    match_key = 'date'

                    if i > 0 and any(pattern.match(words[i - 1]['text']) for pattern in date_transaction_patterns.values()):
                        match_key = [key for key, pattern in date_transaction_patterns.items() if pattern.match(words[i - 1]['text'])][0] + '_' + match_key

                    candidate_date_text = words[i]['text'].lstrip(':').strip()
                    if is_date(candidate_date_text):
                        results.append({match_key: candidate_date_text})
                    else:
                        # Look ahead for day, month, and year in the next few words
                        for j in range(i + 1, min(i + 4, len(words))):
                            next_word = words[j]['text']
                            if is_day(next_word) or is_month(next_word) or is_year(next_word):
                                candidate_date = ' '.join([words[k]['text'] for k in range(i, j + 1)])
                                if is_date(candidate_date):
                                    results.append({match_key: candidate_date})
                                    break  # Found a valid date

    return results






def check_split_date_old(date_parts):
    # Placeholder variables for day, month, and year
    day, month, year = None, None, None

    # Attempt to identify day, month, and year from the list of date parts
    for part in date_parts:
        if not day and is_day(part):
            day = part
        elif not month and is_month(part):
            month = part
        elif not year and is_year(part):
            year = part

    # If we've identified day, month, and year, try to form a valid date string
    if day and month and year:
        try:
            # Handle numeric and textual month representations
            if month.isdigit():
                month_str = f"{int(month):02d}"  # Ensure two-digit format
            else:
                month_str = datetime.strptime(month, '%b').strftime('%m')  # Convert textual month to two-digit format
            
            # Form and validate the full date string
            date_str = f"{year}-{month_str}-{day.zfill(2)}"  # Ensure day is two-digit
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            return None
    
    return None


def find_date_in_sequence(sequence):
    # Generate all possible permutations of three elements from the sequence
    for perm in permutations(sequence, 3):
        # Check if the permutation forms a valid date sequence
        date_str = check_split_date(perm)
        if date_str:
            return date_str

def find_date_matches_v1(pdf_path, date_pattern, date_transaction_patterns):
    with pdfplumber.open(pdf_path) as pdf:
        results = []  # To store results

        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words()  # Extract words with bounding box info

            for i, word in enumerate(words):
                if date_pattern.match(word['text']):

                    match_key = 'date'

                    if i > 0 and any(pattern.match(words[i - 1]['text']) for pattern in date_transaction_patterns.values()):
                        match_key = [key for key, pattern in date_transaction_patterns.items() if pattern.match(words[i - 1]['text'])][0] + '_' + match_key

                   
                    for j in range(i + 1, min(i + 5, len(words))):
                        candidate_date_text = words[j]['text']
                        # Correctly handle ':' prefix in the candidate date text
                        candidate_date_text = candidate_date_text.lstrip(':').strip()

                        if is_date(candidate_date_text):
                            results.append({match_key: candidate_date_text })
                            break
                        
                        ### append candidate_date_text to date_words_list across the loop
                        # after the loop, call function check split date which needs to be written, it goes through the elements the list and if e_1 is dd, e_2 is mm, e_3 is yy then returns e_1, e_2, e_3 also checks for mm, dd, yy

    return results


def check_split_date(date_parts):
    """Check if a list of strings can form a date and return the date string."""
   # print(date_parts)
    year_index = None
    potential_date_parts = None
   # print("here")
    # Identify the position of the year in the list
    for i, part in enumerate(date_parts):
     #   print(part)
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

def find_date_matches(pdf_path, date_pattern, date_transaction_patterns):
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
                        if is_date(candidate_date_text):
                         #   found_date = True
                            results.append({match_key: candidate_date_text})
                            
                            #break
                        date_words_list.append(candidate_date_text)
                    

                    checked_date = check_split_date(date_words_list) 
                    if checked_date:
                            results.append({match_key: checked_date})
                           # print(results)
                            break  # Stop after finding a valid date

    return results




def parse_date_matches(date_match_list):

    #print(date_match_list)
    values_by_key = {}

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



def date_main(pdf_name):
    verbose=True
    #output = find_transaction_patterns(pdf_name, right_patterns_dict, down_patterns_dict_list, other_right_patterns_dict, check_variable_format, calculate_heuristic, "transaction_number")
    
    output =  parse_date_matches(find_date_matches(pdf_name, date_pattern, date_transaction_patterns))
    if verbose:
   #     print(pdf_name)
         print(output)
    #     print('\n')
    return output
