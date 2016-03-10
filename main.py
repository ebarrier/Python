import argparse
import codecs #for Jinja
import GeoIP
import gzip
from jinja2 import Environment, FileSystemLoader #This is the templating engine we use
import os
import urllib

# Following is the directory with log files,
# On Windows substitute it where you downloaded the files
parser = argparse.ArgumentParser(description='Apache2 log parser.')

parser.add_argument('--path', default="/home/ebarrier/logs", help='Path to Apache2 log files')
parser.add_argument('--topurls', help="Find top URL-s", action='store_true')
parser.add_argument('--geoip', help ="Path to file to resolve IPs to country codes", action='store_true', default='/usr/share/GeoIP/GeoIP.dat')
parser.add_argument('--verbose', help="Let's chat", action="store_true")

args = parser.parse_args()

gi = GeoIP.open(args.geoip, GeoIP.GEOIP_MEMORY_CACHE) #download list of countries with their IPs
print "We are expecting logs from:", args.path
print "Do we want top URL-s?", args.topurls

keywords = "Windows", "Linux", "OS X", "Ubuntu", "Googlebot", "bingbot", "Android", "YandexBot", "facebookexternalhit"
d = {} # Curly braces define empty dictionary
urls={} #dictionary for urls
users={} #dictionary for users
ip_addresses={} #Ips
countries={} #list of countries

total = 0


for filename in os.listdir(args.path):
    if not filename.startswith("access.log"):
        continue
    if filename.endswith(".gz"):
        continue # Skips .gz files to save time in processing
        fh = gzip.open(os.path.join(args.path, filename))
    if args.verbose:
        print "Parsing:", filename
    else:
        fh = open(os.path.join(args.path, filename))
    #print "Going to process:", filename

    for line in fh:
        total = total + 1
        try:
            source_timestamp, request, response, referrer, _, agent, _ = line.split("\"") #splits the log line by " character
            method, path, protocol = request.split(" ") #splits the "request" part into smaller parts divided by space
            path = urllib.unquote(path) # makes the path display the right characters no matter what OS generated the URL. 
                                        #It cleans the escape characters. In our case it is used to display well the ~.
            
            source_ip, _, _, timestamp = source_timestamp.split(" ", 3) #3 is the number of separators counted for the split.
            if not ":" in source_ip: #Skips the ipv6 addresses in the count            
                ip_addresses[source_ip] = ip_addresses.get(source_ip, 0) + 1 # nicer than try-catch.
                
                cc = gi.country_code_by_addr(source_ip)
                #print source_ip, "resolves to ", cc
                countries[cc] = countries.get(cc, 0) + 1

            _, status_code, content_length, _ = response.split(" ")
            content_length = int(content_length) #converts the variable into integer
            
            if path.startswith("/~"):
                user, remainder = path[2:].split("/",1) #removes the first two characters and splits every / char. 
                                                        #"user" will be assign to the first part of the split. 
                                                        #"remainder" will be assigned the second part of the split.
                try:
                    users[user] = users[user] + 1
                except:
                    users[user] = 1

            #to count the urls
            url = "httl://enos.itcollege.ee" + path
            try:
                urls[url] = urls[url] + 1
            except:
                urls[url] = 1

            #to count the OSs
            for keyword in keywords:
                if keyword in agent:
                    try:
                        d[keyword] = d[keyword] + 1
                    except KeyError:
                        d[keyword] = 1
                    break # Stop searching for other keywords
        except ValueError:
            pass # This will do nothing, needed due to syntax

from lxml import etree
from lxml.cssselect import CSSSelector

document =  etree.parse(open('BlankMap-World6.svg'))

max_hits = max(countries.values())
print("country with max amount of hits:", max_hits)
print countries

for country_code, hits in countries.items():
    if not country_code: continue # Skip localhost, sattelite phones, etc
    print country_code, hex(hits * 255 / max_hits)[2:] # 2: skips 0x of hexadecimal number
    sel = CSSSelector("#" + country_code.lower())
    for j in sel(document):
        #line below can be another way written j.set("style", "fill:#" + hex(hits * 255 / max_hits)[2:] + "0000")
        red = hits * 255 / max_hits
        #j.set("style", "fill:#%02x%02x00" % (red, 255-red)) # from green to red through yellow
        #Instead of RGB, it is better to use hue saturation luma color coding (from 0 to 360).
        j.set("style", "fill:hsl(%d, 90%%, 70%%);" % (120 + (0 * 120 / max_hits)))

        # Remove styling from children
        for i in j.iterfind("{http://www.w3.org/2000/svg}path"):
            i.attrib.pop("class", "")

with open("highlighted.svg", "w") as fh:
    fh.write(etree.tostring(document))

def humanize(bytes):
    if bytes<1024:
        return "%d B" % bytes
    elif bytes<1024**2:
        return "%.1f kB" % (bytes / 1024.0)
    elif bytes < 1024**3:
        return "%.1f MB" % (bytes / 1024.0**2)
    else:
        return "%.1f GB" % (bytes / 1024.0**3)

users = sorted(users.items(), key = lambda item:item[1], reverse=True)
urls = sorted(urls.items(), key = lambda item:item[1], reverse=True)
env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)), trim_blocks=True)
with codecs.open("output.html", "w", encoding="utf-8") as fh:
    fh.write(env.get_template("report.html").render(locals())) #locals() is a dict which contains all above defined variables.
                                                               #if variable is defined after after in the code, it is not taken into acccount
#os.system("x-www-browser file://" + os.path.realpath("output.html") + " &")
    

print "\n"
print "Total lines:", total
print "\n"

print("Top 5 OSs")
results = d.items()
results.sort(key = lambda item:item[1], reverse=True)
for keyword, hits in results[:5]: #shows the first 5 results
    print keyword, "==>", hits, "(",hits * 100 / total, "%)"
print "\n"

print("Top 5 visited urls")
if args.topurls:
    results = urls.items()
    results.sort(key = lambda item:item[1], reverse=True)
    for keyword, hits in results[:5]: #shows the first 5 results
        print keyword, "==>", hits, "(",hits * 100 / total, "%)"
else:
    print "Sorry you have not asked to get this output\n"
print "\n"

print("Top 5 visited users")
results = users.items()
results.sort(key = lambda item:item[1], reverse=True)
for keyword, hits in results[:5]: #shows the first 5 results
    print keyword, "==>", hits, "(",hits * 100 / total, "%)"
print "\n"

print("Top 5 users bandwidth consumption")
results = users.items()
results.sort(key = lambda item:item[1], reverse=True)
for user, transferred_bytes in results[:5]: #shows the first 5 results
    print user, "==>", humanize(transferred_bytes)
print "\n"

print("Top IP addresses")
results = ip_addresses.items()
results.sort(key = lambda item:item[1], reverse=True)
for source_ip, hits in results[:5]: #shows the first 5 results
    #print "Gotcha:", gi.country_code_by_addr("194.126.115.18").lower()
    print source_ip, "==>", hits, "(",hits * 100 / total, "%) " "==>", gi.country_code_by_addr(source_ip)
print "\n"
