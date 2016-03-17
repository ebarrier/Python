import os
from flask import Flask
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"), trim_blocks=True)

app = Flask(__name__)

def list_log_files():
    #Generator has yield management
    #It basically returns a list of files we are interested in
    for filename in os.listdir("/home/ebarrier/Documents/Python"):
        if filename.endswith(".log"):
            yield filename
        if filename.endswith(".gz"):
            yield filename

@app.route("/")
def hello():
    return env.get_template("index.html").render(log_files=list_log_files())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
