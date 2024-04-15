import pdfplumber
import re
import os


invoice_pattern = re.compile(r"invoice\s*(no|number|id)?\.?\s*[:.#\-\s]+\s*([\w\d\-\#\/]+)", re.IGNORECASE)

bill_pattern = re.compile(r"bill\s*(no|number|id)?\.?\s*[:.#\-\s]*\s*([\w\d\-\#\/]+)", re.IGNORECASE)

order_pattern = re.compile(r"order\s*(no|number|id)?\.?\s*[:.#\s-]*\s*([\w\d\-\#\/]+)", re.IGNORECASE)
purchase_order_pattern = re.compile(r"(purchase\s+order|p\.?\s*o\.?)\s*(no|number|id)?\.?\s*[:.#\s-]*\s*([\w\d\-\#\/]+)", re.IGNORECASE)

number_pattern = re.compile(r"(no|number)\.?\s*[:\s]*\s*([\w\d\-\#\/]+)", re.IGNORECASE)

invoice_pattern_down_with_no = [
    re.compile(r"invoice\.?", re.IGNORECASE),
    re.compile(r"(no|number)\.?", re.IGNORECASE)
]


bill_pattern_down_with_no = [
    re.compile(r"bill\.?", re.IGNORECASE),
    re.compile(r"(no|number)\.?", re.IGNORECASE)
]

order_pattern_down_with_no = [
    re.compile(r"order\.?", re.IGNORECASE),
    re.compile(r"(no|number)\.?", re.IGNORECASE)
]


purchase_order_pattern_down_with_no = [
    re.compile(r"(purchase\s+order|p\.?\s*o\.?)\.?", re.IGNORECASE),
    re.compile(r"(no|number)\.?", re.IGNORECASE)
]

invoice_pattern_down_without_no = [
    re.compile(r"invoice\.?", re.IGNORECASE)

]


bill_pattern_down_without_no = [
    re.compile(r"bill\.?", re.IGNORECASE)
]

order_pattern_down_without_no = [
    re.compile(r"order\.?", re.IGNORECASE)

]


purchase_order_pattern_down_without_no = [
    re.compile(r"(purchase\s+order|p\.?\s*o\.?)\.?", re.IGNORECASE)
]

def capitalize_nos(result_dict):

    updated_dict = {}

    for key, value in result_dict.items():
        
        new_value = ''.join([char.upper() if char.isalpha() else char for char in value])
        
        updated_dict[key] = new_value

    if "purchase_order_number" in updated_dict and "order_number" in updated_dict:
 
        if updated_dict["purchase_order_number"] == updated_dict["order_number"]:

            del updated_dict["order_number"]

        
   # print("updated dict")
   # print(updated_dict)

    return updated_dict


def find_variable_matches(pdf, regex_pattern, variable_name):
    all_matches = []
    for page_num, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text:
            continue

        # Use finditer to iterate over all matches as match objects
        for match in regex_pattern.finditer(text.lower()):
           # print(match)
            #print("match group 0\n")
            #print(match.group(0))
            #print("match group 1\n")
            #rint(match.group(1))
            #print("assign")
            num_groups = len(match.groups())
            #print(match.group(0))

            variable_value = match.group(num_groups) 
          #  print(match.group(0))
          #  print(match.group(num_groups))
            all_matches.append({
                variable_name: variable_value,
                "page": page_num,
                "whole_group": match.group(0)

            })

    return all_matches

def print_variable_matches_from_pdf_path(pdf_path, regex_pattern, variable_name):

  with pdfplumber.open(pdf_path) as pdf:
 
    matches = find_variable_matches(pdf, regex_pattern, variable_name)
    print("printing returned matches")
    for match in matches:
        print(match)



def check_variable_format(variable_type, variable_value):


    if variable_type == "transaction_number":
    
        if len(variable_value) < 4:
             return False

       
       # alphanumeric_pattern = re.compile(r'^(?=.*[0-9])(?=.*[a-zA-Z])[a-zA-Z0-9]+$')
     #   alphanumeric_pattern = re.compile(r'^(?=.*[0-9])(?=.*[a-zA-Z])[\w]+$')
      #  alphanumeric_pattern = re.compile(r'^[a-zA-Z0-9]+(?:[\/#-][a-zA-Z0-9]+)*$')
     #   alphanumeric_pattern = re.compile(r'^(?=.*[0-9])[a-zA-Z0-9]+(?:[\/#-][a-zA-Z0-9]+)*$', re.IGNORECASE)
        alphanumeric_pattern = re.compile(r'^(?=.*[0-9]).*(?:[a-zA-Z0-9]+[\/#-]?)+$', re.IGNORECASE)


   
        numeric_pattern = re.compile(r'^\d+$')

        # Validate against patterns
        if alphanumeric_pattern.match(variable_value) or numeric_pattern.match(variable_value):
            #print("match")
            return True
        else:
            return False
    else:
        # Handles other variable_types
        pass

    return False  

def find_variable_value_from_matches(match_results, key_variable_name, check_variable_name, check_format_func):
  
  #print("match results")
  #print(match_results)

  variable_candidate_list = list(map( lambda x: x[key_variable_name], match_results))
  variable_name_list = [check_variable_name for i in range(len(variable_candidate_list))]
  #print("variable_candidate_list")
  #print(variable_candidate_list)

  list_boolean = list(map(check_format_func,  variable_name_list, variable_candidate_list))

  selected_elements = [element for boolean, element in zip(list_boolean, variable_candidate_list) if boolean]
  
  #print("selected_elements")
  #print(selected_elements)

  if not selected_elements:      
        return None


  max_length_element = max(selected_elements, key=len)
  return max_length_element
  #max_length_element = max(freq_elements, key=len)

  #element_frequency = Counter(selected_elements)

  #max_freq = max(element_frequency.values())

  #freq_elements = [element for element, freq in element_frequency.items() if freq == max_freq]

  #if len(freq_elements) == 1:
  #          return freq_elements[0]

  #max_length_element = max(freq_elements, key=len)

  #max_length_elements = [elem for elem in freq_elements if len(elem) == len(max_length_element)]

  #return max_length_elements[0]

 # return max_length_elements[0]`



def calculate_heuristic(bbox, cbox):

   vertical_distance =  cbox[1] - bbox[1]

   left_horizontal_diff = abs(cbox[2] - bbox[2])

   right_horizontal_diff = abs(cbox[3] - bbox[3])

   return vertical_distance + left_horizontal_diff + right_horizontal_diff

def find_variable_down_with_closeness_score(pdf, patterns, calculate_score_function):
    results = []  

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

                # Finding candidate below this bounding box

                candidates = []
                for candidate in words[i + len(patterns):]: 
                    c_box = candidate['bottom'], candidate['top'], candidate['x0'], candidate['x1']

                    if c_box[1] > resultant_bbox[1] and (c_box[2] < resultant_bbox[3] and c_box[3] > resultant_bbox[2]):
                        candidates.append(candidate['text'])
                    if len(candidates) == 3:  # buffer for fcfs
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


def find_transcation_match_right_from_pdf_path(pdf_path, right_pattern, variable_name, check_variable_name, check_format_func):

    with pdfplumber.open(pdf_path) as pdf:

            matches = find_variable_matches(pdf, right_pattern,variable_name)
            #print(matches)
            if matches:
                selected_element = find_variable_value_from_matches(matches, variable_name, check_variable_name, check_format_func)
                return {variable_name : selected_element}

def find_transcation_match_down_from_pdf_path(pdf_path, down_patterns, variable_name, score_function, check_format_func, check_variable_type):

    with pdfplumber.open(pdf_path) as pdf:
        result = find_variable_down_with_closeness_score(pdf, down_patterns,score_function)
        if result:

            if result[0]['best_candidate'] is not None:

                if check_format_func(check_variable_type, result[0]['best_candidate']):

                    return {variable_name : result[0]['best_candidate']}




right_patterns_dict  = {"invoice_number" : invoice_pattern, "purchase_order_number" : purchase_order_pattern, "order_number":order_pattern, "bill_number": bill_pattern }

down_patterns_dict_with_no = { "invoice_number" : invoice_pattern_down_with_no ,
                              "bill_number" : bill_pattern_down_with_no,
                               "order_number" : order_pattern_down_with_no,
                                "purchase_order_number" : purchase_order_pattern_down_with_no}

down_patterns_dict_without_no = { "invoice_number" : invoice_pattern_down_without_no ,
                              "bill_number" : bill_pattern_down_without_no,
                               "order_number" : order_pattern_down_without_no,
                                "purchase_order_number" : purchase_order_pattern_down_without_no}

down_patterns_dict_list = [down_patterns_dict_with_no, down_patterns_dict_without_no]

other_right_patterns_dict = {"number" : number_pattern }

#down_patterns_dict_with_no["invoice_number



def find_right_transaction_from_patterns(pdf_path, right_patterns_dict, check_variable_type, check_format_func ):

  results = {}
  for variable_name, pattern in right_patterns_dict.items():
    
    result = find_transcation_match_right_from_pdf_path(pdf_path, pattern, variable_name, check_variable_type, check_format_func)
    if result is not None:
        if result[variable_name] is not None:
              results.update(result)

  return results          

def find_down_transaction_from_patterns(pdf_path, down_patterns_dict, score_function, check_variable_type, check_format_func ):

  for variable_name, down_pattern_list in down_patterns_dict.items():

    result = find_transcation_match_down_from_pdf_path(pdf_path, down_pattern_list, variable_name, score_function, check_format_func, check_variable_type)
    if result is not None:
      return result

def find_transaction_patterns(pdf_path, right_patterns_dict, down_patterns_dict_list, other_right_patterns_dict, check_format_func,score_function, check_variable_type):

    R = {}
    results = find_right_transaction_from_patterns(pdf_path, right_patterns_dict, check_variable_type, check_format_func)
    #print(results)
    if results is not None:
        if len(results) > 0:
          # print("here 1")
            if list(results.keys())!=['order_number']:
               return capitalize_nos(results)
            else:
                R.update(capitalize_nos(results))
       

    for down_patterns_dict in down_patterns_dict_list:
     # print("here 2")
      result = find_down_transaction_from_patterns(pdf_path, down_patterns_dict, score_function, check_variable_type, check_format_func)
      if result is not None:
        #print("result")
        #print(result)
        if len(result) > 0:

          #  print("here 2")
            return capitalize_nos(result)
    
    if R is not None:
        if len(R) > 0:
            return R

    result = find_right_transaction_from_patterns(pdf_path, other_right_patterns_dict, check_variable_type, check_format_func)
    if result is not None:
      #  print("here 3")
        return capitalize_nos(result)



def number_main(path):

    verbose = True
    output = find_transaction_patterns(path, right_patterns_dict, down_patterns_dict_list, other_right_patterns_dict, check_variable_format, calculate_heuristic, "transaction_number")
    if verbose:
   #     print(pdf_name)
         print(output)
    #     print('\n')
    return output

#if __name__ == "__main__":

#    parser = argparse.ArgumentParser(description="Extract transaction number from a given PDF file.")
#    parser.add_argument("pdf_name", type=str, help="name of the PDF file to process.")
#    parser.add_argument("--verbose", "-v", action="store_true", help="print detailed output.", default=True)
#    parser.add_argument("--quiet", "-q", action="store_false", dest="verbose", help="suppress detailed output.")

#    args = parser.parse_args()

#    numbrt_main(args.pdf_name, args.verbose)
