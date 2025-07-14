(async function () {
    if (mw.config.get('wgNamespaceNumber') !== 104) return; // Only on Index pages

    // Create the button
    const ocrButton = $('<button>')
        .text('🧠 OCR All Pages')
        .css({ margin: '10px', padding: '5px' })
        .click(startBulkOCR);

    $('#bodyContent').prepend(ocrButton);

    async function startBulkOCR() {
        const indexTitle = mw.config.get('wgPageName');
        const site = mw.config.get('wgServer') + mw.config.get('wgScriptPath');

        const langCode = mw.config.get('wgContentLanguage') || 'hi';

        const indexData = await $.getJSON(site + '/api.php', {
            action: 'query',
            format: 'json',
            prop: 'proofread',
            titles: indexTitle,
            formatversion: 2
        });

        const indexPages = indexData.query.pages[0].proofread.pageList;

        for (const page of indexPages) {
            const pageTitle = 'Page:' + indexTitle.replace('Index:', '') + '/' + page;
            console.log(`Processing ${pageTitle}...`);

            const imageInfo = await $.getJSON(site + '/api.php', {
                action: 'query',
                format: 'json',
                prop: 'imageinfo',
                titles: pageTitle,
                iiprop: 'url',
                iiurlwidth: 1024
            });

            const imagePage = Object.values(imageInfo.query.pages)[0];
            const imageUrl = imagePage.imageinfo?.[0]?.thumburl;

            if (!imageUrl) {
                console.warn(`No image for ${pageTitle}`);
                continue;
            }

            // OCR from wmcloud.org
            const ocrText = await $.get(`https://ocr.wmcloud.org/api/ocr/${langCode}?image_url=${encodeURIComponent(imageUrl)}`);

            // Save using API (requires CSRF token)
            const tokenRes = await $.getJSON(site + '/api.php', {
                action: 'query',
                meta: 'tokens',
                format: 'json'
            });

            const token = tokenRes.query.tokens.csrftoken;

            const saveRes = await $.post(site + '/api.php', {
                action: 'edit',
                title: pageTitle,
                text: ocrText,
                summary: 'Auto OCR via custom script',
                token: token,
                format: 'json'
            });

            if (saveRes.edit?.result === 'Success') {
                console.log(`✅ Saved ${pageTitle}`);
            } else {
                console.error(`❌ Failed ${pageTitle}`, saveRes);
            }

            // Optional delay between pages (to avoid flooding)
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        alert("📘 OCR complete for all pages.");
    }
})();
