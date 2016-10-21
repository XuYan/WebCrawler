import re

class url_generator():
	def __init__(self, url_template):
		self.url_template = url_template
		self.varied_fields = re.findall(r'{([^{}]*)}', self.url_template)
		self.__setup()

	def __setup(self):
		self.field_values_dict = {}
		for i in range(len(self.varied_fields)):
			field_name = self.varied_fields[i]
			if field_name == "city":
				self.field_values_dict[field_name] = self.__readFile(field_name)
			elif field_name == "page":
			 	self.field_values_dict[field_name] = list(range(1, 3))
			else:
				raise ValueError("Invalid field name")

	def __readFile(self, file_name):
		field_values = []
		with open(file_name) as input:
			for value in input.readlines():
				field_values.append(value.strip('\n'))
		return field_values

	def generate(self):
		""" Generate a list of base urls """
		base_urls = []
		for city in self.field_values_dict["city"]:
			temp1 = self.url_template.replace("{city}", city.replace(' ', '+'))
			for page in self.field_values_dict["page"]:
				temp2 = temp1.replace("{page}", str(page))
				base_urls.append(temp2)
		# print(base_urls)
		return  base_urls