const PORT = 8049;

function sendCurrTab(url) {
    fetch(`http://127.0.0.1:${PORT}/send_url`, {
        method: 'POST',
        body: new URLSearchParams({ url: url })
    })
}

chrome.tabs.onActivated.addListener((activeInfo) => {
    chrome.tabs.get(activeInfo.tabId, (tab) => {
        sendCurrTab(tab.url);
    });
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (tab.active && changeInfo.url) {
        sendCurrTab(changeInfo.url);
    }
});