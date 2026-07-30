/** @odoo-module **/

import { Component, useEffect, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { useDateTimePicker } from "@web/core/datetime/datetime_hook";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { formatDateTime, formatDate } from "@web/core/l10n/dates";

const { DateTime } = luxon;

export class VisitDateWidget extends Component {
    static template = "hill_solution.VisitDateWidget";
    static props = {
        ...standardFieldProps,
        maxDate: { type: String, optional: true },
        minDate: { type: String, optional: true },
        placeholder: { type: String, optional: true },
        required: { type: Boolean, optional: true },
        rounding: { type: Number, optional: true },
        showTime: { type: Boolean, optional: true },
    };
    static defaultProps = { showTime: true };
    static supportedTypes = ["datetime", "date"];

    setup() {
        this.rpc = useService("rpc");

        this.bookedState = useState({ bookedDates: new Set() });

        const getTechId = () => this.props.record.data.technician_name?.[0];

        // Reload booked dates whenever the technician changes (and on mount)
        useEffect(() => {
            this._loadBookedDates(getTechId());
        }, () => [getTechId()]);

        const getPickerProps = () => this._getPickerProps();

        const dateTimePicker = useDateTimePicker({
            target: "root",
            get pickerProps() {
                return getPickerProps();
            },
            onChange: () => {},
            onApply: () => {
                const value = this.state.value;
                if (value !== undefined && value !== null) {
                    this.props.record.update({ [this.props.name]: value });
                }
            },
        });
        this.state = useState(dateTimePicker.state);
        this.openPicker = dateTimePicker.open;
    }

    _getPickerProps() {
        const field = this.props.record.fields[this.props.name];
        const value = this.props.record.data[this.props.name];
        const pickerProps = {
            value,
            type: field.type,
            isDateValid: this._isDateValid.bind(this),
            dayCellClass: this._dayCellClass.bind(this),
        };
        if (this.props.maxDate) {
            pickerProps.maxDate = this._parseLimitDate(this.props.maxDate);
        }
        if (this.props.minDate) {
            pickerProps.minDate = this._parseLimitDate(this.props.minDate);
        }
        if (!isNaN(this.props.rounding)) {
            pickerProps.rounding = this.props.rounding;
        }
        return pickerProps;
    }

    async _loadBookedDates(technicianId) {
        if (!technicianId) {
            this.bookedState.bookedDates = new Set();
            return;
        }
        try {
            const dates = await this.rpc("/hill_solution/technician_booked_dates", {
                technician_id: technicianId,
            });
            this.bookedState.bookedDates = new Set(dates);
        } catch (e) {
            console.error("Failed to load booked dates", e);
            this.bookedState.bookedDates = new Set();
        }
    }

    _isDateValid(date) {
        return !this.bookedState.bookedDates.has(date.toISODate());
    }

    _dayCellClass(date) {
        return this.bookedState.bookedDates.has(date.toISODate())
            ? "o_visit_date_booked"
            : "";
    }

    get formattedValue() {
        const value = this.props.record.data[this.props.name];
        if (!value) {
            return "";
        }
        const isDateOnly =
            this.props.record.fields[this.props.name].type === "date" ||
            !this.props.showTime;
        const dt = value instanceof DateTime ? value : DateTime.fromISO(value);
        return isDateOnly ? formatDate(dt) : formatDateTime(dt);
    }

    _parseLimitDate(limit) {
        if (limit === "today") {
            return DateTime.now().startOf("day");
        }
        return DateTime.fromISO(limit);
    }

    onInput() {
        this.triggerIsDirty(true);
    }
}

registry.category("fields").add("visit_date_widget", {
    component: VisitDateWidget,
    supportedTypes: ["datetime", "date"],
    extractProps: ({ attrs }) => ({
        maxDate: attrs.maxDate,
        minDate: attrs.minDate,
        placeholder: attrs.placeholder,
        required: attrs.required,
        rounding: attrs.rounding,
        showTime: "showTime" in attrs ? attrs.showTime : true,
    }),
});
