from odoo import fields, models, api
from odoo.http import request


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    @api.model
    def get_approval_recs(self):
        data = []
        for rec in self.search([("state", "=", "draft")]):
            data.append({
                'name': rec.name,
                'model': self._name,
                'model_name': "Purchase Requisition",
                'id': rec.id,
            })
        return data
