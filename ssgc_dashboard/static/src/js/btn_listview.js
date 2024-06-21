/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';
import { useService } from "@web/core/utils/hooks";
import { Component, EventBus, onWillStart, useSubEnv, useState } from "@odoo/owl";

export class MRListController extends ListController {

    setup() {
        super.setup();
        this.action = useService("action");
    }

    async onCreateRecord() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            name:  'Create Material Requisition',
            res_model: 'purchase.requisition.wizard',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'new',
        });
    }

}

export class MCListController extends ListController {

    setup() {
        super.setup();
        this.action = useService("action");
    }

    onCreateRecord() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'purchase.consumption.wizard',
            name:'Create Material Consumption',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'new',
        });
    }

}

export class LRListController extends ListController {

    setup() {
        super.setup();
        this.action = useService("action");
    }

    onCreateRecord() {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'labour.requisition.wizard',
            name:'Create Labour Requisition',
            views: [[false, 'form']],
            view_mode: 'form',
            target: 'new',
        });
    }

}

registry.category("views").add("material_requisition", {
    ...listView,
    Controller: MRListController,
    buttonTemplate: "material_requisition.ListView.Buttons",
});

registry.category("views").add("material_consumption", {
    ...listView,
    Controller: MCListController,
    buttonTemplate: "material_consumption.ListView.Buttons",
});

registry.category("views").add("labour_requisition", {
    ...listView,
    Controller: LRListController,
    buttonTemplate: "labour_requisition.ListView.Buttons",
});
