# -*- coding: utf-8 -*-
# from odoo import http


# class PaymentCod(http.Controller):
#     @http.route('/payment_cod/payment_cod', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/payment_cod/payment_cod/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('payment_cod.listing', {
#             'root': '/payment_cod/payment_cod',
#             'objects': http.request.env['payment_cod.payment_cod'].search([]),
#         })

#     @http.route('/payment_cod/payment_cod/objects/<model("payment_cod.payment_cod"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('payment_cod.object', {
#             'object': obj
#         })

