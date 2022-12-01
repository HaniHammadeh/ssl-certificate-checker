__author__ = "Hani Hammadeh"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Hani"
__twitter__ = "@hanihammadeh"
__status__ = "Development"

from urllib.request import ssl, socket
#from urllib.error import URLError, HTTPError
from datetime import datetime
import json
import time
import asyncio
import argparse

DEFAULT_HTTPS_PORT=443


def  get_expiry_date(hostname: str, port)-> str:
    '''This function is used to get the expiry date of ssl certificate for a
        given domain name'''
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            data = json.dumps(ssock.getpeercert())
    jsondata=json.loads(data)
    print("".join(
            ('{', json.dumps(hostname),':',json.dumps(jsondata['notAfter']),
            ',', json.dumps('days_to_expire'),':',
            json.dumps(get_days_to_expires(jsondata['notAfter'])),'}')
            )
         )
    #print(jsondata)
    return jsondata['notAfter']

async def async_get_expiry_date(hostname: str, port) -> None:
   '''this is asyncio version of the get_expiry_date function'''
   try:
      coro= asyncio.to_thread(get_expiry_date,hostname,port)
      task = asyncio.create_task(coro)
      await task
   except TimeoutError as et_exception:
        print(f"Time out issue cannot connect to the host {et_exception}")
   except  socket.gaierror as sg_exception:
      print(f'invalid hostname {sg_exception}')
   except ssl.SSLCertVerificationError as ssl_exipred_error:
      print(
            f'The ssl certificate is expired for host {hostname}'
            f'{ssl_exipred_error}'
            )

def get_hostname_port(hostname_port: list[str])->list[tuple]:
   '''This function will take a list of hostnames and ports seperated by : for
      instance www.bbc.com:443 and then retun a list of tuples of the hostname
      and ports'''
   result=[]
   for element in hostname_port:
      host,_, port=element.partition(':')
      port=int(port or DEFAULT_HTTPS_PORT  )
      result.append((host,port))
   return result

def get_days_to_expires(end_date):
   '''This function will return the number of days for a certificate to expire'''
   start_date=datetime.today().strftime("%b %d %H:%M:%S %Y %Z")
   start_date=datetime.strptime(start_date,"%b %d %H:%M:%S %Y ")
   end_date=datetime.strptime(end_date,"%b %d %H:%M:%S %Y %Z")
   
   return str((end_date-start_date).days)

def usage()-> str:
   '''usage message appear to the end user'''
   usage_message='''
   EXAMPLES:
   The below formats are all valid

      - certChecker -o www.goole.com
      - certCheker -o www.goole.com:443 -o www.bbc.com
   The default port is 443 for HTTPS
   '''
   return usage_message

async def main() -> None:
     '''the main function'''
     domain_list:list[str]=[]
     parser=argparse.ArgumentParser(
             prog='certChecker',formatter_class=argparse.RawTextHelpFormatter,
             epilog=usage()
             )
     parser.add_argument(
             '-o','--hostname',action='append',required=True,nargs='+',
             type=str,help='The list of the FQDN to be validated'
             )
     args=parser.parse_args()
     #port=args.port if args.port else 443
     domain_list=[element for sublist in args.hostname for element in sublist]
     hosts=[async_get_expiry_date(host,port) for host,port  in 
             get_hostname_port(domain_list) ]
     await asyncio.gather(*hosts)
     

if __name__=='__main__':
    asyncio.run(main())
