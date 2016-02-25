import os
import urllib
 
# Following is the directory with log files,
# On Windows substitute it where you downloaded the files
root = "/home/ebarrier/logs"

keywords = "Windows", "Linux", "OS X", "Ubuntu", "Googlebot", "bingbot", "Android", "YandexBot", "facebookexternalhit"
d = {} # Curly braces define empty dictionary
urls={} #dictionary for urls
users={} #dictionary for users

total = 0
import gzip

for filename in os.listdir(root):
    if not filename.startswith("access.log"):
        continue
        print "Skipping unknown file:", filename
    if filename.endswith(".gz"):
        fh = gzip.open(os.path.join(root, filename))
    else:
        fh = open(os.path.join(root, filename))
    #print "Going to process:", filename

    for line in fh:
        total = total + 1
        try:
            source_timestamp, request, response, referrer, _, agent, _ = line.split("\"") #splits the log line by " character
            method, path, protocol = request.split(" ") #splits the "request" part into smaller parts divided by space
            path = urllib.unquote(path) # makes the path display the right characters no matter what OS generated the URL. It cleans the escape characters. In our case it is used to display well the ~.
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


#print "Total lines:", total

print("Top 5 OSs")
results = d.items()
results.sort(key = lambda item:item[1], reverse=True)
for keyword, hits in results[:5]: #shows the first 5 results
    print keyword, "==>", hits, "(", hits * 100 / total, "%)"

print("Top 5 visited urls")
results = urls.items()
results.sort(key = lambda item:item[1], reverse=True)
for keyword, hits in results[:5]: #shows the first 5 results
    print keyword, "==>", hits, "(", hits * 100 / total, "%)"

print("Top 5 visited users")
results = users.items()
results.sort(key = lambda item:item[1], reverse=True)
for keyword, hits in results[:5]: #shows the first 5 results
    print keyword, "==>", hits, "(", hits * 100 / total, "%)"

print("Top 5 users bandwidth consumption")
results = users.items()
results.sort(key = lambda item:item[1], reverse=True)
for user, transferred_bytes in results[:5]: #shows the first 5 results
    print keyword, "==>", transferred_bytes / 1024, "MB"


