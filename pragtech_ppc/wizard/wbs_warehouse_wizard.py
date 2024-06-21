# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class WBSWarehouseWizard(models.TransientModel):
    _name = 'wbs.warehouse.wizard'
    _description = 'WBS Warehouse'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', required=True)

    def create_deliveries(self):

        picking_obj = self.env['stock.picking']
        picking_type_obj = self.env['stock.picking.type']
        for rec in self.env['project.task'].browse(self._context.get('active_id')):
            move_ids_without_package = []
            picking_type_id = picking_type_obj.search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', self.warehouse_id.id)], limit=1)
            if picking_type_id:
                for line in rec.material_estimate_line:
                    move_ids_without_package.append((0, 0, {
                        'material_line_id': line.id,
                        'name': line.material_id.name,
                        'product_id': line.material_id.id,
                        'product_uom_qty': line.material_uom_qty,
                        'location_dest_id': picking_type_id.default_location_dest_id.id or self.env[
                            'stock.location'].search([('usage', '=', 'customer')], limit=1).id,
                        'location_id': picking_type_id.default_location_src_id.id or self.warehouse_id.lot_stock_id.id
                    }))

                if move_ids_without_package:
                    picking_obj.create({
                        'picking_type_id': picking_type_id.id,
                        'move_ids': move_ids_without_package,
                        'wbs_id': rec.id,
                    })
