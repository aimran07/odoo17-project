/** @odoo-module **/

import { onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";

patch(FormRenderer.prototype, {

    setup() {
        super.setup();
        onMounted(() => {
            document
                .querySelectorAll(".accordion-header")
                .forEach((header) => {
                    header.addEventListener(
                        "click",
                        function () {
                            const content =
                                this.nextElementSibling;
                            content.classList.toggle(
                                "collapsed"
                            );
                            this.classList.toggle(
                                "opened"
                            );
                        }
                    );
                });
        });
    },
});
