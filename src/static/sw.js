// from https://blog.techbridge.cc/2018/10/13/pwa-in-action/
var installPromptEvent;

// 要顯示 prompt 的延遲
var showTime = 30 * 1000

self.addEventListener('beforeinstallprompt', function (e) {
  e.preventDefault()
  installPromptEvent = e
  var data = navigator.userAgent.match(/Chrom(e|ium)\\/([0-9]+)\\./)
  var version = (data && data.length >= 2) ? parseInt(data[2], 10) : null
  if (version && installPromptEvent.prompt) {

    // 延遲一段時間才顯示 prompt
    setTimeout(function() {
        // 如果 Chrome 版本是 67（含）以下，可以直接呼叫
        if (version <= 67) {
            installPromptEvent.prompt()
            return
        }

        // 否則的話必須透過 user action 主動觸發
        // 這邊幫 #root 加上 event listener，代表點擊螢幕任何一處都會顯示 prompt
        document.querySelector('#root').addEventListener('click', addToHomeScreen)
    }, showTime)
  }
});

function addToHomeScreen(e) {
    if (installPromptEvent) {
        installPromptEvent.prompt()
        installPromptEvent = null
        document.querySelector('#root').removeEventListener('click', addToHomeScreen)
    }
}
