# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.exceptions import UserError


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _description = 'Purchase Requisition'

    @api.model
    def _default_stage(self):
        st_ids = self.env['stage.master'].search([('draft', '=', True)])
        if st_ids:
            for st_id in st_ids:
                return st_id.id

    # is_use = fields.Boolean('Use')
    # material_id = fields.Many2one('product.product', 'Material')
    # quantity = fields.Integer(' Quantity')
    # model = fields.Char('Related Document Model', index=1)
    # total_ordered_qty = fields.Float('Ordered Qty', readonly=True)
    # balance_qty = fields.Float('Balance Qty', compute='get_balanced_qty')
    # Requisition_as_on_date = fields.Float('Requisition as on date')
    # current_req_qty = fields.Float('Current requisition Qty')
    # unit = fields.Many2one('uom.uom', 'Unit', required=True)
    # rate = fields.Float('Rate')
    # material_category = fields.Many2one('product.category', string='Material Category',
    # related='material_id.categ_id', store=True)

    name = fields.Char('Requisition No.')
    group_id = fields.Many2one('project.task', 'Task Group')
    task_id = fields.Many2one('project.task', 'Task')
    flag = fields.Boolean('Flag', default=False)

    requisition_date = fields.Date('Date', default=fields.date.today(), required=True)
    requirement_date = fields.Date('Requirement Date')
    procurement_date = fields.Date('Procurement Date')

    specification = fields.Char('Specification')
    remark = fields.Char('Remark')

    mesge_ids = fields.One2many('mail.messages', 'res_id', string='Massage',
                                domain=lambda self: [('model', '=', self._name)], auto_join=True, readonly=True)
    # previous quantity fields
    total_approved_qty = fields.Float('Approved Qty', readonly=True)
    requisition_qty = fields.Float('Requisition Qty')
    estimated_qty = fields.Float('Estimated Qty')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status')
    priority = fields.Selection([('high', 'High'), ('low', 'Low')], 'Priority')
    brand_id = fields.Many2one('brand.brand', 'Brand')
    requisition_type = fields.Selection([('estimated', 'Estimated'), ('non_estimated', 'Non Estimated')], 'Type')
    procurement_type = fields.Selection([('New Purchase from Supplier', 'New Purchase from Supplier'),
                                         ('Cash Purchase ', 'Cash Purchase '),
                                         ('IST from other sites', 'IST from other sites')], "Procurement Type")
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse")
    purchase_ids = fields.Many2many('purchase.order', 'po_requisition_rel1', 'requisition_id', 'purchase_id',
                                    string='Purchase Orders')
    requisition_fulfill = fields.Boolean('Req fulfill', compute='is_requisition_fulfill')
    stage_id = fields.Many2one('stage.master', 'Stage', default=_default_stage, readonly=True, copy=False,
                               track_visibility='onchange')
    project_wbs = fields.Many2one('project.task', 'project WBS',
                                  domain=[('is_wbs', '=', True), ('is_task', '=', False)])
    project_id = fields.Many2one('project.project', 'Project')

    sub_project = fields.Many2one('sub.project', 'Sub Project')
    estimation_id = fields.Many2one('task.material.line', 'Estimate No.')

    related_task_category = fields.Many2one('task.category', related='task_id.category_id', store=True)
    task_category = fields.Many2many('task.category', 'purchase_req_task_cat_rel', 'purchase_req_id',
                                     'task_category_id', string='Task Category')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('confirm', 'Confirm'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    me_sequence = fields.Char(readonly=True)
    counter = fields.Integer('counter')

    pr_line_ids = fields.One2many("purchase.requisition.line", 'pr_id')
    picking_ids = fields.One2many("stock.picking", 'mrf_id')

    count_picking_ids = fields.Integer(compute="compute_count_picking_ids")

    def compute_count_picking_ids(self):
        for rec in self:
            if rec.picking_ids:
                rec.count_picking_ids = len(rec.picking_ids)
            else:
                rec.count_picking_ids = 0

    def open_deliveries(self):
        if self.picking_ids:
            if len(self.picking_ids) > 1:
                return {
                    'name': _('Deliveries'),
                    'view_mode': 'tree,form',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'domain': [('id', 'in', self.picking_ids.ids)]
                }
            else:
                return {
                    'name': _('Delivery'),
                    'view_mode': 'form',
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'res_id': self.picking_ids.id
                }

    @api.depends('current_req_qty', 'total_ordered_qty')
    def get_balanced_qty(self):
        self.balance_qty = self.current_req_qty - self.total_ordered_qty

    @api.depends('current_req_qty')
    @api.onchange('current_req_qty')
    def validate_req_qty(self):
        self.balance_qty = self.quantity - (self.total_ordered_qty + self.current_req_qty)
        if self.balance_qty < 0.0:
            raise UserError(_('Invalid Current requisition Qty.'))

    def unlink(self):
        ids = []
        for line in self:
            ids.append(line.id)
        Purchase_order_obj = self.env['po.requisition'].search([('requisition_id', 'in', ids)])
        if Purchase_order_obj:
            raise UserError(_('You cannot delete Requisition which is used in Purchase Order.'))

    @api.model
    def is_requisition_fulfill(self):
        total_qty = 0
        po_line_obj = self.env['purchase.order.line'].search([('requisition_id', '=', self.id)])
        for line in po_line_obj:
            total_qty = +line.product_qty

        if total_qty > self.quantity:
            self.update({'requsition_fulfill': True})
            return True

    def change_state_1(self, context=None):
        if context is None:
            context = {}
        view_id = self.env.ref('pragtech_purchase.approval_wizard_form_view_purchase').id
        return {
            'type': 'ir.actions.act_window',
            'key2': 'client_action_multi',
            'res_model': "approval.wizard",
            'multi': "True",
            'target': 'new',
            'views': [[view_id, 'form']],
        }

    def change_state(self, context=None):
        if context is None:
            context = {}
        if self.counter == 0:
            self.counter = self.counter + 1
            if context.get('copy', False):
                self.write({'state': 'confirm'})

            """Updating Requisition till date in estimation table"""

            requisition_till_date = self.estimation_id.requisition_till_date
            if requisition_till_date <= self.estimation_id.material_uom_qty:
                self.estimation_id.requisition_till_date = self.estimation_id.requisition_till_date
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition') or '/'
                self.flag = 1
            else:
                self.flag = 0
                raise UserError(_('Sorry you cannot approve requisition greater then available quantity!'))

            view_id = self.env.ref('pragtech_purchase.approval_wizard_form_view_purchase').id
            return {
                'type': 'ir.actions.act_window',
                'key2': 'client_action_multi',
                'res_model': "approval.wizard",
                'multi': "True",
                'target': 'new',
                'views': [[view_id, 'form']],
            }

    def create_purchase_orders(self):
        purchase_ids = []
        for rec in self.filtered(lambda x: x.state == 'confirm'):
            if rec.pr_line_ids:
                seller_ids = rec.pr_line_ids.mapped('material_id.seller_ids.partner_id')
                if seller_ids:
                    for seller in seller_ids:
                        lines = rec.pr_line_ids.filtered(
                            lambda x: seller in x.mapped('material_id.seller_ids.partner_id'))
                        lst = []
                        for line in lines.filtered(lambda x: x.available_req_qty):
                            seller_id = line.material_id.seller_ids.filtered(lambda x: x.partner_id == seller)

                            lst.append((0, 0, {
                                'product_id': line.material_id.id,
                                'product_qty': line.available_req_qty,
                                'product_uom': line.unit.id,
                                'price_unit': seller_id and seller_id[0].price or 0,
                            }))

                        if lst:
                            purchase_ids.append(self.env['vendor.quotation'].create({
                                'partner_id': seller.id,
                                'requisition_id': rec.id,
                                'order_line': lst,
                                # 'project_id': rec.project_id.id,
                                # 'sub_project': rec.sub_project.id,
                                # 'project_wbs': rec.project_wbs.id,
                            }).id)

        if purchase_ids:
            return {
                'name': _('Draft RFQ'),
                'type': 'ir.actions.act_window',
                'res_model': 'purchase.order',
                'view_mode': 'tree,form',
                'domain': [('id', '=', purchase_ids)]
            }

    def create_deliveries_from_mrf(self):
        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']
        warehouse_ids = self.pr_line_ids.mapped('warehouse_id')
        move_ids = []
        picking_type_id = picking_type_obj.search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', self.warehouse_id.id)], limit=1)
        if picking_type_id:
            for warehouse_id in warehouse_ids:
                for line in self.pr_line_ids.filtered(lambda x: x.current_req_qty and x.warehouse_id.id == warehouse_id.id):
                    move_ids.append((0, 0, {
                        'mrf_line_id': line.id,
                        'name': line.material_id.name,
                        'product_id': line.material_id.id,
                        'product_uom_qty': line.current_req_qty,
                        'location_dest_id': picking_type_id.default_location_dest_id.id or self.env[
                            'stock.location'].search([('usage', '=', 'customer')], limit=1).id,
                        'location_id': picking_type_id.default_location_src_id.id or self.warehouse_id.lot_stock_id.id
                    }))

                if move_ids:
                    picking_obj.create({
                        'picking_type_id': picking_type_id.id,
                        'move_ids': move_ids,
                        'mrf_id': self.id,
                    })


class PurchaseRequisitionLine(models.Model):
    _name = "purchase.requisition.line"
    _description = "Purchase Requisition Line"

    def _default_warehouse_id(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1)
        return warehouse

    pr_id = fields.Many2one("purchase.requisition")
    warehouse_id = fields.Many2one("stock.warehouse", default=_default_warehouse_id)
    material_id = fields.Many2one("product.product")
    unit = fields.Many2one("uom.uom")
    rate = fields.Float()
    quantity = fields.Float()
    total_ordered_qty = fields.Float()
    balance_qty = fields.Float()
    Requisition_as_on_date = fields.Float()
    req_qty = fields.Float()
    current_req_qty = fields.Float()
    available_req_qty = fields.Float(compute="_compute_available_req_qty", store=True)
    state = fields.Selection(related="pr_id.state")
    available_warehouse_qty = fields.Float(compute="_compute_warehouse_qty")
    check_vendors = fields.Boolean(compute="compute_check_vendors")

    def compute_check_vendors(self):
        for rec in self:
            rec.check_vendors = True if rec.material_id.seller_ids else False

    @api.depends('current_req_qty')
    def _compute_available_req_qty(self):
        for rec in self:
            rec.available_req_qty = rec.req_qty - rec.current_req_qty

    def _compute_warehouse_qty(self):
        for rec in self:
            available_warehouse_qty = 0
            product_qty = rec.material_id.with_context(to_date=fields.Date.today(),
                                                       warehouse=rec.warehouse_id.id).read(['qty_available'])
            if product_qty:
                available_warehouse_qty = product_qty[0]['qty_available']
            rec.available_warehouse_qty = available_warehouse_qty
