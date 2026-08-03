/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, useRef, onWillStart, onWillUpdateProps, onMounted, onWillUnmount } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

export class HillPhotoWidget extends Component {
    static template = "hill_solution.HillPhotoWidget";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.fileInputRef = useRef("photoFileInput");
                this.clickOutsideRef = useRef("clickOutside");

        this.state = useState({
            photos: [],
            loading: false,
            uploading: false,
            progress: 0,
            queue: [],
            lightbox: false,
            selectedPhoto: null,
            dragOver: false,
            showUploadOptions: false,
            showWebcam: false,
            webcamStream: null,
            pendingCapture: null,
            geolocation: null,
        });

        onMounted(() => {
            document.addEventListener('click', this._onDocumentClick.bind(this));
        });

        onWillUnmount(() => {
            document.removeEventListener('click', this._onDocumentClick.bind(this));
        });

        onWillStart(async () => {
            await this.loadPhotos();
        });

        onWillUpdateProps(async (nextProps) => {
            const newIds = nextProps.value?.currentIds || [];
            const oldIds = this.props.value?.currentIds || [];
            const changed =
                newIds.length !== oldIds.length ||
                newIds.some((id) => !oldIds.includes(id));
            if (changed) {
                await this.loadPhotos(newIds);
            }
        });
    }

    _setVideoStream() {
        const video = document.querySelector(".mv_webcam_video");
        if (video && this.state.webcamStream) {
            if (!video.srcObject) {
                video.srcObject = this.state.webcamStream;
            }
            video.play().catch(() => {});
        }
    }

    async loadPhotos(ids = null) {
        let photoIds = ids;

        if (photoIds === null) {
            photoIds = this.props.value?.currentIds || [];
        }

        if (!photoIds.length && this.props.record?.resId) {
            try {
                const result = await this.orm.read(
                    this.props.record.resModel,
                    [this.props.record.resId],
                    [this.props.name]
                );
                photoIds = result[0]?.[this.props.name] || [];
            } catch (e) {
                console.error("Failed to fetch photo ids", e);
            }
        }

        if (!photoIds.length) {
            this.state.photos = [];
            return;
        }

        this.state.loading = true;
        try {
            const records = await this.orm.read(
                "hill.site.photo",
                photoIds,
                ["id", "attachment_id", "name", "mimetype", "file_size", "uploaded_at"]
            );
            this.state.photos = records.map((r) => ({
                id: r.id,
                attachmentId: r.attachment_id[0],
                name: r.name,
                mimetype: r.mimetype,
                size: r.file_size,
                uploadedAt: r.uploaded_at,
                url: `/web/image/${r.attachment_id[0]}`,
            }));
        } catch (e) {
            console.error("HillPhotoWidget: failed to load", e);
        } finally {
            this.state.loading = false;
        }
    }

    onDragOver(ev) {
        ev.preventDefault();
        this.state.dragOver = true;
    }

    onDragLeave(ev) {
        ev.preventDefault();
        this.state.dragOver = false;
    }

    async onDrop(ev) {
        ev.preventDefault();
        this.state.dragOver = false;
        const files = Array.from(ev.dataTransfer.files).filter((f) =>
            f.type.startsWith("image/")
        );
        if (files.length) await this._processFiles(files);
    }

    onClickUpload() {
        if (!this.props.readonly) {
            this.state.showUploadOptions = !this.state.showUploadOptions;
        }
    }

    onClickGallery() {
        this.state.showUploadOptions = false;
        this.fileInputRef.el.click();
    }

    onClickCamera() {
        this.state.showUploadOptions = false;
        this._openWebcamModal();
    }

    async _openWebcamModal() {
        if (this.props.readonly) return;
        this._requestGeolocation();
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            this.notification.add(_t("Camera is not supported on this device."), { type: "warning" });
            return;
        }
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: "environment" } 
            });
            this.state.webcamStream = stream;
            this.state.showWebcam = true;
            setTimeout(() => this._setVideoStream(), 50);
            this.state.showWebcamError = false;
        } catch (e) {
            console.error("Webcam access failed", e);
            this.state.showWebcamError = true;
            this.notification.add(
                _t("Cannot access camera. Please check permissions."),
                { type: "danger" }
            );
        }
    }

    closeWebcamModal() {
        if (this.state.webcamStream) {
            this.state.webcamStream.getTracks().forEach(t => t.stop());
            this.state.webcamStream = null;
        }
        this.state.showWebcam = false;
    }

    captureFromWebcam() {
        const videoEl = document.querySelector(".mv_webcam_video");
        if (!videoEl || !videoEl.srcObject) return;
        const canvas = document.createElement("canvas");
        canvas.width = videoEl.videoWidth || 640;
        canvas.height = videoEl.videoHeight || 480;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoEl, 0, 0);
        canvas.toBlob(blob => {
            if (blob) {
                const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
                this.state.pendingCapture = {
                    blob,
                    name: "webcam-capture.jpg",
                    dataUrl,
                };
                this.closeWebcamModal();
            }
        }, "image/jpeg", 0.9);
    }

    _requestGeolocation() {
        if (!navigator.geolocation) {
            this.state.geolocation = null;
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                this.state.geolocation = {
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                };
            },
            () => {
                this.state.geolocation = null;
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
        );
    }

    async confirmCapture() {
        if (!this.state.pendingCapture) return;
        const file = new File(
            [this.state.pendingCapture.blob],
            this.state.pendingCapture.name,
            { type: "image/jpeg" }
        );
        this.state.pendingCapture = null;
        await this._processFiles([file], true);
    }

    retakeCapture() {
        this.state.pendingCapture = null;
        this._openWebcamModal();
    }

    async onFileChange(ev) {
        const files = Array.from(ev.target.files);
        await this._processFiles(files);
        ev.target.value = "";
    }

    async _processFiles(files, isWebcam = false) {
        if (this.props.readonly) return;

        const recordId = this.props.record?.resId;
        const model = this.props.record?.resModel;

        if (!recordId) {
            this.notification.add(
                _t("Save the record first before uploading photos."),
                { type: "info" }
            );
            return;
        }

        this.state.uploading = true;
        this.state.progress = 0;
        this.state.queue = files.map((f) => ({ name: f.name, status: "pending" }));

        let successCount = 0;

        for (let i = 0; i < files.length; i++) {
            this.state.queue[i].status = "uploading";
            try {
                const data = await this._readFileAsBase64(files[i]);
                const result = await this.orm.create("ir.attachment", [{
                    name: files[i].name,
                    datas: data,
                    mimetype: files[i].type,
                    res_model: model,
                    res_id: recordId,
                }]);

                const attachmentId = result[0];
                const photoVals = {
                    site_report_id: recordId,
                    attachment_id: attachmentId,
                };
                if (isWebcam) {
                    photoVals.is_webcam_capture = true;
                    if (this.state.geolocation) {
                        photoVals.geo_latitude = this.state.geolocation.lat;
                        photoVals.geo_longitude = this.state.geolocation.lon;
                    }
                }
                await this.orm.create("hill.site.photo", [photoVals]);

                successCount++;
                this.state.queue[i].status = "done";
            } catch (e) {
                this.notification.add(
                    sprintf(_t("Upload failed: %s"), files[i].name),
                    { type: "danger" }
                );
                this.state.queue[i].status = "error";
                console.error(e);
            }
            this.state.progress = Math.round(((i + 1) / files.length) * 100);
        }

        await this.props.record.load();
        await this.loadPhotos();
        this.state.uploading = false;
        this.state.queue = [];

        if (successCount > 0) {
            this.notification.add(
                sprintf(_t("%s photo(s) uploaded successfully"), successCount),
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

    async removePhoto(ev, photoId) {
        ev.stopPropagation();
        if (this.props.readonly) return;

        await this.orm.unlink("hill.site.photo", [photoId]);
        await this.props.record.load();
        await this.loadPhotos();
    }

    openLightbox(photo) {
        this.state.selectedPhoto = photo;
        this.state.lightbox = true;
    }

    closeLightbox() {
        this.state.lightbox = false;
        this.state.selectedPhoto = null;
    }

    _onDocumentClick(ev) {
        if (this.state.showUploadOptions && this.clickOutsideRef?.el && !this.clickOutsideRef.el.contains(ev.target)) {
            this.state.showUploadOptions = false;
        }
    }

    navigate(dir) {
        const photos = this.state.photos;
        if (!photos.length) return;
        const currentId = this.state.selectedPhoto?.id;
        const idx = photos.findIndex((p) => p.id === currentId);
        this.state.selectedPhoto =
            photos[(idx + dir + photos.length) % photos.length];
    }

    fmtSize(bytes) {
        if (!bytes) return "";
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / 1048576).toFixed(1) + " MB";
    }

    downloadPhoto(ev, photo) {
        ev.stopPropagation();
        if (photo.url) window.open(photo.url, "_blank");
    }
}

registry.category("fields").add("hill_photo_widget", {
    component: HillPhotoWidget,
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
