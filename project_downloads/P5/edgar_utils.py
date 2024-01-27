import pandas as pd
import re
import geopandas
import netaddr
from bisect import bisect 

ips = pd.read_csv("ip2location.csv")

def lookup_region(ip):
    fixedip=re.sub(r"[A-Z]|[a-z]", "0", ip)
    myip=int(netaddr.IPAddress(fixedip))
    idx= bisect(ips["low"], myip)-1
    region= ips.iloc[idx]["region"]
    return region

class Filing:
    def __init__(self, html):
        self.dates=[]
        dates=re.findall(r"[12][09]\d{2}-\d{2}-[0123][0-9]", html)
        for date in dates:
            if date[-2:]!="00":
                if int(date[5:7])>0 and int(date[5:7])<=31:
                    if int(date[:4])>=1900 and int(date[:4])<=2050:
                        self.dates.append(date)
        sic=re.search(r"SIC=[0-9]+", html)
        if sic !=None:
            sic=re.sub(r"[^0-9|\s]", r"", sic[0])
        addys=[]
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            full_addy=re.sub(r"\\n",r'', "\n".join(lines))
            if full_addy!='':
                addys.append(str(full_addy))
        if sic!=None:
            self.sic=int(sic)
        else:
            self.sic=sic
        self.addresses = addys

    def state(self):
        code=None
        for addy in self.addresses:
            code=re.search(r"[^A-Z][A-Z]{2} [0-9]{5}", addy)
            if code!=None:
                break
        if code!=None:
            return code[0][1:3]
        