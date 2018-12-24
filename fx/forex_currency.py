# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import re
from frappe.model.document import Document
from frappe.utils import nowdate, now

	# def get_currency(self):
		# link = "http://www.finbyz.com/ASPNET/Forex/GetSingleRateForSingleCurrency.aspx?CurrencyID=2&RateType=A&UserName="+self.user_name+"&Password="+self.password
		
		# r = requests.get(link)

		# ask = float(r.text) if r.text else 0.0

		# doc_name = frappe.db.exists('SPOT RATES', {'ccy1': 'EUR', 'ccy2': 'USD', 'posting_date': nowdate()})
		
		# frappe.msgprint(doc_name)
		# spot_rate = None
		
		# if doc_name:
			# spot_rate = frappe.get_doc('SPOT RATES', doc_name)
			# spot_rate.ask = ask
			
			# spot_rate.save()
		
		# else:
			# spot_rate = frappe.new_doc("SPOT RATES")
			# spot_rate.ccy1 = "USD"
			# spot_rate.ccy2 = "INR"
			# spot_rate.ask = ask
			
			# spot_rate.posting_date = nowdate()
			# spot_rate.save()
		
		# frappe.db.set_value(spot_rate.doctype, spot_rate.name, 'timestamp', now())
		# frappe.errprint(now())
		
def set_forex_currency():
	response = requests.get('http://www.finbyz.com/ASPNET/Forex/GetForwardRatesForSingleCurrency.aspx?CurrencyID=2&UserName=apan_imex&Password=0apan@123')

	api_response = response.text

	content = re.findall('(?<=<tr>).*?(?=<\/tr>)', api_response)
	# print(content)
	the_list = []
	for row in content[1:]:
		x = re.findall('(?<=<td>).*?(?=<\/td>)', row)	
		the_list.append(x)

	print(the_list)
	
@frappe.whitelist()	
def forward_before_save():
		finbyz_user = frappe.get_single('Finbyz User')
		user = finbyz_user.user
		password = finbyz_user.password
		currency_pair = frappe.get_list(doctype="Currency Pair", fields=['ccy1', 'ccy2', 'currency_pair_code'], filters=None)

		for cp in currency_pair:	
			response = requests.get('http://www.finbyz.com/ASPNET/Forex/GetForwardRatesForSingleCurrency.aspx?CurrencyID={}&UserName=apan_imex&Password=0apan@123'.format(cp['currency_pair_code']))
			forward_doc_name = frappe.db.exists('Forward', {'ccy1': cp['ccy1'], 'ccy2': cp['ccy2'], 'posting_date': nowdate()})
			forward = None

			api_response = response.text
			content = re.findall('(?<=<tr>).*?(?=<\/tr>)', api_response)
			
			content_list = []
			for row in content[1:]:
				data = re.findall('(?<=<td>).*?(?=<\/td>)', row)
				data.append(nowdate())
				content_list.append(data)

			if forward_doc_name:
				forward = frappe.get_doc('Forward', forward_doc_name)	
				
			else:
				forward = frappe.new_doc("Forward")		
				forward.ccy1 = cp['ccy1']
				forward.ccy2 = cp['ccy2']
				forward.timestamp = now()
				forward.posting_date = nowdate()
	
			forward.set('forward_premium', [])
			for data in content_list:	
				forward.append('forward_premium', {
						"ref_month": data[0],
						"fwd_bid": data[1],
						"fwd_ask": data[2],
						"date": data[3]
					})

			forward.save()
			frappe.db.set_value('Forward', forward_doc_name, 'timestamp', now())

@frappe.whitelist()	
def spot_rate_before_save():
	finbyz_user = frappe.get_single('Finbyz User')
	user = finbyz_user.user
	password = finbyz_user.password
	currency_pair = frappe.get_list(doctype="Currency Pair", fields=['ccy1', 'ccy2', 'currency_pair_code'], filters=None)
	for cp in currency_pair:
		response = requests.get('http://www.finbyz.com/ASPNET/Forex/GetSingleRateForSingleCurrency.aspx?CurrencyID={}&RateType=A&UserName=apan_imex&Password=0apan@123'.format(cp['currency_pair_code']))

		ask = float(response.text) if response.text else 0.0

		sr_doc_name = frappe.db.exists('Spot Rate', {'ccy1': cp['ccy1'], 'ccy2': cp['ccy2'], 'posting_date': nowdate()})
		spot_rate = None
		
		if sr_doc_name:
			spot_rate = frappe.get_doc('Spot Rate', sr_doc_name)
			spot_rate.ask = ask
			spot_rate.save()
		
		else:
			spot_rate = frappe.new_doc("Spot Rate")
			spot_rate.ccy1 = cp['ccy1']
			spot_rate.ccy2 = cp['ccy2']
			spot_rate.ask = ask
			spot_rate.posting_date = nowdate()
			spot_rate.save()			
		frappe.db.set_value(spot_rate.doctype, spot_rate.name, 'timestamp', now())