# from core_function import corefc
# from corefunction import corefc
#from checkdt import checkdate
from pathlib import Path
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.runtime.auth.token_response import TokenResponse
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.runtime.client_request_exception import ClientRequestException
from ast import literal_eval
from string import ascii_lowercase
from itertools import groupby
import configparser

import os
from office365.sharepoint.attachments.creation_information import (
    AttachmentCreationInformation,
)



config_obj = configparser.ConfigParser()
config_obj.read(r'/code/config.ini')

sppaths = config_obj['spdl_path']
spparam = config_obj['spdoclib']
sprlpath = config_obj['sp_relative_path']
fol_loc = config_obj['folder_path']

spsite = spparam['rootsite']
spdoclib = spparam['site_url']
splistname = spparam['list_name']
spusername = spparam['uname']
sppassword = spparam['upass']
cid = spparam['cid']
cs = spparam['cs']

sproot = sppaths['root']
spprocessed = sppaths['processed']
#spproblematic = sppaths['problematic']
#spduplicate = sppaths['duplicate'] ###Add duplicate path

lsppath = fol_loc['spdl']

sprppro = sprlpath['processed']
#sprpproblem = sprlpath['problematic']
#sprpduplicate = sprlpath['duplicate'] ###Add duplicate path

global tasks_list
def list_connection(list_name):
    global tasks_list
    try:
        ctx = ClientContext(spdoclib).with_credentials(ClientCredential(cid, cs))
        list_title = list_name
        tasks_list = ctx.web.lists.get_by_title(list_title)

    except Exception as e:
        if e.response.status_code == 404:
            print(None)
        else:
            print(e.response.text)

def duplicate_bill_check(bill_no):
    list_connection('IProv1')
    paged_items = tasks_list.items.get().execute_query()
    for index, item in enumerate(paged_items): 
        if bill_no == item.properties.get("inv_no"):
            print(item.properties.get('RequestNo'))
            return 1
    return 0
      
from datetime import datetime

def try_parsing_date(text):
    for fmt in ('%d­%b­%Y','%d-%b-%y','%d-%m-%Y','%d-%b-%Y','%d%b%Y','%d-%b-%Y','%d-%b-%y','%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y' ,'%d %b %Y'):
        try:
            
            input_date = datetime.strptime(text, fmt)
            output_format = "%d/%m/%Y"

            # Convert the datetime object to a string with the desired output format
            output_date_string = input_date.strftime(output_format)

            return output_date_string

        except ValueError:
            pass


def Untrained(path,inv_no,inv_date,inv_total,gst1,gst1_name, gst1_addr,gst2,gst2_name, gst2_addr,purchase_order_number,bill_number,due_date,delivery_date):
    list_connection('UnTrained_INV')
    try:
        items = tasks_list.items.get().execute_query()
        idlist =[]
        for item in items:  # type:ListItem
            idlist.append(item.properties.get("RequestNo"))
        last_req = idlist[-1]   
        last_req = last_req.split('-')
        last_req = literal_eval(last_req[1])
        new_req = f'REQ-{last_req+1}'

    except Exception as te:
        new_req = 'REQ-1'
    
    
    try:
        task_item = tasks_list.add_item(
            {
                'RequestNo' : str(new_req),
                'Invoice_no' : str(inv_no),
                'Purchase_Order' : str(purchase_order_number),
                'bill_number' : str(bill_number),
                'Invoice_date' : str(inv_date),
                'Due_date' : str(due_date),
                'delivery_date' : str(delivery_date),
                'Inv_total' : str(inv_total),
                'gst_1' : str(gst1),
                'gst1_name'  : str(gst1_name),
                'gst1_addr'  : str(gst1_addr),
                'gst_2' : str(gst2),
                'gst2_name'  : str(gst2_name),
                'gst2_addr'  : str(gst2_addr),
            }
        ).execute_query()

        print('Inserted in untrained')
        with open(path, "rb") as fh:
            file_content = fh.read()
            attachment_file_info = AttachmentCreationInformation(
                os.path.basename(path), file_content
            )
        attachment = task_item.attachment_files.add(attachment_file_info).execute_query()
        print(attachment.server_relative_url)

    except Exception as e:
        if e.response.status_code == 404:
            print(None)
        else:
            print('########',e.response.text) 
    

