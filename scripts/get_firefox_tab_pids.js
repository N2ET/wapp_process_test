function getPids(url) {

    var sections = document.querySelectorAll('.section');
    var pid;
    sections = [].slice.call(sections, 1);
    sections.some(function(section) {
        var items = document.querySelectorAll('.mrName');
        var linkDom;

        [].slice.call(items).some(function (dom) {
            if (dom.textContent.indexOf(url) !== -1) {
                linkDom = dom;
                return true;
            }
        });

        if (!linkDom) {
            return;
        }

        var ret = section.firstElementChild.textContent.match(/Web Content \(pid (\d+)\)/);
        if (ret && ret[1]) {
            pid = Number(ret[1]);
            return true;
        }
    });

    return pid ? [pid] : [];
}