import argparse

class crawler():
	def __init__(self, url, css_selectors):
		self.url = url
		self.css_selectors = css_selectors

	def crawl(self):
		print("Crawling...")


def parseArgs():
	""" Parse command line arguments """
	# TODO: Add usage and more robust error checking logic
	parser = argparse.ArgumentParser(description='Web crawler')
	parser.add_argument('-url', nargs='?', required=True, help='the url of a webpage to start with')
	parser.add_argument('-css', nargs='+', required=True, help='the list of css to capture webpage information')
	args = parser.parse_args();

	return (args.url, args.css)

if __name__ == '__main__':
	url, css_selectors = parseArgs()
	crawler = crawler(url, css_selectors)
	crawler.crawl()