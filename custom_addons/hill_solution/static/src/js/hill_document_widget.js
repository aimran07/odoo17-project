/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onWillStart, onWillUpdateProps, useRef } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

export class HillDocumentWidget extends Component {
    static template = "hill_solution.HillDocumentWidget";

    setup() {
        this.fileInputRef = useRef("docFileInput");
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.state = useState({
            documents: [],
            previewDoc: null,
            showModal: false,
            loading: false,
            uploading: false,
        });

        onWillStart(async () => {
            await this.loadDocuments();
        });

        onWillUpdateProps(async (nextProps) => {
            const newIds = nextProps.value?.currentIds || [];
            const oldIds = this.props.value?.currentIds || [];
            const changed =
                newIds.length !== oldIds.length ||
                newIds.some((id) => !oldIds.includes(id));
            if (changed) {
                await this.loadDocuments(newIds);
            }
        });
    }

    async loadDocuments(ids = null) {
        let docIds = ids;

        if (docIds === null) {
            docIds = this.props.value?.currentIds || [];
        }

        if (!docIds.length && this.props.record?.resId) {
            try {
                const result = await this.orm.read(
                    this.props.record.resModel,
                    [this.props.record.resId],
                    [this.props.name]
                );
                docIds = result[0]?.[this.props.name] || [];
            } catch (e) {
                console.error("Failed to fetch document ids", e);
            }
        }

        if (!docIds.length) {
            this.state.documents = [];
            return;
        }

        this.state.loading = true;
        try {
            const records = await this.orm.read(
                "hill.site.document",
                docIds,
                ["id", "attachment_id", "name", "mimetype", "file_size", "uploaded_at"]
            );
            this.state.documents = records.map((r) => ({
                id: r.id,
                attachmentId: r.attachment_id[0],
                name: r.name,
                mimetype: r.mimetype,
                file_size: r.file_size,
                uploadedAt: r.uploaded_at,
                previewUrl: `/web/content/${r.attachment_id[0]}?download=false`,
                icon: this._getIcon(r.mimetype),
                typeLabel: this._getTypeLabel(r.mimetype),
                sizeLabel: this._formatSize(r.file_size),
            }));
        } catch (e) {
            console.error("HillDocumentWidget: failed to load", e);
        } finally {
            this.state.loading = false;
        }
    }

    _getIcon(mimetype) {
        if (!mimetype) return "fa-file-o";
        if (mimetype === "application/pdf") return "fa-file-pdf-o";
        if (mimetype.includes("word")) return "fa-file-word-o";
        if (mimetype.includes("excel") || mimetype.includes("spreadsheet"))
            return "fa-file-excel-o";
        return "fa-file-o";
    }

    _getTypeLabel(mimetype) {
        if (!mimetype) return "FILE";
        if (mimetype === "application/pdf") return "PDF";
        if (mimetype.includes("word")) return "WORD";
        if (mimetype.includes("excel")) return "EXCEL";
        return "FILE";
    }

    _formatSize(bytes) {
        if (!bytes) return "\u2014";
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    openPreview(doc) {
        this.state.previewDoc = doc;
        this.state.showModal = true;
    }

    closePreview() {
        this.state.showModal = false;
        this.state.previewDoc = null;
    }

    downloadDoc(ev, doc) {
        ev.stopPropagation();
        window.open(`/web/content/${doc.attachmentId}?download=true`, "_blank");
    }

    async removeDoc(ev, doc) {
        ev.stopPropagation();
        if (this.props.readonly || !this.props.record) return;

        await this.props.record.update({
            [this.props.name]: [[2, doc.id]],
        });
        await this.props.record.save();

        const currentIds = this.state.documents
            .map((d) => d.id)
            .filter((id) => id !== doc.id);
        await this.loadDocuments(currentIds);
    }

    // async onFileUpload(ev) {
    //     if (this.props.readonly) return;

    //     const files = ev.target.files;
    //     if (!files.length) return;

    //     const recordId = this.props.record?.resId;
    //     const model = this.props.record?.resModel;

    //     if (!recordId) {
    //         this.notification.add(
    //             "Save the record first before uploading documents.",
    //             { type: "info" }
    //         );
    //         return;
    //     }

    //     const allowed = [
    //         "application/pdf",
    //         "application/msword",
    //         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    //         "application/vnd.ms-excel",
    //         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    //     ];
    //     const invalid = Array.from(files).filter((f) => !allowed.includes(f.type));
    //     if (invalid.length) {
    //         this.notification.add(
    //             "Only PDF, Word, and Excel files are allowed.",
    //             { type: "danger" }
    //         );
    //         return;
    //     }

    //     this.state.uploading = true;

    //     try {
    //         const linkCommands = [];

    //         for (const file of files) {
    //             const data = await this._readFileAsBase64(file);
    //             const result = await this.orm.create("ir.attachment", [{
    //                 name: file.name,
    //                 datas: data,
    //                 mimetype: file.type,
    //                 res_model: model,
    //                 res_id: recordId,
    //             }]);

    //             const attachmentId = result[0];
    //             await this.orm.create("hill.site.document", [{
    //                 site_report_id: recordId,
    //                 attachment_id: attachmentId,
    //             }]);
    //         }

    //         await this.props.record.update({
    //             [this.props.name]: linkCommands,
    //         });
    //         await this.props.record.save();

    //         const result = await this.orm.read(
    //             model,
    //             [this.props.record.resId],
    //             [this.props.name]
    //         );
    //         const savedIds = result[0]?.[this.props.name] || [];
    //         await this.loadDocuments(savedIds);

    //         this.notification.add(
    //             `${linkCommands.length} document(s) uploaded successfully`,
    //             { type: "success" }
    //         );
    //     } catch (e) {
    //         this.notification.add("Upload failed. Please try again.", { type: "danger" });
    //         console.error(e);
    //     } finally {
    //         this.state.uploading = false;
    //         ev.target.value = "";
    //     }
    // }
    async onFileUpload(ev) {
        if (this.props.readonly) return;

        const files = ev.target.files;
        if (!files.length) return;

        const recordId = this.props.record?.resId;
        const model = this.props.record?.resModel;

        if (!recordId) {
            this.notification.add(
                _t("Save the record first before uploading documents."),
                { type: "info" }
            );
            return;
        }

        const allowed = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ];
        const invalid = Array.from(files).filter((f) => !allowed.includes(f.type));
        if (invalid.length) {
            this.notification.add(
                _t("Only PDF, Word, and Excel files are allowed."),
                { type: "danger" }
            );
            return;
        }

        this.state.uploading = true;
        let successCount = 0;

        for (const file of files) {
            try {
                const data = await this._readFileAsBase64(file);
                const result = await this.orm.create("ir.attachment", [{
                    name: file.name,
                    datas: data,
                    mimetype: file.type,
                    res_model: model,
                    res_id: recordId,
                }]);

                const attachmentId = result[0];
                await this.orm.create("hill.site.document", [{
                    site_report_id: recordId,
                    attachment_id: attachmentId,
                }]);

                successCount++;
            } catch (e) {
                this.notification.add(
                    sprintf(_t("Upload failed: %s"), file.name),
                    { type: "danger" }
                );
                console.error(e);
            }
        }

        await this.props.record.load();
        await this.loadDocuments();
        this.state.uploading = false;
        ev.target.value = "";

        if (successCount > 0) {
            this.notification.add(
                sprintf(_t("%s document(s) uploaded successfully"), successCount),
                { type: "success" }
            );
        }
    }

    _readFileAsBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(",")[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    triggerUpload() {
        if (this.props.readonly) return;
        this.fileInputRef.el.click();
    }
}

registry.category("fields").add("hill_document_widget", {
    component: HillDocumentWidget,
    supportedTypes: ["many2many", "one2many"],
    extractProps({ attrs, field }, dynamicInfo) {
        return {
            name: field.name,
            id: attrs.id,
            value: dynamicInfo.value,
            record: dynamicInfo.record,
            readonly: dynamicInfo.readonly,
            required: dynamicInfo.required,
            context: field.context || {},
        };
    },
});
