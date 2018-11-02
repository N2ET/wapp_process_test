/**
 *  实验功能！谨慎使用！
 *  通过 chrome://memory-internals/ 获取标签页进程id
 */

window.processData = window.processData || [];

if(!window._returnProcessList) {
    console.log('init returnProcessList');
    window._returnProcessList = returnProcessList;

	// returnProcessList is async function
    returnProcessList = function(data) {
        console.log('returnProcessList', data);
        processData = data.processes;
        window._returnProcessList.apply(this, arguments);    
    }
}

// update process list
console.log('requestProcessList');
requestProcessList();


// get Renderer process list
var ret = processData.map(function(item) {
    console.log('filter: ', item);
    return item[1] === 'Renderer' ? item[0] : false;
}).filter(function(item) {
    return item;
})
console.log('ret ', ret);
return ret;