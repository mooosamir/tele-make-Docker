/** @tele-module */

import tour from 'web_tour.tour';
import wTourUtils from 'website.tour_utils';

const clickOnImgStep = {
    content: "Click somewhere else to save.",
    trigger: '#wrap .s_text_image img',
};

tour.register('link_tools', {
    test: true,
    url: '/?enable_editor=1',
}, [
    // 1. Create a new link from scratch.
    wTourUtils.dragNDrop({
        id: 's_text_image',
        name: 'Text - Image',
    }),
    {
        content: "Replace first paragraph, to insert a new link",
        trigger: '#wrap .s_text_image p',
        run: 'text Go to tele: '
    },
    {
        content: "Open link tools",
        trigger: "#toolbar #create-link",
    },
    {
        content: "Type the link URL tele.studio",
        trigger: '#o_link_dialog_url_input',
        run: 'text tele.studio'
    },
    clickOnImgStep,
    // 2. Edit the link with the link tools.
    {
        content: "Click on the newly created link, change content to tele website",
        trigger: '.s_text_image a[href="http://tele.studio"]:contains("tele.studio")',
        run: 'text tele website',
    },
    {
        content: "Link tools, should be open, change the url",
        trigger: '#o_link_dialog_url_input',
        run: 'text tele.be'
    },
    clickOnImgStep,
    ...wTourUtils.clickOnSave(),
    // 3. Edit a link after saving the page.
    wTourUtils.clickOnEdit(),
    {
        content: "The new link content should be tele website and url tele.be",
        extra_trigger: "#oe_snippets.o_loaded",
        trigger: '.s_text_image a[href="http://tele.be"]:contains("tele website")',
    },
    {
        content: "The new link content should be tele website and url tele.be",
        trigger: '#toolbar button[data-original-title="Link Style"]',
    },
    {
        trigger: 'body',
        run: () => {
            // When doing automated testing, the link popover takes time to
            // hide. While hidding, the editor observer is unactive in order to
            // prevent the popover mutation to be recorded. In a manual
            // scenario, the popover has plenty of time to be hidden and the
            // obsever would be re-activated in time. As this problem arise only
            // in test, we activate the observer here for the popover.
            $('#wrapwrap').data('wysiwyg').teleEditor.observerActive('hide.bs.popover');
        },
    },
    {
        content: "Click on the secondary style button.",
        trigger: '#toolbar we-button[data-value="secondary"]',
    },
    ...wTourUtils.clickOnSave(),
    {
        content: "The link should have the secondary button style.",
        trigger: '.s_text_image a.btn.btn-secondary[href="http://tele.be"]:contains("tele website")',
        run: () => {}, // It's a check.
    },
    // 4. Add link on image.
    wTourUtils.clickOnEdit(),
    {
        content: "Click on image.",
        trigger: '.s_text_image img',
        extra_trigger: '#oe_snippets.o_loaded',
    },
    {
        content: "Activate link.",
        trigger: '.o_we_customize_panel we-row:contains("Media") we-button.fa-link',
    },
    {
        content: "Set URL.",
        trigger: '.o_we_customize_panel we-input:contains("Your URL") input',
        run: 'text tele.studio',
    },
    {
        content: "Deselect image.",
        trigger: '.s_text_image p',
    },
    {
        content: "Re-select image.",
        trigger: '.s_text_image img',
    },
    {
        content: "Check that link tools appear.",
        trigger: '.popover div a:contains("http://tele.studio")',
        run: () => {}, // It's a check.
    },
    // 5. Remove link from image.
    {
        content: "Remove link.",
        trigger: '.popover:contains("http://tele.studio") a .fa-chain-broken',
    },
    {
        content: "Check that image is not within a link anymore.",
        trigger: '.s_text_image div > img',
        run: () => {}, // It's a check.
    },
]);
