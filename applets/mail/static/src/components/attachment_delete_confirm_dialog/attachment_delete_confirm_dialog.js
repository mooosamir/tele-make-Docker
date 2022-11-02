/** @tele-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

import Dialog from 'web.TwlDialog';

const { Component } = twl;
const { useRef } = twl.hooks;

export class AttachmentDeleteConfirmDialog extends Component {

    /**
     * @override
     */
    constructor(...args) {
        super(...args);
        // to manually trigger the dialog close event
        this._dialogRef = useRef('dialog');
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {mail.attachment}
     */
    get attachment() {
        return this.messaging && this.messaging.models['mail.attachment'].get(this.props.attachmentLocalId);
    }

    /**
     * @returns {string}
     */
    getBody() {
        return _.str.sprintf(
            this.env._t(`Do you really want to delete "%s"?`),
            twl.utils.escape(this.attachment.displayName)
        );
    }

    /**
     * @returns {string}
     */
    getTitle() {
        return this.env._t("Confirmation");
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onClickCancel() {
        this._dialogRef.comp._close();
    }

    /**
     * @private
     */
    async _onClickOk() {
        await this.attachment.remove();
        this._dialogRef.comp._close();
        this.trigger('o-attachment-removed', { attachmentLocalId: this.props.attachmentLocalId });
    }

}

Object.assign(AttachmentDeleteConfirmDialog, {
    components: { Dialog },
    props: {
        attachmentLocalId: String,
    },
    template: 'mail.AttachmentDeleteConfirmDialog',
});

registerMessagingComponent(AttachmentDeleteConfirmDialog);
