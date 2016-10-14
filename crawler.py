#!/usr/bin/python
import argparse
import httplib2
from bs4 import BeautifulSoup
from enum import Enum

class Selector():
	def __init__(self, css_selector):
		self.data_type, self.data_source, self.data_org, self.css = css_selector.split('|')

	def isForRedirectionData(self):
		return self.data_type == "redirection"

class Crawler():
	def __init__(self, css_selectors, domain):
		self.css_selectors = css_selectors
		self.domain = "" if domain is None else domain
		self.output = open('results', 'w')
		self.http = httplib2.Http(".cache")

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

		selectors = self.createSelectorObjects(css_selectors[level].split(',')) # All selectors in current level
		redirection_selector_index = self.getRedirectionDataIndex(selectors)

		if redirection_selector_index != -1: # We'll grab data and go to next level
			redirection_selector = selectors[redirection_selector_index]
			redirection_links = [self.domain + r_path for r_path in self.getValues(html_doc, redirection_selector)]
			redirection_link_count = len(redirection_links)

			self.moveToLast(selectors, redirection_selector_index)

			list_info_list = self.getListInfoList(html_doc, selectors[0:-1], redirection_link_count)
			info_count = len(list_info_list) # The total number of newly-added info in this level

			for i in range(redirection_link_count):
				for j in range(info_count):
					information_list.append(list_info_list[j][i])
				self.crawl(redirection_links[i], level + 1, information_list)
				del information_list[-info_count : ]

		else: # This is the last level in our crawling process
			max_info_list_len = self.getMaxInfoListLength(html_doc, selectors)
			list_info_list = self.getListInfoList(html_doc, selectors, max_info_list_len)
			info_count = len(list_info_list) # The total number of newly-added info in this level

			for i in range(max_info_list_len):
				for j in range(info_count):
					information_list.append(list_info_list[j][i])
				self.write(information_list)
				del information_list[-info_count: ]

	def getMaxInfoListLength(self, html_doc, information_selector_list):
		max_length = -1
		for info_selector in information_selector_list:
			value_list = self.getValues(html_doc, info_selector)
			max_length = max(max_length, len(value_list))
		return max_length

	def getListInfoList(self, html_doc, information_selector_list, expect_length):
		"""
			Get a list of information list.
			The length of each information list should be {expect_length}
		"""
		ret_list = []
		for info_selector in information_selector_list:
			value_list = self.getValues(html_doc, info_selector)
			if info_selector.data_org == "combination":
				if len(value_list) != 1:
					print("WARNING: info selector with combination org doesn't give a list of length 1")
					ret_list.append([""] * expect_length)
				else:
					ret_list.append(value_list * expect_length)
			else:
				assert len(value_list) == expect_length
				ret_list.append(value_list)
		return ret_list

	def getValues(self, html_doc, selector):
		"""
			Pull tag's text content / attribute value from target elements
		"""
		values = []
		for target_element in html_doc.select(selector.css):
			if selector.data_source.startswith("attribute"):
				print(target_element)
				attr_name = selector.data_source.split(' ')[1]
				values.append(target_element.attrs[attr_name])
			else:
				values.append(target_element.text)
		if selector.data_org == "combination" and len(values) != 0:
			return ["\t".join(values)]
		return values

	def getRedirectionDataIndex(self, selector_list):
		""" Get the index of the only redirection data selector in given list (-1 if there is none) """
		for index in range(len(selector_list)):
			selector = selector_list[index]
			if selector.isForRedirectionData():
				return index
		return -1

	def createSelectorObjects(self, selector_str_list):
		""" Create selector object list from given serialized selector list """
		selector_list = []
		for selector_str in selector_str_list:
			selector_list.append(Selector(selector_str))
		return selector_list

	def moveToLast(self, selector_objs, index):
		""" Swap the selector at {index} with the last selector in {selector_objs} """
		last_index = len(selector_objs) - 1
		selector_objs[index], selector_objs[last_index] = selector_objs[last_index], selector_objs[index]

	def write(self, information_list):
		output_str = "\t".join(information_list) + "\n"
		self.output.write(output_str.encode("UTF-8"))

def parseArgs():
	""" Parse command line arguments """
	# TODO: Add usage and more robust error checking logic
	# Last level shouldn't have any redirection link
	# Any level shouldn't have more than one redirection link
	# Checking if given data type is valid enum
	parser = argparse.ArgumentParser(description='Web crawler')
	parser.add_argument('-url', nargs='?', required=True, help='the url of a webpage to start with')
	parser.add_argument('-css', nargs='+', required=True, help='the list of css to capture webpage information')
	parser.add_argument('-domain', nargs='?', help='the base domain for each relative redirection path')
	args = parser.parse_args();

	return (args.url, args.css, args.domain)

if __name__ == '__main__':
	base_url, css_selectors, domain = parseArgs()
	crawler = Crawler(css_selectors, domain)
	crawler.crawl(base_url, 0, [])
	crawler.output.close()