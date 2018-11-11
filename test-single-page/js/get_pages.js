var linkSelector = '.header-nav_column-title-link';

function $(selector) {
    return document.querySelectorAll(selector);
}

var map = {};
var pages = [];

var homePageDom = $('[utid=home-page] .active')[0];
pages.push({
    text: homePageDom.innerText.trim(),
    url: homePageDom.href
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