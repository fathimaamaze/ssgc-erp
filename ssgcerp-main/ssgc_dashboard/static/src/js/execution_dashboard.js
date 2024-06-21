/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { session } from "@web/session";
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";

export class DashBoard extends Component {
    static template = "execution_dashboard_template"

    setup() {
        this.dashboard_data = {};

        this.orm = useService("orm");
        this.action = useService("action");

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

registry.category("actions").add("execution_dashboard", DashBoard);
