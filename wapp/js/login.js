var nameEl = document.querySelector('#loginname');
var pwdEl = document.querySelector('input[name=password]');

nameEl.value = 'aaa';
pwdEl.value = 'bbb';

document.querySelector('[action-type=btn_submit]').click();