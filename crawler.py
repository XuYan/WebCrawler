import argparse

parser = argparse.ArgumentParser(description='Web crawler')
parser.add_argument('-url', nargs='?', required=True, help='the url of a webpage to start with')
parser.add_argument('-css', nargs='+', required=True, help='the list of css to capture webpage information')

parser.parse_args('-url www.google.com -css #id1 .class1'.split());