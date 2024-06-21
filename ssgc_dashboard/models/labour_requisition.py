from odoo import fields, models, api
from odoo.http import request


class LabourRequisition(models.Model):
    _inherit = "labour.requisition"

    @api.model
    def get_approval_recs(self):
        data = []
        for rec in self.search([("state", "=", "draft")]):
            data.append({
                'name': rec.name,
                'model': self._name,
                'model_name': "Labour Requisition",
                'id': rec.id,
            })
        return data
