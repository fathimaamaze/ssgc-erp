from odoo import fields, models, api
from odoo.http import request


class Users(models.Model):
    _inherit = "res.users"

    def get_contracting_dashboard_data(self):
        project_ids = self.env['project.project'].search([])
        user_ids = self.search([])
        warehouse_ids = self.search([])

        return {
            'welcome_msg': self.name,
            'cards': [
                {
                    'name': 'Active Project',
                    'value': len(project_ids),
                    'id': 'no_of_unit',
                    'class': 'card-dark-reb'
                },
                {
                    'name': 'Active Users',
                    'value': len(user_ids),
                    'id': 'no_of_unit',
                    'class': 'card-gray-reb'
                },
                {
                    'name': 'Warehouse',
                    'value': len(warehouse_ids),
                    'id': 'no_of_unit',
                    'class': 'card-bluish-reb'
                },
                # card-bluish-reb
                # card-slate-reb
                # card-silk-blue-reb
                # card-navy-reb
            ],

        }
