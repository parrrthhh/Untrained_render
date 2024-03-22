import pdfplumber
import pandas as pd
import re
from string import ascii_lowercase
from itertools import groupby
from statistics import mean
import os
from collections import Counter


#total invoice|order|purchase order|bil amount/value INR  :

total_pattern = re.compile(r"(amount|Amount|total|Total)[:\s]*", re.IGNORECASE)



def print_total_lines(pdf_path):

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            lines = page.extract_text().split('\n')
            for line in lines:

                if total_pattern.search(line):
                    print(line)
                    print('\n')



def is_numeric_string(s):
    try:
        float(s.replace(',', ''))  # Remove commas before conversion
    except ValueError:
        return False
    return True

def is_money(s):
   # money_pattern = re.compile(r'^\d{1,3}(,\d{3})*(\.\d{1,2})?$')
    
    #money_pattern = re.compile(r'^\d{1,3}(,\d{3})*(\.\d+)?$|^(\d+)(\.\d+)?')
    money_pattern = re.compile(r'^\$?\d{1,3}(,\d{3})*(\.\d+)?\$?$|^\$?(\d+)(\.\d+)?\$?$')
    
    return bool(money_pattern.match(s))


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

        if variable_type == "total":

          return is_money(variable_value)

    return False  

def extract_total(pdf_path, total_pattern):

    with pdfplumber.open(pdf_path) as pdf:
        results = []
        for page in pdf.pages:
            total_lines = []
            lines = page.extract_text().split('\n')
            for line in lines:
                if total_pattern.search(line):
                    total_lines.append(line)



            for line in total_lines:
                words = line.split(' ')
                #print(words[-1])
                if is_money(words[-1]):

                    if(words[-1]!=0):
                    #print("here")

                              total_value = words[-1]
                              rest_of_the_string = " ".join(words[:-1])
                              #rest_words = rest_of_the_string.split(' ')

                              results.append({"total": total_value, "additional_detail": rest_of_the_string})
                    else:

                              total_value = words[-1]
                              rest_of_the_string = " ".join(words[:-1])
                              results.append({"total": total_value, "additional_detail": rest_of_the_string})


        return results

def extract_grand_total(pdf_path, total_pattern):
    with pdfplumber.open(pdf_path) as pdf:
        highest_total = None
        highest_total_line = None
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                if total_pattern.search(line):
                    words = line.split(' ')
                    if words:  # Check if words list is not empty
                        last_word = words[-1].replace('$', '')  # Remove dollar sign if present
                        if is_money(last_word):
                            numeric_value = float(last_word.replace(',', ''))
                            if highest_total is None or numeric_value > highest_total:
                                highest_total = numeric_value
                                highest_total_line = line
                    else:
                        for i, word in enumerate(words):
                            if total_pattern.search(word):
                                for j in range(i+1, len(words)):
                                    word_j = words[j].replace('$', '')  # Remove dollar sign if present
                                    if is_money(word_j):
                                        numeric_value = float(word_j.replace(',', ''))
                                        if highest_total is None or numeric_value > highest_total:
                                            highest_total = numeric_value
                                            highest_total_line = line
                                            break
        if highest_total_line:
            rest_of_the_string = " ".join(highest_total_line.split(' '))
            return [{"total": highest_total, "additional_detail": rest_of_the_string}]
        return []


def extract_grand_total_old(pdf_path, total_pattern):
    with pdfplumber.open(pdf_path) as pdf:
        highest_total = None
        highest_total_line = None
        for page in pdf.pages:
            lines = page.extract_text().split('\n')
            for line in lines:
                if total_pattern.search(line):
                    
                    words = line.split(' ')
                   # print(words)
                   # print(words[-1])
                    # Check if the last word is a monetary value not equal to zero
                    if is_money(words[-1]):
                    #    print("here")
                       # print(words[-1])
                        # Convert to float for comparison, removing commas
                        

                        numeric_value = float(words[-1].replace(',', ''))
                        if highest_total is None or numeric_value > highest_total:
                            highest_total = numeric_value
                            highest_total_line = line
                    else:

                      for i, word in enumerate(words):
                        if total_pattern.search(word):
                          for j in range(i+1, (len(words))):

                              if is_money(words[j]):


                                      numeric_value = float(words[j].replace(',', ''))
                                      if highest_total is None or numeric_value > highest_total:
                                              highest_total = numeric_value
                                              highest_total_line = line
                                              break
                                      
                                
                      
        # Construct the final result if a highest total has been found
        if highest_total_line:
            words = highest_total_line.split(' ')
            #total_value = words[-1]
            rest_of_the_string = " ".join(words)
            return [{"total": highest_total, "additional_detail": rest_of_the_string}]
        return []





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

def total_main(pdf_name):
    verbose=True
    #output = find_transaction_patterns(pdf_name, right_patterns_dict, down_patterns_dict_list, other_right_patterns_dict, check_variable_format, calculate_heuristic, "transaction_number")
    
    output = extract_grand_total(pdf_name, total_pattern)
    
    if len(output)>0:

        result = output[0]
        if verbose:

           print(result)
        return result

    else:           
   
       output =  find_transcation_match_down_from_pdf_path(pdf_name, [total_pattern], "total", calculate_heuristic, check_variable_format, "total" ) 

       if output is not None:

           if verbose:

              print(output)
           return output

