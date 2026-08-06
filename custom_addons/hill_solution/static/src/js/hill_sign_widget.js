/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class HillSignCanvas extends Component {
    static template = "hill_solution.HillSignCanvas";
    static props = {
        ...standardFieldProps,
        width: { type: Number, optional: true },
        height: { type: Number, optional: true },
    };
    static defaultProps = { width: 500, height: 180 };
    static supportedTypes = ["binary"];

    setup() {
        this.drawing = false;
        this.ctx = null;
        this.canvasRef = useRef("canvas");

        onMounted(() => {
            const canvas = this.canvasRef.el;
            this.ctx = canvas.getContext("2d");
            this._prepareCanvas();

            // Render existing value if the field already holds an image
            const initial = this.props.value;
            if (initial && initial.length > 40) {
                this._loadImage(initial);
            }
        });

        onWillUnmount(() => {
            if (this._image) {
                this._image.onload = null;
            }
        });
    }

    _prepareCanvas() {
        const ctx = this.ctx;
        ctx.lineWidth = 2.5;
        ctx.lineCap = "round";
        ctx.lineJoin = "round";
        ctx.strokeStyle = "#1f2937";
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, this.props.width, this.props.height);
    }

    get canvasEl() {
        return this.canvasRef.el;
    }

    _getPointerPosition(ev) {
        const canvas = this.canvasEl;
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const clientX = ev.clientX ?? ev.touches?.[0]?.clientX ?? 0;
        const clientY = ev.clientY ?? ev.touches?.[0]?.clientY ?? 0;
        return {
            x: (clientX - rect.left) * scaleX,
            y: (clientY - rect.top) * scaleY,
        };
    }

    onPointerDown(ev) {
        ev.preventDefault();
        this.drawing = true;
        const { x, y } = this._getPointerPosition(ev);
        this._prepareCanvas();
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
    }

    onPointerMove(ev) {
        if (!this.drawing) {
            return;
        }
        ev.preventDefault();
        const { x, y } = this._getPointerPosition(ev);
        this.ctx.lineTo(x, y);
        this.ctx.stroke();
    }

    onPointerUp(ev) {
        if (!this.drawing) {
            return;
        }
        this.drawing = false;
        this._saveToField();
    }

    _saveToField() {
        const dataUrl = this.canvasEl.toDataURL("image/png");
        const base64 = dataUrl.split(",")[1] || "";
        this.props.record.update({ [this.props.name]: base64 });
    }

    _loadImage(base64) {
        if (this._image) {
            this._image.onload = null;
        }
        this._image = new Image();
        this._image.onload = () => {
            this._prepareCanvas();
            this.ctx.drawImage(this._image, 0, 0);
        };
        this._image.src = "data:image/png;base64," + base64;
    }

    onClear() {
        this._prepareCanvas();
        this.props.record.update({ [this.props.name]: "" });
    }
}

registry.category("fields").add("hill_sign_canvas", {
    component: HillSignCanvas,
    supportedTypes: ["binary"],
    extractProps: ({ attrs }) => ({
        width: attrs.width,
        height: attrs.height,
    }),
});
