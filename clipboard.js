// ==UserScript==
// @name         Disable clipboard auto-copy
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Disable clipboard auto-copy
// @match        https://*.baidu.com/*
// @match        https://*.jianshu.com/*
// @grant        none
// ==/UserScript==
function setClipboardText(event) {
    event.preventDefault();
    var result = window.getSelection().toString();
    if (result && confirm("是否允许复制内容：\n" + result ) == true){
        if(event.clipboardData){
            event.clipboardData.setData("text/html", result);
            event.clipboardData.setData('text/plain', result);
        }
        else if(window.clipboardData){
            return window.clipboardData.setData("text", text);
        }
        return true;
    }else{
        document.execCommand = () => {};
        navigator.clipboard.writeText = () => {};
        return false;
    }
};

document.addEventListener('copy', function (event) {
    setClipboardText(event);
});
