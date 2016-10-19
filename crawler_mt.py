#!/usr/bin/python
import argparse
import httplib2
from bs4 import BeautifulSoup
import time
import threading

def defensiveCopy(info_list):
	copy = []
	for info in info_list:
		copy.append(info)
	return copy

class CrawlThread(threading.Thread):
	terminated = False
	def __init__(self, crawler, info_list, current_level_info, next_url, next_level):
		"""
			Parameters
			----------
			info_list: list
				Accumulated information up to previous level
			current_level_info: list
				New information from this level. To be added to {info_list}
		"""
		threading.Thread.__init__(self)
		self.crawler = crawler
		self.current_level_info = current_level_info
		self.info_list = defensiveCopy(info_list)
		self.next_url = next_url
		self.next_level = next_level
		self.daemon = True

	def run(self):
		if not CrawlThread.terminated:
			self.info_list.extend(self.current_level_info)
			self.crawler.crawl(self.next_url, self.next_level, self.info_list)

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
		self.write_lock = threading.Lock()

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
		resp, content = httplib2.Http().request(url)
		html_doc = BeautifulSoup(content, "html.parser")

		selectors = self.createSelectorObjects(css_selectors[level].split(',')) # All selectors in current level
		redirection_selector_index = self.getRedirectionDataIndex(selectors)

		if redirection_selector_index != -1: # We'll grab data and go to next level
			redirection_selector = selectors[redirection_selector_index]
			redirection_links = [self.domain + r_path for r_path in self.getValues(html_doc, redirection_selector)]
			redirection_link_count = len(redirection_links)

			self.moveToLast(selectors, redirection_selector_index)

			(target_length, list_info_list) = self.getListInfoList(
				html_doc, selectors[0:-1], expect_length = redirection_link_count)
			info_count = len(list_info_list) # The total number of newly-added info in this level

			for i in range(redirection_link_count):
				current_level_info = []
				for j in range(info_count):
					current_level_info.append(list_info_list[j][i])
				crawl_thread = CrawlThread(self, information_list, current_level_info, redirection_links[i], level + 1)
				crawl_thread.start()

		else: # This is the last level in our crawling process
			(target_length, list_info_list) = self.getListInfoList(html_doc, selectors)
			info_count = len(list_info_list) # The total number of newly-added info in this level

			for i in range(target_length):
				for j in range(info_count):
					information_list.append(list_info_list[j][i])
				self.write(information_list)
				del information_list[-info_count: ]

	def getListInfoList(self, html_doc, information_selector_list, expect_length = None):
		"""
			Get a list of information list.
			The size of each information list should be {expect_length}
		"""
		ret_list = []
		for info_selector in information_selector_list:
			ret_list.append(self.getValues(html_doc, info_selector))
		target_length = self.__checkValidity(information_selector_list, ret_list, expect_length)
		if target_length <= 0:
			raise ValueError("Invalid information list size")
		self.__adjustLength(ret_list, target_length)
		return (target_length, ret_list)

	def __checkValidity(self, info_selector_list, list_info_list, expect_length):
		"""
			Check if applying info selectors give us expected result
			Parameters
			----------
			info_selector_list: list
				a list of info selectors
			list_info_list: list of list
				a list of info list that each info list is obtained
				by applying each info selector to current webpage correspondingly
			expect_length: int
				expected length of each info list
				Can be None
			Return
			----------
			if not valid, non-positive
			if valid, positive
		"""
		separate_length = -1
		combination_length = -1
		for i in range(len(info_selector_list)):
			info_selector = info_selector_list[i]
			info_list = list_info_list[i]
			if info_selector.data_org == "combination":
				assert (len(info_list) == 1), "Information list with combination org doesn't give a list of size 1"
				combination_length = 1
			else: # data_org is "separate"
				if separate_length == -1:
					separate_length = len(info_list)
				assert (separate_length == len(info_list)), "Inconsistent information list size"

		if expect_length is None:
			return separate_length if separate_length != -1 else combination_length
		else: # expect_length is not None. In other words, current webpage contains redirection link(s)
			if separate_length != -1:
				assert (separate_length == expect_length), "Info list size not match the number of redirection links"
			return expect_length

	def __adjustLength(self, list_info_list, target_length):
		""" Adjust info list of size 1 to be {target_length} """
		for i in range(len(list_info_list)):
			if len(list_info_list[i]) != target_length:
				list_info_list[i] = list_info_list[i] * target_length

	def getValues(self, html_doc, selector):
		"""
			Pull tag's text content / attribute value from target elements
		"""
		values = []
		for target_element in html_doc.select(selector.css):
			if selector.data_source.startswith("attribute"):
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
		self.write_lock.acquire()
		self.output.write(output_str.encode("UTF-8"))
		self.write_lock.release()

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
	try:
		base_url, css_selectors, domain = parseArgs()
		crawler = Crawler(css_selectors, domain)
		start_time = time.time()
		crawler.crawl(base_url, 0, [])
		while threading.active_count() > 1:
			time.sleep(0.5)
		end_time = time.time()
		print("Running Time: " + str(end_time - start_time) + " seconds")
		crawler.output.close()
	except KeyboardInterrupt:
		print("Program is terminated with ctrl + c")
		CrawlThread.terminated = True
		raise