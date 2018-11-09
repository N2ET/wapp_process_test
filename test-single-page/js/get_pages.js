var linkSelector = '.header-nav_column-title-link';

function $ = function(selector) {
    return document.querySelector(selector);
}

var map = {};
var pages = [];

var homePageDom = $('[utid=home-page] .active');
pages.push({
    text: homePageDom.innerText.trim(),
    url: dom.href
});

$(linkSelector).forEach(function(dom) {
    var url = dom.href;
    var mod = url.replace(/\?.*$/g, '');
    var text = dom.innerText.trim();

    if(map[mod]) {
        return;
    }

    map[mod] = 1;
    pages.push({
        name: text,
        url: url
    });
});

return pages;