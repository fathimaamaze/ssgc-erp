# -*- coding: utf-8 -*-

import datetime
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    code = fields.Char('Code', default='New')
    sub_pro_seq_code = fields.Integer(default=1001)
    wsb_seq_code = fields.Integer(default=1001)
    company_id = fields.Many2one('res.company', string='Company')
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24, change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', 'State', ondelete='restrict', store=True)
    country_id = fields.Many2one('res.country', 'Country', ondelete='restrict')
    architect = fields.Many2one('res.partner', 'Architect')
    consultant = fields.Many2one('res.partner', 'Consultant')
    legal_adviser = fields.Many2one('res.partner', string='Legal Adviser')
    engineer_incharge = fields.Many2one('res.partner', string='Engineer Incharge')
    site_specifications = fields.Char(string='Site Specifications')
    site_contact_person = fields.Many2one('res.partner', string='Site Contact Person')
    site_contact_no = fields.Char('Site Contact No')
    vat = fields.Char('VAT No')
    cst = fields.Char('CST No')
    saleable_area = fields.Float('Saleable Area')
    builtup_area = fields.Float('Builtup Area')
    carpet_area = fields.Float('Carpet Area')
    tdr = fields.Char('TDR')
    plot_area = fields.Float('Plot Area')
    construction_cost_per_SFT = fields.Char('Construction Cost per SFT')
    total_construction_cost = fields.Float('Total Construction Cost', compute='get_total_construction_cost',
                                           readonly=True)
    fsi = fields.Char('FSI')
    lbt_location_id = fields.Char('LBT Location ID')
    project_category = fields.Many2one('project.category', string='Category')
    sanction_no = fields.Char('Sanction No')
    start_date = fields.Date('Start Date')
    finish_date = fields.Date('Finish Date')
    file_name = fields.Char('File Name')
    description = fields.Text('Remark/Description')
    attachment_line_ids = fields.One2many('ir.attachment', 'document_id', 'Attachment Lines')
    date_ids = fields.One2many('sanction.date', 'date_id', 'Sanction Dates')
    location_id = fields.Many2one('stock.location', 'Location')
    subproject_ids = fields.One2many('sub.project', 'project_id')

    stage_id = fields.Many2one('project.project.stage', 'Stage', default=_default_stage)
    flag = fields.Boolean('Flag', default=False, copy=False)
    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage',
                                domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)
    group_ids = fields.Many2many('res.groups', 'project_group_rel', 'group_id', 'project_id', 'Groups')
    active_duplicate = fields.Boolean(compute='get_active_duplicate')

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

    def get_total_construction_cost(self):
        """ Method to calculate the total_construction_cost of project. """
        for project in self:
            total_amount = 0.0
            account_move_rec = self.env['account.move'].search(
                [('project_id', '=', project.id), ('state', '=', 'posted')])
            for move in account_move_rec:
                total_amount += move.amount_total

            project.update({
                'total_construction_cost': total_amount
            })

    def get_active_duplicate(self):
        self.active_duplicate = True
        self.env['res.users'].browse(self._context.get('uid'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            name = vals.get('name')
            if self.env['stock.location']:
                stock_location_obj = self.env['stock.location']
                loc_id = (stock_location_obj.search([('name', '=', 'Virtual Locations')])).id
                data = {
                    'usage': 'production',
                    'location_id': loc_id,
                    'name': 'Consumed' + ' ' + str(name)
                }
                location_obj = self.env['stock.location'].create(data)

                vals.update({'location_id': location_obj.id})
            """" Creating Audit Trail """

            existing_stage = []
            st_ids = self.env['stage.master'].search([('draft', '=', True)])
            if st_ids:
                for st_id in st_ids:
                    msg_ids = {
                        'date': datetime.datetime.now(),
                        'from_stage': None,
                        'to_stage': st_id.id,
                        'model': 'project.project'
                    }

            if self._context.get('uid'):
                msg_ids.update(
                    {'remark': 'Created by ' + (self.env['res.users'].browse(self._context.get('uid'))).name, })

            existing_stage.append((0, 0, msg_ids))
            vals.update({'mesge_ids': existing_stage})

        return super(ProjectProject, self).create(vals_list)

    def change_state(self, context={}):
        if context.get('copy', False):
            self.flag = True

            if self.code in [False, 'New']:
                self.code = self.env['ir.sequence'].next_by_code('ssgc.project') or 'New'

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


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    _description = 'Ir Attachment'

    document_id = fields.Many2one('project.project', 'Document ID')


class SanctionDate(models.Model):
    _name = 'sanction.date'
    _description = 'Sanction Date'

    date_id = fields.Many2one('project.project', string='Order Reference', Invisible=True)
    sanction_date = fields.Date('Sanction Date')
    sanction_no = fields.Integer('Sanction No')


class ProjectCategories(models.Model):
    _name = 'project.category'
    _description = 'Project Categories'

    name = fields.Char('Name', required=True)
    description = fields.Text('Remark/Description')


class TransactionStatus(models.Model):
    _name = 'transaction.status'
    _description = 'Transaction Status'

    name = fields.Char('Name', required=True)


class StateMaster(models.Model):
    _name = 'stage.master'
    _description = 'State Master'

    name = fields.Char('Stage Name', required=True, translate=True)
    draft = fields.Boolean('Drafts')
    approved = fields.Boolean('Approved')
    foreclosed = fields.Boolean('Foreclosed')
    amend_and_draft = fields.Boolean('Amend And Draft')

    def stage_uniq(self):
        draft_list = []
        approve_list = []
        forclose_list = []
        amend_draft_list = []
        stage_obj_draft = self.env['stage.master'].search([('draft', '=', True)])
        for stage in stage_obj_draft:
            draft_list.append(stage.id)
            if len(set(draft_list)) > 1:
                return False

        stage_obj_approved = self.env['stage.master'].search([('approved', '=', True)])
        for stage in stage_obj_approved:
            approve_list.append(stage.id)
            if len(set(approve_list)) > 1:
                return False

        stage_obj_forclosed = self.env['stage.master'].search([('foreclosed', '=', True)])
        for stage in stage_obj_forclosed:
            forclose_list.append(stage.id)
            if len(set(forclose_list)) > 1:
                return False

        stage_obj_amend_draft = self.env['stage.master'].search([('amend_and_draft', '=', True)])
        for stage in stage_obj_amend_draft:
            amend_draft_list.append(stage.id)
            if len(set(amend_draft_list)) > 1:
                return False

        return True

    _constraints = [
        (stage_uniq, 'The draft, approved, foreclosed, amend_and_draft state must be unique!',
         ['draft', 'approved', 'foreclosed', 'amend_and_draft'])
    ]
