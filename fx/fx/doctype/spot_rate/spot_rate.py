# -*- coding: utf-8 -*-
# Copyright (c) 2018, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SpotRate(Document):
	pass
	def before_save(self):
		title = self.ccy1 + "/" + self.ccy2
		self.db_set('title',title)
		
		frappe.db.commit()