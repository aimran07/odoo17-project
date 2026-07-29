/** @odoo-module **/

import {
    Component,
    useRef,
    onMounted,
    onWillUnmount,
    onWillUpdateProps,
} from "@odoo/owl";

export class DashboardChart extends Component {

    static template = "hill_dashboard.DashboardChart";

    static props = {
        config: Object,
    };

    setup() {

        this.canvasRef = useRef("canvas");
        this.chart = null;

        onMounted(() => {
            this.renderChart(this.props.config);
        });

        onWillUpdateProps((nextProps) => {
            this.renderChart(nextProps.config);
        });

        onWillUnmount(() => {
            this.destroyChart();
        });
    }

    destroyChart() {

        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    renderChart(config) {

        if (!config) {
            return;
        }

        if (!this.canvasRef.el) {
            return;
        }

        this.destroyChart();

        this.chart = new window.Chart(
            this.canvasRef.el,
            config
        );
    }

}
