# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'
    _description = 'Stock Move'

    task_category = fields.Many2one('task.category', 'Task Category')
    material_line_id = fields.Many2one('task.material.line', 'Task Category')


class StockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Stock Location'

    project_id = fields.Many2one('project.project', 'Project')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    wbs_id = fields.Many2one('project.task', 'WBS')

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        if self.wbs_id:
            material_line_obj = self.env['task.material.line']
            for rec in self:
                for line in rec.move_ids:
                    if line.material_line_id:
                        material_line_obj.browse(line.material_line_id.id).delivered_qty = line.quantity

        return res
