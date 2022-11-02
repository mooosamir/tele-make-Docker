/** @tele-module **/
/* global BarcodeDetector */

import Dialog from "web.TwlDialog";
import { delay } from "web.concurrency";
import { loadAssets } from "@web/core/assets";

const { core, Component, hooks, mount } = twl;
import { _t } from 'web.core';
const { useRef } = hooks;
const bus = new core.EventBus();
const busOk = "BarcodeDialog-Ok";
const busError = "BarcodeDialog-Error";

/**
 * Check for HTMLVideoElement readiness.
 *
 * See https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/readyState
 */
const HAVE_NOTHING = 0;
const HAVE_METADATA = 1;
function isVideoElementReady(video) {
    return ![HAVE_NOTHING, HAVE_METADATA].includes(video.readyState);
}

/**
 * Builder for BarcodeDetector-like polyfill class using ZXing library.
 *
 * @param {ZXing} ZXing Zxing library
 * @returns {class} ZxingBarcodeDetector class
 */
function buildZXingBarcodeDetector(ZXing) {
    const ZXingFormats = new Map([
        ["aztec", ZXing.BarcodeFormat.AZTEC],
        ["code_39", ZXing.BarcodeFormat.CODE_39],
        ["code_128", ZXing.BarcodeFormat.CODE_128],
        ["data_matrix", ZXing.BarcodeFormat.DATA_MATRIX],
        ["ean_8", ZXing.BarcodeFormat.EAN_8],
        ["ean_13", ZXing.BarcodeFormat.EAN_13],
        ["itf", ZXing.BarcodeFormat.ITF],
        ["pdf417", ZXing.BarcodeFormat.PDF_417],
        ["qr_code", ZXing.BarcodeFormat.QR_CODE],
        ["upc_a", ZXing.BarcodeFormat.UPC_A],
        ["upc_e", ZXing.BarcodeFormat.UPC_E],
    ]);

    const allSupportedFormats = Array.from(ZXingFormats.keys());

    /**
     * ZXingBarcodeDetector class
     *
     * BarcodeDetector-like polyfill class using ZXing library.
     * API follows the Shape Detection Web API (specifically Barcode Detection).
     */
    class ZXingBarcodeDetector {
        /**
         * @param {object} opts
         * @param {Array} opts.formats list of codes' formats to detect
         */
        constructor(opts = {}) {
            const formats = opts.formats || allSupportedFormats;
            const hints = new Map([
                [ZXing.DecodeHintType.POSSIBLE_FORMATS, formats.map((format) => ZXingFormats.get(format))],
                // Enable Scanning at 90 degrees rotation
                // https://github.com/zxing-js/library/issues/291
                [ZXing.DecodeHintType.TRY_HARDER, true],
            ]);
            this.reader = new ZXing.MultiFormatReader();
            this.reader.setHints(hints);
        }

        /**
         * Detect codes in image.
         *
         * @param {HTMLVideoElement} video source video element
         * @returns {Promise<Array>} array of detected codes
         */
        async detect(video) {
            if (!(video instanceof HTMLVideoElement)) {
                throw new DOMException("imageDataFrom() requires an HTMLVideoElement", "InvalidArgumentError");
            }
            if (!isVideoElementReady(video)) {
                throw new DOMException("HTMLVideoElement is not ready", "InvalidStateError");
            }
            const canvas = document.createElement("canvas");
            const ctx = canvas.getContext("2d");

            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

            const luminanceSource = new ZXing.HTMLCanvasElementLuminanceSource(canvas);
            const binaryBitmap = new ZXing.BinaryBitmap(new ZXing.HybridBinarizer(luminanceSource));
            try {
                const result = this.reader.decode(binaryBitmap);
                const format = Array.from(ZXingFormats).find(([k, val]) => val === result.getBarcodeFormat());
                const rawValue = result.getText();
                return [
                    {
                        format,
                        rawValue,
                    },
                ];
            } catch (err) {
                if (err.name === "NotFoundException") {
                    return [];
                }
                throw err;
            }
        }
    }

    /**
     * Supported codes formats
     *
     * @static
     * @returns {Array}
     */
    ZXingBarcodeDetector.getSupportedFormats = async () => allSupportedFormats;

    return ZXingBarcodeDetector;
}
class BarcodeDialog extends Component {
    /**
     * @override
     */
    constructor() {
        super(...arguments);
        this.videoPreviewRef = useRef("videoPreview");
        this.interval = null;
        this.stream = null;
        this.detector = null;
    }

    async willStart() {
        let DetectorClass;
        // Use Barcode Detection API if available.
        // As support is still bleeding edge (mainly Chrome on Android),
        // also provides a fallback using ZXing library.
        if ("BarcodeDetector" in window) {
            DetectorClass = BarcodeDetector;
        } else {
            await loadAssets({
                jsLibs: ["/web_enterprise/static/lib/zxing-library/zxing-library.js"],
            });
            DetectorClass = buildZXingBarcodeDetector(window.ZXing);
        }
        const formats = await DetectorClass.getSupportedFormats();
        this.detector = new DetectorClass({ formats });
    }

    async mounted() {
        const constraints = {
            video: { facingMode: "environment" },
            audio: false,
        };

        try {
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (err) {
            const errors = {
                NotFoundError: _t('No device can be found.'),
                NotAllowedError: _t('Tele needs your authorization first.'),
            };
            const errorMessage = _t('Could not start scanning. ') + (errors[err.name] || err.message);
            this.onError(new Error(errorMessage));
            return;
        }
        this.videoPreviewRef.el.srcObject = this.stream;
        await this.isVideoReady();
        this.interval = setInterval(this.detectCode.bind(this), 100);
    }

    willUnmount() {
        clearInterval(this.interval);
        this.interval = null;
        if (this.stream) {
            this.stream.getTracks().forEach((track) => track.stop());
            this.stream = null;
        }
    }

    /**
     * Check for camera preview element readiness
     *
     * @returns {Promise} resolves when the video element is ready
     */
    async isVideoReady() {
        // FIXME: even if it shouldn't happend, a timeout could be useful here.
        return new Promise(async (resolve) => {
            while (!isVideoElementReady(this.videoPreviewRef.el)) {
                await delay(10);
            }
            resolve();
        });
    }

    /**
     * Detection success handler
     *
     * @param {string} result found code
     */
    onResult(result) {
        this.closeDialog();
        bus.trigger(busOk, result);
    }

    /**
     * Detection error handler
     *
     * @param {Error} error
     */
    onError(error) {
        this.closeDialog();
        bus.trigger(busError, { error });
    }

    /**
     * Close the dialog.
     */
    closeDialog() {
        this.destroy();
    }

    /**
     * Attempt to detect codes in the current camera preview's frame
     */
    async detectCode() {
        try {
            const codes = await this.detector.detect(this.videoPreviewRef.el);
            if (codes.length === 0) {
                return;
            }
            this.onResult(codes[0].rawValue);
        } catch (err) {
            this.onError(err);
        }
    }
}

Object.assign(BarcodeDialog, {
    components: {
        Dialog,
    },
    template: "web_enterprise.BarcodeDialog",
});

/**
 * Check for BarcodeScanner support
 * @returns {boolean}
 */
export function isBarcodeScannerSupported() {
    return navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
}

/**
 * Opens the BarcodeScanning dialog and begins code detection using the device's camera.
 *
 * @returns {Promise<string>} resolves when a {qr,bar}code has been detected
 */
export async function scanBarcode() {
    const promise = new Promise((resolve, reject) => {
        bus.on(busOk, null, resolve);
        bus.on(busError, null, reject);
    });
    await mount(BarcodeDialog, { target: document.body });
    return promise;
}
