from odoo import models, fields, api

class PaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def create_cod_payment_method(self):
        if not self.search([('code', '=', 'cod')]):
            payment_method_vals = {
                'name': 'Cash on Delivery',
                'code': 'cod',
                'payment_type': 'inbound',  # or 'outbound' based on your requirement
            }
            payment_method = self.create(payment_method_vals)
            return payment_method