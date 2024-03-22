import os
import glob
import pdfplumber
from pathlib import Path
from urllib.error import HTTPError
import shutil
import pathlib
import datetime
import json
import configparser
# import logging
# import logging.config
import re
import time
import sys
import time
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.runtime.client_request_exception import ClientRequestException
from ast import literal_eval
from string import ascii_lowercase
from itertools import groupby
import pandas as pd
import pdfplumber
import pdfplumber
from office365.sharepoint.files.move_operations import MoveOperations
from process_given_pdf import main as given_pdf_main



config_obj = configparser.ConfigParser()
config_obj.read(r'D:\Advait Invoice code\config.ini')
sppaths = config_obj['spdl_path']
spparam = config_obj['spdoclib']
sprlpath = config_obj['sp_relative_path']
fol_loc = config_obj['folder_path']

spsite = spparam['rootsite']
spdoclib = spparam['site_url']
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
sprproot= sprlpath['root']
#sprpproblem = sprlpath['problematic']
#sprpduplicate = sprlpath['duplicate'] ###Add duplicate path

ctx = ClientContext(spdoclib).with_credentials(ClientCredential(cid, cs))
        
flag =0
def main(sproot):

    global sprppro, ctx
    print('1')

    root_folder = ctx.web.get_folder_by_server_relative_path(sproot)
    #pro_folder = ctx.web.get_folder_by_server_relative_path(spprocessed)

    root_folder.expand(["Folders"]).get().execute_query()
    metaurl = ''

    if root_folder.folders:
        print(root_folder.folders)
        for folder in root_folder.folders:
            folder = try_get_folder(folder.serverRelativeUrl)
            files = folder.get_files(True).execute_query()
            for f in files:
                text =''
                metaurl = f.properties['ServerRelativeUrl']
                finalurl = spsite+metaurl
                file_name = os.path.basename(finalurl)
                path = os.path.join(lsppath, file_name)

                print('>>>>>>>>>>>>>>>>',path)
                with open(path,'wb') as local_file:
                    p_file = ctx.web.get_file_by_server_relative_url(metaurl).download(local_file).execute_query()
            
                if '.pdf' in file_name or '.PDF' in file_name:
                    print('pdf',file_name)
                    with pdfplumber.open(path) as pdf:
                        for page in pdf.pages:                    
                            text += page.extract_text()

                    given_pdf_main(path)

                os.remove(path)
            move_to_folder_processed(folder.serverRelativeUrl,sprppro)
    

def move_to_folder_processed(folder,sprppro):
    file_from = ctx.web.get_folder_by_server_relative_url(folder).execute_query()

    file_to = file_from.move_to(sprppro).execute_query()
    print("'{0}' moved into '{1}'".format(folder, sprppro))

                                                                                                                                                        
def try_get_folder(url):
    try:
        return ctx.web.get_folder_by_server_relative_url(url).get().execute_query()
    except ClientRequestException as e:
        if e.response.status_code == 404:
            return None
        else:
            raise ValueError(e.response.text)
        

main(sproot)

