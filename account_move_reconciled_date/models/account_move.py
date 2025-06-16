import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_date = fields.Date(compute="_compute_payment_date", store=True)
    reconcile_date = fields.Date(compute="_compute_payment_date", store=True)

    @api.depends("payment_state")
    def _compute_payment_date(self):
        for move in self:
            # Get move lines that are reconciled
            move_lines = self.env["account.move.line"].browse(move.line_ids._reconciled_lines())

            # Only check move lines from bank journal
            move_lines = move_lines.filtered(lambda line: line.journal_id.type == "bank")

            if move_lines:
                move.payment_date = max(move_lines.mapped("date"))
                move.reconcile_date = max(move_lines.mapped("write_date"))
