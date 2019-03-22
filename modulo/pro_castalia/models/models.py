# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare, pycompat

#MODELO DE SALE.ORDER
class SaleOrder(models.Model):
	_inherit = 'sale.order'

	id_client	   = fields.Integer(string="ID_client", compute="_id_client")
	amount_notes	= fields.Float(string="Credito total", compute="_amount_total_notes")
	credit_notes	= fields.Many2one('account.invoice', string="Nota de credito")
	amount_note_now = fields.Float(string="Credito de la nota", compute="_amount_note")

	@api.one
	@api.depends('partner_id')
	def _id_client(self):
		self.id_client = self.partner_id.id

	@api.onchange('partner_id')
	def _amount_total_notes(self):
		domain = [('partner_id', '=', self.partner_id.id),('type','=','out_refund'),('state','=','open')]
		res = self.env['account.invoice'].search(domain)
		total = 0
		for refund in res:
			total += refund.amount_total
		self.amount_notes = total

	@api.one
	@api.depends('credit_notes')
	def _amount_note(self):
		self.amount_note_now = self.credit_notes.amount_total


#MODELO ACCOUNT.INVOICE
class AccountInvoice2(models.Model):
	_inherit = 'account.invoice'

	id_nota = fields.Integer(string="id_nota")
	nota = fields.Char(string="Nota que se aplico")
	amount_note = fields.Monetary(string="Monto de nota")

	@api.multi
	def name_get(self):
		result = []
		for record in self:
			record_name = str(record.name) + '   |   ' + str(record.amount_total)
			result.append((record.id, record_name))
		return result

	@api.one
	@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding','currency_id', 'company_id', 'date_invoice', 'type')
	def _compute_amount(self):

		for order in self:
			note = order.search([('id', '=', self.refund_invoice_id.id),('type','=', 'out_refund')])
		self.write({'amount_note': note.amount_total})	
		round_curr = self.currency_id.round
		self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
		self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
		total = self.amount_untaxed + self.amount_tax - self.amount_note
		if self.refund_invoice_id:
			self.update({'amount_total': total})
		else:	
			self.amount_total = self.amount_untaxed + self.amount_tax
		amount_total_company_signed = self.amount_total
		amount_untaxed_signed = self.amount_untaxed
		if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
			currency_id = self.currency_id.with_context(date=self.date_invoice)
			amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
			amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
		sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		self.amount_total_company_signed = amount_total_company_signed * sign
		self.amount_total_signed = self.amount_total * sign
		self.amount_untaxed_signed = amount_untaxed_signed * sign

	@api.one
	def action_invoice_open(self):
		for order in self:
			id = order.search([('id', '=', self.refund_invoice_id.id)])
			if id:
				order.write({'state':'paid'})
		return super(AccountInvoice2, self).action_invoice_open()		
	
	
