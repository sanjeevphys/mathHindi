if (mw.config.get('wgNamespaceNumber') === 104) {
    const ocrButton = $('<button>')
        .text('🧠 OCR All Pages')
        .css({ margin: '10px', padding: '5px' })
        .click(() => alert('OCR script would run here.'));

    $('#bodyContent').prepend(ocrButton);
    console.log("✅ OCR button added on Index page");
}
