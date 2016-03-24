import argparse
import codecs #for Jinja
import GeoIP
import gzip
import os
from maprender import render_map
from logparser import LogParser
from jinja2 import Environment, FileSystemLoader

# This will contain main.py and templates
PROJECT_ROOT = os.path.dirname(__file__)

# Following is the directory with log files,
# On Windows substitute it where you downloaded the files
parser = argparse.ArgumentParser(description='Apache2 log parser.')

parser.add_argument('--output', help="This is where we place the output files such as report.html and map.svg", default='build')
parser.add_argument('--path', default="/home/ebarrier/Documents/Python/logs", help='Path to log files')
parser.add_argument('--topurls', help="Find top URL-s", action='store_true')
parser.add_argument('--geoip', help ="Path to file to resolve IPs to country codes", action='store_true', default='/usr/share/GeoIP/GeoIP.dat')
parser.add_argument('--verbose', help="Let's chat", action="store_true")
parser.add_argument('--skip-compressed',
    help="Skip compressed files", action="store_true")
args = parser.parse_args()

try:
    #download list of countries with their IPs
    gi = GeoIP.open(args.geoip, GeoIP.GEOIP_MEMORY_CACHE)
except GeoIP.error:
    print "Failed to open up GeoIP database, are you sure %s exists?" % os.path.realpath(args.geoip)
    exit(254)

# Here we create an instance of the LogParser class
# this object shall contain statistics for one run
logparser = LogParser(gi, keywords = ("Windows", "Linux", "OS X"))

for filename in os.listdir(args.path):
    if not filename.startswith("access."):
        continue
    if filename.endswith(".gz"):
        continue # Skips .gz files to save time in processing
        fh = gzip.open(os.path.join(args.path, filename))
    else:
        fh = open(os.path.join(args.path, filename))

    if args.verbose:
        print "Parsing:", filename

    logparser.parse_file(fh)

if not logparser.urls:
    print "No log entries!"
    exit(254)

def humanize(bytes):
    if bytes<1024:
        return "%d B" % bytes
    elif bytes<1024**2:
        return "%.1f kB" % (bytes / 1024.0)
    elif bytes < 1024**3:
        return "%.1f MB" % (bytes / 1024.0**2)
    else:
        return "%.1f GB" % (bytes / 1024.0**3)


env = Environment(loader=FileSystemLoader(os.path.join(PROJECT_ROOT, "templates")), trim_blocks=True)


# Here we use render_map function from maprender.py to generate colored map
rendered_map = render_map(
    open(os.path.join(PROJECT_ROOT, 'templates', 'map.svg')),
    logparser.countries)


# This is the context variable for our template, these are the only
# variables that can be accessed inside template

context = {
    "map_svg": rendered_map,
    "humanize": humanize, # This is why we use locals() :D
    "keyword_hits": sorted(logparser.d.items(), key=lambda i:i[1], reverse=True),
    "url_hits": sorted(logparser.urls.items(), key=lambda i:i[1], reverse=True),
    "user_bytes": sorted(logparser.user_bytes.items(), key = lambda item:item[1], reverse=True),
}

with codecs.open(os.path.join(args.output, "report.html"), "w", encoding="utf-8") as fh:
    fh.write(env.get_template("report.html").render(context))

    # A more convenient way is to use env.get_template("...").render(locals())
    # locals() is a dict which contains all locally defined variables ;)

os.system("x-www-browser file://" + os.path.realpath("build/report.html") + " &")
