/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { useRef, useEffect } from "@odoo/owl";
import { ListRenderer } from "@web/views/list/list_renderer";
import { useExternalListener } from "@odoo/owl";

patch(ListRenderer.prototype, {

    freezeColumnWidths() {
        if (!this.keepColumnWidths) {
            this.columnWidths = null;
        }

        debugger
        const model = this.env.model.config;
        const resModel = JSON.parse(JSON.stringify( model)).resModel

        const table = this.tableRef.el;
        const headers = [...table.querySelectorAll("thead th:not(.o_list_actions_header)")];

        if (!this.columnWidths || !this.columnWidths.length) {
            // no column widths to restore

            table.style.tableLayout = "fixed";
            const allowedWidth = table.parentNode.getBoundingClientRect().width;
            // Set table layout auto and remove inline style to make sure that css
            // rules apply (e.g. fixed width of record selector)
            table.style.tableLayout = "auto";
            headers.forEach((th) => {
                th.style.width = null;
                th.style.maxWidth = null;
            });

            this.setDefaultColumnWidths();

            if (resModel !== 'purchase.requisition.wizard') {
                // Squeeze the table by applying a max-width on largest columns to
                // ensure that it doesn't overflow
                this.columnWidths = this.computeColumnWidthsFromContent(allowedWidth);
                table.style.tableLayout = "fixed";
            }
        }

        if (resModel !== 'purchase.requisition.wizard') {
            headers.forEach((th, index) => {
                if (!th.style.width) {
                    th.style.width = `${Math.floor(this.columnWidths[index])}px`;
                }
            });
        }

    }

});