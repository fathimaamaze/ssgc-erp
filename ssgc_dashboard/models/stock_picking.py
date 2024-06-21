from odoo import fields, models, api
from odoo.http import request


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def get_approval_recs(self):
        data = []
        # for rec in self.search([("picking_type_code", "=", "outgoing"), ("state", "=", "draft")]):
        for rec in self.search([("state", "=", "draft")]):
            data.append({
                'name': rec.name,
                'model': self._name,
                'model_name': "Stock Picking",
                'id': rec.id,
            })
        return data
