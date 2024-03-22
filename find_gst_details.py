import re
import requests
import pdfplumber
def gstdetails(gstin):
    try:
        url = f'http://sheet.gstincheck.co.in/check/2046e097577fd2efa1c721fc3d0f2948/{gstin}'
        response = requests.get(url)
        data = response.json()
        vendor_name = data['data']['lgnm']  # Vendor Name
        vendor_address = ''.join(data['data']['pradr']['adr'])
        print(">> \n",vendor_address)
          # Vendor Address
        return vendor_name, vendor_address
    except Exception as e:
        print(f"Error fetching details for GSTIN {gstin}: {e}")
        return '-', '-'

def gst_main(path):
    gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr = '-','-','-','-','-','-'
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text()

    gstin_regex = r'[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}'
    gstin_numbers = list(set(re.findall(gstin_regex, text)))  # Remove duplicates

    gst_data = []
    if len(gstin_numbers) == 1:
        gstin = gstin_numbers[0]
        gst_name, gst_addr = gstdetails(gstin)
        gst_data.append(gstin)
        gst_data.append(gst_name)
        gst_data.append(gst_addr)
    else:
        for gstin in gstin_numbers[:3]:  # Handle at most three GSTINs
            gst_name, gst_addr = gstdetails(gstin)
            gst_data.append(gstin)
            gst_data.append(gst_name)
            gst_data.append(gst_addr)
    
    print(gst_data)
    if len(gst_data) == 3:
        gst1= gst_data[0]
        gst1_name = gst_data[1]
        gst1_addr = gst_data[2]
    if len(gst_data) == 6:
        gst1= gst_data[0]
        gst1_name = gst_data[1]
        gst1_addr = gst_data[2]
        gst2= gst_data[3]
        gst2_name = gst_data[4]
        gst2_addr = gst_data[5]
    
    return gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr


#gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr = gst_main("D:\Advait Invoice code\PO1.pdf")

#print(gst1)
#print(gst1_name)
#print(gst1_addr)
#print(gst2)
#print(gst2_name)
#print(gst2_addr)