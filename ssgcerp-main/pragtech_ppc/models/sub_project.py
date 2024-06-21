# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api


class SubProject(models.Model):
    _name = 'sub.project'
    _description = 'Sub Project'

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    name = fields.Char('Name', required=True)
    code = fields.Char(default='New')
    project_id = fields.Many2one('project.project', 'Project', required=True,
                                 domain=[('approval_state', '=', 'approve')])
    budget_applicable = fields.Boolean('Budget Applicable')
    wbs_id = fields.One2many('project.task', 'sub_project')

    seq_code = fields.Integer(default=1001)

    stage_id = fields.Many2one('stage.master', 'Stage', default=_default_stage)
    flag = fields.Boolean('Flag', default=False)  # For Change state button
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='Status', readonly=True, copy=False,
                             default='draft')
    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage',
                                domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')

    approval_state = fields.Selection([('approve', 'Approval')], string='State')

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        if name:
            domain += ['|', ('name', 'ilike', name), ('code', 'ilike', name)]
        return self._search(domain, limit=limit, order=order)

    @api.depends('code')
    def _compute_display_name(self):
        for rec in self:

            if rec.name:
                display_name = rec.name
                if rec.code and rec.code not in [False, 'New']:
                    display_name += ' / ' + rec.code
            elif rec.code and rec.code not in [False, 'New']:
                display_name = rec.code
            else:
                display_name = '/'

            rec.display_name = display_name

    @api.model_create_multi
    def create(self, vals_list):
        """" Creating Audit Trail """
        for vals in vals_list:
            existing_stage = []
            st_id = self.env['stage.master'].search([('draft', '=', True)])
            msg_ids = {
                'date': datetime.now(),
                'from_stage': None,
                'to_stage': st_id.id,
                'model': 'sub.project'
            }

            if self._context.get('uid'):
                msg_ids.update(
                    {'remark': 'Created by ' + (self.env['res.users'].browse(self._context.get('uid'))).name, })

            existing_stage.append((0, 0, msg_ids))
            vals.update({'mesge_ids': existing_stage})

        return super(SubProject, self).create(vals_list)

    def change_state(self, context={}):
        if context.get('copy', False):
            self.flag = True
            if self.project_id and self.code in [False, 'New']:
                self.code = 'SP' + str(self.project_id.sub_pro_seq_code) + '-' + self.project_id.code[1:]
                self.project_id.sub_pro_seq_code += 1
        else:
            self.approval_state = 'approve'
            self.flag = False
            view_id = self.env.ref('pragtech_ppc.approval_wizard_form_view').id
            return {
                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': 'approval.wizard',
                'multi': 'True',
                'target': 'new',
                'views': [[view_id, 'form']],
            }
