# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import db
from frappe.model.document import Document
from frappe.utils import flt
from datetime import timedelta, date, datetime, time
from frappe.utils import nowdate, add_days, getdate, get_time, add_months

class ForwardBooking(Document):
	def on_submit(self):
		for row in self.forward_booking_underlying:
			doc = frappe.get_doc(row.link_to, row.document)
			amount_hedged = flt(doc.amount_hedged) + flt(row.amount_covered)
			amount_unhedged = flt(doc.grand_total) - flt(amount_hedged) - flt(doc.advance_paid) - flt(doc.natural_hedge)
			doc.amount_hedged = flt(amount_hedged)
			doc.amount_unhedged = flt(amount_unhedged)
			doc.save()
			frappe.db.commit()
				
	def on_cancel(self):
		for row in self.forward_booking_underlying:
			doc = frappe.get_doc(row.link_to, row.document)
			amount_hedged = flt(doc.amount_hedged) - flt(row.amount_covered)
			amount_unhedged = flt(doc.grand_total) - flt(amount_hedged) - flt(doc.advance_paid) - flt(doc.natural_hedge)
			doc.amount_hedged = flt(amount_hedged)
			doc.amount_unhedged = flt(amount_unhedged)
			doc.save()
			frappe.db.commit()

	def before_save(self):
	
		# Calculate Total Underlying
		total_underlying = 0.0
		for row in self.forward_booking_underlying:
			total_underlying += flt(row.amount_covered)
			
		self.total_underlying = flt(total_underlying)
		
		# Calculate Total Cancelled Amount & Average Rate
		total = 0.0
		inr_total = 0.0
		
		for row in self.cancellation_details:
			total += flt(row.cancel_amount)
			inr_total += flt(row.inr_amount)
		
		self.total_cancelled = flt(total)
		if self.total_cancelled>0:
			self.can_avg_rate = flt(inr_total) / flt(total)
			# Calculate Cancellation Loss Profit
			rate_diff = 0.0
			if self.hedge == "Export":
				rate_diff = flt(self.booking_rate) - flt(self.can_avg_rate)
			else:
				rate_diff = flt(self.can_avg_rate) - flt(self.booking_rate)
			
			self.rate_diff = rate_diff
			self.cancellation_profit_or_loss = flt(rate_diff) * flt(self.total_cancelled)
		
		
		# Calculate Outstanding Amount
		# outstanding = flt(self.amount) - flt(self.total_utilization)-flt(self.total_cancelled)
		# self.amount_outstanding = flt(outstanding)

		
		# Set Status as closed if no outstanding
		if self.amount_outstanding <= 0:
			self.status = "Closed"
		else:
			self.status = "Open"