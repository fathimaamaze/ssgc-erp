from odoo import fields, models, api
from odoo.http import request


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_approval_recs(self):
        data = []
        for rec in self.search([("state", "=", "draft")]):
            data.append({
                'name': rec.name,
                'model': self._name,
                'model_name': "Purchase Order",
                'id': rec.id,
            })
        return data
