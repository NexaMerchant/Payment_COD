# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_cod import utils as cod_utils
from odoo.addons.payment_cod.const import PAYMENT_STATUS_MAPPING

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # See https://developer.cod.com/docs/api-basics/notifications/ipn/IPNandPDTVariables/
    # this field has no use in Odoo except for debugging
    cod_type = fields.Char(string="Cash on Delivery Transaction Type")

    def _get_specific_processing_values(self, processing_values):
        """ Override of `payment` to return the Cash on Delivery-specific processing values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the
                                       transaction.
        :return: The dict of provider-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_processing_values(processing_values)
        if self.provider_code != 'cod':
            return res

        partner_first_name, partner_last_name = payment_utils.split_partner_name(self.partner_name)
        payload = {
            'intent': 'CAPTURE',
            'purchase_units': [
                {
                    'reference_id': self.reference,
                    'description': f'{self.company_id.name}: {self.reference}',
                    'amount': {
                        'currency_code': self.currency_id.name,
                        'value': self.amount,
                    },
                    'payee':  {
                        'display_data': {
                            'business_email':  self.provider_id.company_id.email,
                            'brand_name': self.provider_id.company_id.name,
                        },
                        'email_address': cod_utils.get_normalized_email_account(self.provider_id)
                    },
                },
            ],
            'payment_source': {
                'cod': {
                    'experience_context': {
                        'shipping_preference': 'NO_SHIPPING',
                    },
                    'email_address': self.partner_email,
                    'name': {
                        'given_name': partner_first_name,
                        'surname': partner_last_name,
                    },
                    'address': {
                        'address_line_1': self.partner_address,
                        'admin_area_1': self.partner_state_id.name,
                        'admin_area_2': self.partner_city,
                        'postal_code': self.partner_zip,
                        'country_code': self.partner_country_id.code,
                    },
                },
            },
        }
        _logger.info(
            "Sending '/checkout/orders' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(payload)
        )
        idempotency_key = payment_utils.generate_idempotency_key(
            self, scope='payment_request_order'
        )
        order_data = self.provider_id._cod_make_request(
            '/v2/checkout/orders', json_payload=payload, idempotency_key=idempotency_key
        )
        _logger.info(
            "Response of '/checkout/orders' request for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(order_data)
        )
        return {'order_id': order_data['id']}

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of `payment` to find the transaction based on Cash on Delivery data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: payment.transaction
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'cod' or len(tx) == 1:
            return tx

        reference = notification_data.get('reference_id')
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'cod')])
        if not tx:
            raise ValidationError(
                "Cash on Delivery: " + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """ Override of `payment` to process the transaction based on Cash on Delivery data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'cod':
            return

        if not notification_data:
            self._set_canceled(state_message=_("The customer left the payment page."))
            return

        amount = notification_data.get('amount').get('value')
        currency_code = notification_data.get('amount').get('currency_code')
        assert amount and currency_code, "Cash on Delivery: missing amount or currency"
        assert self.currency_id.compare_amounts(float(amount), self.amount) == 0, \
            "Cash on Delivery: mismatching amounts"
        assert currency_code == self.currency_id.name, "Cash on Delivery: mismatching currency codes"

        # Update the provider reference.
        txn_id = notification_data.get('id')
        txn_type = notification_data.get('txn_type')
        if not all((txn_id, txn_type)):
            raise ValidationError(
                "Cash on Delivery: " + _(
                    "Missing value for txn_id (%(txn_id)s) or txn_type (%(txn_type)s).",
                    txn_id=txn_id, txn_type=txn_type
                )
            )
        self.provider_reference = txn_id
        self.cod_type = txn_type

        # Force Cash on Delivery as the payment method if it exists.
        self.payment_method_id = self.env['payment.method'].search(
            [('code', '=', 'cod')], limit=1
        ) or self.payment_method_id

        # Update the payment state.
        payment_status = notification_data.get('status')

        if payment_status in PAYMENT_STATUS_MAPPING['pending']:
            self._set_pending(state_message=notification_data.get('pending_reason'))
        elif payment_status in PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled()
        else:
            _logger.info(
                "received data with invalid payment status (%s) for transaction with reference %s",
                payment_status, self.reference
            )
            self._set_error(
                "Cash on Delivery: " + _("Received data with invalid payment status: %s", payment_status)
            )
