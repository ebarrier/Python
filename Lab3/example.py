import argparse

parser = argparse.ArgumentParser(description='Apache2 log parser.')

parser.add_argument('--path', default="/var/log/Apache2",
                   help='Path to Apache2 log files')

args = parser.parse_args()
print "We are expecting logs from", args.path
