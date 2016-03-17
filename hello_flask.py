import os
from flask import Flask
from jinja2 import Environment, FileSystemLoader
import gzip
import urllib

env = Environment(loader=FileSystemLoader("templates"), trim_blocks=True)

app = Flask(__name__)

def humanize(bytes):
    if bytes<1024:
        return "%d B" % bytes
    elif bytes<1024**2:
        return "%.1f kB" % (bytes / 1024.0)
    elif bytes < 1024**3:
        return "%.1f MB" % (bytes / 1024.0**2)
    else:
        return "%.1f GB" % (bytes / 1024.0**3)

def list_log_files():
    #Generator has yield management
    #It basically returns a list of files we are interested in
    for filename in os.listdir("/home/ebarrier/Documents/Python/logs"):
        if filename.endswith(".log"):
            yield filename
        if filename.endswith(".gz"):
            yield filename

def parse_log_file(filename):
    if filename.endswith(".gz"):
        fh = gzip.open(os.path.join("/home/ebarrier/Documents/Python/logs", filename))
    else:
        fh = open(os.path.join("/home/ebarrier/Documents/Python/logs", filename))
    urls={}
    user_bytes={}
    for line in fh:
        try:
            source_timestamp, request, response, referrer, _, agent, _ = line.split("\"")
            method, path, protocol = request.split(" ") 
        except ValueError:
            continue
        if path == "*": continue
        _, status_code, content_length, _ = response.split(" ")
        content_length = int(content_length)          
        path = urllib.unquote(path)

        if path.startswith("/~"):
            user = path[2:].split("/")[0]
            try:
                user_bytes[user] = user_bytes[user] + content_length
            except:
                user_bytes[user] = content_length
        try:
            urls[path] = urls[path] + 1
        except:
            urls[path] = 1
    return urls, user_bytes


#Here we add another view for displaying the report
from flask import request

@app.route("/report/")
def report():
    #Prevents directory transversal attacks such as /etc/passwd or ../../etc/passwd
    if "/" in request.args.get("filename"):
        return "File not found, we are so sorry."
    
    urls, user_bytes = parse_log_file(request.args.get("filename"))
    user_bytes = sorted(user_bytes.items(), key = lambda item:item[1], reverse=True)    
    return env.get_template("report.html").render(
    humanize=humanize,
    user_bytes=user_bytes,
    urls=urls)

@app.route("/")
def hello():
    return env.get_template("index.html").render(log_files=list_log_files())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
