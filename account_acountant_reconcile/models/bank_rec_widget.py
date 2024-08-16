import logging

from odoo import models

_logger = logging.getLogger(__name__)


class BankRecWidget(models.Model):
    _inherit = "bank.rec.widget"

    def _action_trigger_matching_rules(self):
        self.ensure_one()
        if self.st_line_id.is_reconciled:
            return

        payment_ref = self.st_line_id.payment_ref
        amount = self.st_line_id.amount
        matching_lines = self.env['account.move.line'].search([
            ("amount_residual", "=", amount),
            ("name", "=", payment_ref),
            ("move_type", "=", "out_invoice")
        ])

        _logger.warning([payment_ref, amount, matching_lines])

        if len(matching_lines) == 1:
            invoice_line = matching_lines[0]
            bank_line = self.st_line_id.move_id.line_ids.filtered(lambda: l.credit)


            # _logger.warning([l for l in matching_lines])
            # self.env["account.move.line"].create({
            #     "name": payment_ref,
            #     "account_id": line.account_id.id,
            #     "move_id": self.st_line_id.move_id.id,
            #     "credit": amount,
            # })
            # matching_lines.reconcile()
            # line = matching_lines[0]
            # self.js_action_reconcile_st_line(
            # self.st_line_id.id,
            # {
            #     'to_reconcile': [(0, line.id)],
            #     'partner_id': line.partner_id.id,
            #     'command_list': [],
            #     'exchange_diff': {0:{
            #             'amount_residual': line.balance,
            #             'amount_residual_currency': line.amount_currency,
            #             'analytic_distribution': line.analytic_distribution,
            #         }}
            # },
            # )
        

        return super()._action_trigger_matching_rules()
