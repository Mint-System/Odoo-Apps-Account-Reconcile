import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def _cron_try_auto_reconcile_statement_lines(self, batch_size=None, limit_time=0):
        """
        OVERWRITE: Replace the reconcilation method. Reconcile only based on amount and reference.
        """

        # Get all unreconciled bank statement lines
        st_line_ids = self.search(
            [
                ("is_reconciled", "=", False),
                (
                    "create_date",
                    ">",
                    fields.Datetime.now().date() - relativedelta(months=3),
                ),
            ]
        )

        # Get all unreconciled invoice lines
        unreconciled_lines = self.env["account.move.line"].search(
            [
                ("reconciled", "=", False),
                ("parent_state", "=", "posted"),
                ("is_account_reconcile", "=", True),
            ]
        )

        for st_line_id in st_line_ids:

            # Get payment reference and amount
            payment_ref = st_line_id.payment_ref
            amount = st_line_id.amount

            # Find invoice line by reference and amount
            matching_lines = unreconciled_lines.filtered(
                lambda l: l.name == payment_ref and l.amount_residual == amount
            )

            # _logger.warning([st_line_id, payment_ref, amount, matching_lines])

            # If only one invoice lines is found reconcile it
            if len(matching_lines) == 1:
                invoice_line = matching_lines[0]

                # Update the bank line of the bank statement post
                bank_line = st_line_id.line_ids.filtered(lambda l: l.debit > 0)
                if bank_line:
                    bank_line.write({"partner_id": invoice_line.partner_id.id})

                # Update the suspense line of the bank statement post
                suspense_line = st_line_id.line_ids.filtered(lambda l: l.credit > 0)
                if suspense_line:
                    suspense_line.write(
                        {
                            "partner_id": invoice_line.partner_id.id,
                            "account_id": invoice_line.account_id.id,
                        }
                    )

                    # Reconcile the suspense and invoice lien
                    lines = suspense_line + invoice_line
                    lines.reconcile()
                    _logger.debug("Reconciled lines: %s", lines)
