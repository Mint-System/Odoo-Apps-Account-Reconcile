import logging

from odoo import models

_logger = logging.getLogger(__name__)


class BankRecWidget(models.Model):
    _inherit = "bank.rec.widge"

    def _action_trigger_matching_rules(self):
        res = super()._action_trigger_matching_rules()
        _logger.warning("RECONCILE")
        return res
