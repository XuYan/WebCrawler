It works like a pipe. User specifies a start url and multiple CSS selectors.
Applying the first CSS selector to the start url webpage will redirect to a second webpage,
to which we apply the second CSS selector will lead us to the third webpage, so on and so forth.
The whole process works recursively util the last CSS selector is used to get final results.

# Web Crawler

One Paragraph of project description goes here

This is a webpage crawler, written with Python, that takes a start webpage and data selectors as inputs and outputs information you care to a file.
The crawler crawls webpages recursively. The whole process works like a pipe. The crawling outputs of previous webpage will serve as inputs to crawling next webpage.
For details, refer to ### Usage

### Prerequisities

Python 2.7.3 at least
BeautifulSoup, argparse, httplib2 lib

### Usage 

The crawler will be run through command line by specifying some necessary and optional arguments

E.g. python crawler.py [args]

Arguments:
	Required Arguments:
		-url: The url of starting webpage. This is the first webpage to start crawling
		-selectors: The crawling instruction string always with the following format
			data_type|data_source|data_org|css_selector
			Crawler accepts multiple selectors for one webpage. When specifying multiple, they should be separated by comma
			
			data_type: value can be either "redirection" or "information"
				   "redirection": data is urls(absolute/relative) that crawler needs to jump to
				   "information": data is the info we cared.
			data_source: value can be either "element" or "attribute"
				     "element": data is stored as the text value in an html tag
				     "attribute": data is stored as the attribute of an html tag
				     		  here, particular attribute name is needed for crawler to extract data
						  the attribute name should be immediately following "attribute" string with space as delimeter
						  E.g. attribute href --- get the href value of a matching html tag
			data_org: value can be either "separate" or "combination". Indicate how to organize extracted data
				  This only make sense when there exist a list of matching tags after applying css selectors
				  Since each matching tag will give us data,
				  we can choose either passing all these data to next webpage (when these data are highly correlated. Will be in one line in file separated by tab)
				                or passing each of them to each of the redirection webpage correspondingly
				  "separate": used when EACH data in list is for one record
				  "combination": used when ALL data in list are for one record
			css_selector: CSS selectors to select html elements in DOM tree

	Optional Arguments:
		-domain: The domain of the website being crawled.
			 This is necessary when current webpage contains redirection links, specified as relative path,
			 that the crawler needs to jump to for further crawling

Examples:
	-domain "http://www.yellowpages.com"
	-url "http://www.yellowpages.com/search?search_terms=event+coordinate&geo_location_terms=bellevue%2C+WA&page=1"
	-css "redirection|attribute href|separate|div.v-card > div.info > h3.n > a"
	     "information|element|combination|div.sales-info > h1, information|attribute href|combination|div.business-card > section > footer > a.email-business"

## Authors

* **Xu Yan** - *Initial work* - [WebCrawler](https://github.com/XuYan/WebCrawler)
