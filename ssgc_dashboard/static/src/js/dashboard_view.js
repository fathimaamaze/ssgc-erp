/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";

export class DashBoard extends Component {
    static template = "contracting_dashboard_template"

    setup() {
        this.dashboard_data = {};

        this.state = useState({
            material_requisition: [],
            labour_requisition: [],
            purchase_orders: [],
            delivery_orders: [],
        })

        this.orm = useService("orm");
        this.action = useService("action");

        onWillStart(async() => {
            this.state.material_requisition = await this.orm.call('purchase.requisition','get_approval_recs', []);
            this.state.labour_requisition = await this.orm.call('labour.requisition','get_approval_recs', [])
            this.state.purchase_orders = await this.orm.call('purchase.order','get_approval_recs', [])
            this.state.delivery_orders = await this.orm.call('stock.picking','get_approval_recs', [])
        })

        onMounted(async () => {
            await this.update_project();
        });
    }

    async update_project() {
        var self = this;
        const res = await this.orm.call(
            "res.users",
            "get_contracting_dashboard_data",
            [session.user_id]
        );
        self.update_dashboard_data(res);
    }

    update_dashboard_data(data) {
        $("#welcome_msg").html(data.welcome_msg);

        var project_names = [];
        var project_selection = "<div class='check-box'>";

        var cards = "";
        data.cards.forEach(function (card) {
            cards += "<div class='col mb-4 stretch-card transparent' data-id='" + card.id + "'>";
            cards += "<div class='card card-reb " + card.class + "'>";
            cards += "<div class='card-body card-body-reb'>";
            cards += "<p class='mb-5'>" + card.name + "</p>";
            cards += "<p class='mb-2'>" + card.value + "</p>";
            cards += "</div></div></div>";
        });
        $("#cards").html(cards);

    }

    btn_click_open_rec(ev) {
        let data = ev.target.parentElement.dataset;
        this.action.doAction({
            type: 'ir.actions.act_window',
            name: _t(data.model_name),
            res_model: data.model,
            views: [[false, 'form']],
            res_id: parseInt(data.id)
        });
    }
}

registry.category("actions").add("contracting_dashboard", DashBoard);
