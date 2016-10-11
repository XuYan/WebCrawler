import argparse
import httplib2
from bs4 import BeautifulSoup
from enum import Enum

class DataType(Enum):
	redirection = 1
	information = 2

class DataSource(Enum):
	attribute = 1
	element = 2

class Selector():
	def __init__(self, css_selector):
		css_fields = css_selector.split('|')
		self.css = css_fields[0]
		self.data_type = css_fields[1]
		self.data_source = css_fields[2]

class Crawler():
	def __init__(self, css_selectors):
		self.css_selectors = css_selectors
		self.depth = len(css_selectors)
		self.output = open('results', 'w')
		self.http = httplib2.Http(".cache")
		self.result = []

	def crawl(self, url, level, information_list):
		"""
			Parameters
			----------
			level: int
				the current crawling recursion level
			url: string
				the url to redirect current webpage
			information_list: list
				the list of information for a single data point
		"""
		print("Crawling level " + str(level) + "...")
		resp, content = self.http.request(url)
		html_doc = BeautifulSoup(content, "html.parser")

		redirect_urls = []
		info_count = 0 # The total number of newly-added info in this level
		data_list = css_selectors[level].split(',')
		for data in data_list:
			selector = Selector(data)
			values = self.getValues(html_doc, selector.css, selector.data_source)
			for value in values:
				if selector.data_type == DataType.redirection:
					""" Redirection link """
					redirect_urls.append(value)
				else:
					""" Info """
					info_count += 1
					information_list.append(value)

		if len(redirect_urls) == 0:
			self.write(information_list)
			del information_list[-info_count: ]
			return
		else:
			for redirect_url in redirect_urls:
				self.crawl(redirect_url, level + 1, information_list)
			del information_list[-info_count: ]

	def write(self, information_list):
		output_str = "\t".join(information_list) + "\n"
		self.output.write(output_str.encode("UTF-8"))

	def getValues(self, html_doc, css_selector, data_source):
		"""	Pull tag's text content / attribute value from target elements """
		values = []
		target_elements = html_doc.select(css_selector)
		for target_element in target_elements:
			if data_source == DataSource.attribute:
				attr_name = data_source.split(' ')[1]
				values.append(target_element.attr[attr_name])
			else:
				values.append(target_element.text)
		return values

def parseArgs():
	""" Parse command line arguments """
	# TODO: Add usage and more robust error checking logic
	# Last level shouldn't have any redirection link
	parser = argparse.ArgumentParser(description='Web crawler')
	parser.add_argument('-url', nargs='?', required=True, help='the url of a webpage to start with')
	parser.add_argument('-css', nargs='+', required=True, help='the list of css to capture webpage information')
	args = parser.parse_args();

	return (args.url, args.css)

if __name__ == '__main__':
	base_url, css_selectors = parseArgs()
	crawler = Crawler(css_selectors)
	crawler.crawl(base_url, 0, [])
	crawler.output.close()