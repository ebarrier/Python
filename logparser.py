import urllib
from collections import Counter

class LogParser(object):

    def __init__(self, gi, keywords):
        """
        This function sets up an LogParser instance
        """
        self.gi = gi                # Reference to GeoIP database object
        self.keywords = keywords    # List/tuple of keywords
        self.reset()                # Define and reset counter attributes

    def reset(self):
        """
        This function resets the counters of an LogParser instance
        """
        self.total = 0              # Total number of log entries parsed
        self.d = Counter()          # Hits per keyword
        self.urls = Counter()       # Hits per URL using the Counter instead of dictionnary
        self.user_bytes = Counter() # Bytes served per user
        self.countries = {}         # Hits per country code
        self.ip_addresses = {}      # Hits per source IP address

    def parse_file(self, fh):
        for line in fh:
            self.total = self.total + 1
            try:
                #splits  the log line by " character
                source_timestamp, request, response, referrer, _, agent, _ = line.split("\"")
                #splits the "request" part into smaller parts divided by space
                method, path, protocol = request.split(" ")
            except ValueError:
                continue # Skip garbage

            #3 is the number of separators counted for the split
            source_ip, _, _, timestamp = source_timestamp.split(" ", 3)
        
            #Skips the ipv6 addresses in the count
            if not ":" in source_ip:
                # nicer than try-catch.
                self.ip_addresses[source_ip] = self.ip_addresses.get(source_ip, 0) + 1
                cc = self.gi.country_code_by_addr(source_ip)
                #print source_ip, "resolves to ", cc
                self.countries[cc] = self.countries.get(cc, 0) + 1
            if path == "*": continue # Skip asterisk for path

            _, status_code, content_length, _ = response.split(" ")
            #converts the variable into integer
            content_length = int(content_length)

            # makes the path display the right characters no matter what OS generated the URL.
            #It cleans the escape characters. In our case it is used to display well the ~.        
            path = urllib.unquote(path)

            if path.startswith("/~"):
                #removes the first two characters and splits every / char.
                username = path[2:].split("/")[0]
                self.user_bytes[username] += content_length

            #to count the urls. With the Counter() function, we do not need the Try/Catch.
            self.urls[path] += 1 ##self.urls({path:1}) does the same

            #to count the OSs
            for keyword in self.keywords:
                if keyword in agent:
                    self.d[keyword] += 1
                    break # Stop searching for other keywords                                                       
                                                        
