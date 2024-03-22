from datetime import datetime 
import datetime
from pytz import timezone
# "%m/%d/%Y"
def checkdate(string):
    for format in ["%d %b %Y","%b %d, %Y", "%d-%b-%Y","%d-%m-%Y", "%m-%d-%Y", "%d-%b-%y","%d/%b/%Y", "%d-%m-%y","%d/%m/%y","%d/%m/%Y" ,"%B %d,%Y"]:
        try:
            return datetime.datetime.strptime(string, format).date()
        except ValueError:
            continue
    raise ValueError(string)

