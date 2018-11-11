function $(selector, dom) {
    return (dom || document).querySelectorAll(selector);
}

var pages = [];

var groupTitleDomList = $('.nav-group__title');
var groupTitleDom = [].slice.call(groupTitleDomList).filter(function(dom) {
    return dom.innerText.trim().toLowerCase() == 'data';
})[0];

$('.pure-menu-list a[href]', groupTitleDom.parentNode).forEach(function(dom) {
    pages.push({
        name: dom.innerText.trim(),
        url: dom.href
    });
});

return pages;