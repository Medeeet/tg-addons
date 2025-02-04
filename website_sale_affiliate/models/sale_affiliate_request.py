# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from datetime import timedelta

from odoo import fields, models
from odoo.http import request


class AffiliateRequest(models.Model):
    _name = "sale.affiliate.request"
    _order = "create_date desc"
    _description = "Sale Affiliate Request"

    name = fields.Char(
        required=True,
        index=True,
        help='Name corresponds with the "aff_key" value of the url used, if '
        "present. Otherwise, name is determined by the sequence selected in "
        "the parent affiliate record",
    )
    affiliate_id = fields.Many2one(
        "sale.affiliate",
        string="Affiliate",
        required=True,
        help="Affiliate that referred request",
    )
    date = fields.Datetime(
        string="Start Date",
        required=True,
        default=lambda self: fields.Datetime.now(),
        help="Date and time of initial request",
    )
    ip = fields.Char(
        string="Client IP",
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            "REMOTE_ADDR",
        ),
    )
    referrer = fields.Char(
        default=lambda self: request.httprequest.headers.environ.get(
            "HTTP_REFERER",
        ),
        help="Request session referrer header",
    )
    user_agent = fields.Char(
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            "HTTP_USER_AGENT",
        ),
        help="Request session user agent",
    )
    accept_language = fields.Char(
        required=True,
        default=lambda self: request.httprequest.headers.environ.get(
            "HTTP_ACCEPT_LANGUAGE",
        ),
        help="Request session accept language",
    )
    sale_ids = fields.One2many(
        "sale.order",
        "affiliate_request_id",
        string="Sales",
        help="Qualified conversions generated as a result of affiliate request",
    )

    def _conversions_qualify(self):
        self.ensure_one()

        valid_hours = self.affiliate_id.valid_hours
        valid_sales = self.affiliate_id.valid_sales
        datetime_start = self.date
        datetime_delta = timedelta(hours=valid_hours)
        expiration = datetime_start + datetime_delta

        qualified_sales = valid_sales < 0 or len(self.sale_ids) < valid_sales
        qualified_time = valid_hours < 0 or fields.Datetime.now() < expiration

        return qualified_sales and qualified_time

    def current_qualified(self):
        if not request:
            return

        try:
            current_id = request.session["affiliate_request"]
        except KeyError:
            return

        current = self.search([("id", "=", current_id)], limit=1)
        if not current:
            return

        if current._conversions_qualify():
            return current
        return
