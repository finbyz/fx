# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import re
import requests
from frappe.utils import nowdate, now

class Forward(Document):
	pass
	# def autoname(self):
	# 	self.name = self.ccy1 + "/" + self.ccy2
		
	def before_save(self):
		title = self.ccy1 + "/" + self.ccy2
		self.db_set('title',title)
		
		frappe.db.commit()

@frappe.whitelist()
def add_forward_premium():
	response = requests.get('http://www.finbyz.com/ASPNET/Forex/GetForwardRatesForSingleCurrency.aspx?CurrencyID=2&UserName=apan_imex&Password=0apan@123')

	api_response = response.text
	# print(api_response)
	content = re.findall('(?<=<tr>).*?(?=<\/tr>)', api_response)
	# print(content)
	value = []
	for row in content[1:]:
		x = re.findall('(?<=<td>).*?(?=<\/td>)', row)
		x.append(nowdate())
		value.append(x)

	

	return value

