# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectTaskLibrary(models.Model):
    _name = 'project.task.library'
    _description = 'Project BOQ'

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    name = fields.Char('Task Title', required=True)

    code = fields.Char()
    task_id = fields.Many2one('project.task', string='WBS')
    user_id = fields.Many2one('res.users', 'Assigned to')
    is_library_task = fields.Boolean('Library Task')
    category_id = fields.Many2one('task.category', 'Category')
    sub_category_id = fields.Many2one('task.sub.category', 'Sub Category')
    material_cost = fields.Float(compute='_calculate_material_cost', default='0.0', string='Material Cost', method=True)
    min_qty = fields.Integer('Minimum Qty', required=True)
    labour_cost = fields.Float(compute="calculate_labour_cost", string="Labour Cost", method=True)
    date_start = fields.Date('Start Date')
    date_end = fields.Date('End Date')
    parent_task_id = fields.Many2one('project.task.library', 'Parent Group')
    parent_group_id = fields.Many2one('project.task.library', 'Parent Group')
    parent_id = fields.Many2one('project.task.library', string="Parent", help="Hierarchy Purpose.")
    task_ids = fields.One2many('project.task.library', 'parent_task_id', 'Tasks')
    group_ids = fields.One2many('project.task.library', 'parent_group_id', 'Group')
    child_ids2 = fields.One2many('project.task.library', 'parent_id', compute='compute_child', store=True)
    task_material_line = fields.One2many('material.library', 'task_library_id', string='Task Material Lines')
    task_labour_line = fields.One2many('labour.library', 'task_library_id', string='Task labour Lines')
    uom_id = fields.Many2one('uom.uom', 'Unit')
    total_cost = fields.Float(compute='_get_total_cost', string='Total Cost',
                              help='Sum of material cost and labour cost', method=True)

    stage_id = fields.Many2one('project.project.stage', 'Stage', default=_default_stage)
    flag = fields.Boolean('Flag', default=False, copy=False)
    approval_state = fields.Selection([('approve', 'Approval')], string='State')

    def change_state(self, context={}):
        if context.get('copy', False):
            self.flag = True

            if self.task_id and self.code in [False, 'New']:
                task_id = self.task_id
                if task_id.project_id and self.code in [False, 'New']:
                    task_id.code = 'PS' + str(task_id.project_id.wsb_seq_code) + '-' + task_id.project_id.code[1:]
                    task_id.project_id.wsb_seq_code += 1
                self.code = 'B' + str(self.task_id.boq_seq_code) + '-' + self.task_id.code[2:]
                self.task_id.boq_seq_code += 1
        else:
            view_id = self.env.ref('pragtech_purchase.approval_wizard_form_view_purchase').id
            return {
                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': 'approval.wizard',
                'multi': 'True',
                'target': 'new',
                'views': [[view_id, 'form']],
            }

    def _get_total_cost(self):
        for this in self:
            this.total_cost = sum([line.subtotal for line in this.task_material_line]) + sum(
                [line.subtotal for line in this.task_labour_line])

    @api.onchange('category_id')
    def onchange_category_id(self):
        return {
            'domain': {
                'sub_category_id': [('category_id', '=', self.category_id.id)]
            }
        }

    def _calculate_material_cost(self):
        for line in self:
            total_material_cost = 0.0
            if line.task_material_line:
                for lines in line.task_material_line:
                    total_material_cost += lines.material_uom_qty * lines.material_rate

                line.material_cost = total_material_cost
            else:
                self.material_cost = total_material_cost

    def calculate_labour_cost(self):
        for line in self:
            total_labour_cost = 0.0
            if line.task_labour_line:
                for lines in line.task_labour_line:
                    total_labour_cost += lines.labour_uom_qty * lines.labour_rate

                line.labour_cost = total_labour_cost
            else:
                self.labour_cost = total_labour_cost

    @api.depends('task_ids', 'group_ids')
    def compute_child(self):
        for task in self:
            child_ids = []
            for child_task in task.task_ids:
                child_ids.append((4, child_task.id))

            for child_task in task.group_ids:
                child_ids.append((4, child_task.id))

            if child_ids:
                task.child_ids2 = child_ids
