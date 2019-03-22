# -*- coding: utf-8 -*-
from odoo import http

# class ProCatalia(http.Controller):
#     @http.route('/pro_catalia/pro_catalia/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pro_catalia/pro_catalia/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pro_catalia.listing', {
#             'root': '/pro_catalia/pro_catalia',
#             'objects': http.request.env['pro_catalia.pro_catalia'].search([]),
#         })

#     @http.route('/pro_catalia/pro_catalia/objects/<model("pro_catalia.pro_catalia"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pro_catalia.object', {
#             'object': obj
#         })