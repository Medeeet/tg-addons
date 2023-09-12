from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    x_payment_reference = fields.Many2many(
        "payment.transaction",
        string="Payment Transaction",
        compute="_compute_transactions",
          mpute_sudo=True,
    )
    x_payment_reference_done = fields.Many2many(
        "payment.transaction",
        string="Confirmed Payments",
        compute="_compute_transactions",
        compute_sudo=True,
    )

    @api.depends("sale_order_id", "sale_order_id.state")
    def _compute_transactions(self):
        Transactions = self.env["payment.transaction"]
        txs = Transactions.search([("sale_order_ids", "in", self.mapped("sale_order_id").ids)])
        for r in self:
            so_txs = txs.filtered(lambda x: r.sale_order_id in x.sale_order_ids)
            r.x_payment_reference = so_txs
            r.x_payment_reference_done = so_txs.filtered(lambda x: x.state == "done")
