/** 台灣政府補助新聞網：訂閱／取消訂閱（同一 Email 再送一次即切換）
 * 綁定試算表「台灣政府補助新聞網訂閱名單」。部署為網頁應用程式（執行身分：我；存取權：所有人）。
 * 呼叫：GET ?email=xxx&callback=fn（JSONP）或 POST email=xxx。回傳 {status:"subscribed"|"unsubscribed"|"invalid"|"wait"}
 */
var HEADER = ['電子郵件', '狀態', '訂閱時間', '取消時間', '最後更新'];
function doGet(e) { return respond_(handle_(e && e.parameter && e.parameter.email), e && e.parameter && e.parameter.callback); }
function doPost(e) {
  var email = e && e.parameter && e.parameter.email;
  if (!email && e && e.postData && e.postData.contents) {
    try { email = JSON.parse(e.postData.contents).email; } catch (x) {}
  }
  return respond_(handle_(email), e && e.parameter && e.parameter.callback);
}
function handle_(raw) {
  var email = String(raw || '').trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return { status: 'invalid' };
  var cache = CacheService.getScriptCache(), key = 'sub_' + Utilities.base64EncodeWebSafe(email);
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    var last = cache.get(key);
    if (last) return { status: 'wait', current: last };          // 30 秒內同一 Email 只處理一次
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    var head = sh.getRange(1, 1, 1, HEADER.length).getValues()[0];
    if (head.join('|') !== HEADER.join('|')) sh.getRange(1, 1, 1, HEADER.length).setValues([HEADER]);
    var now = new Date(), n = sh.getLastRow(), status;
    var emails = n > 1 ? sh.getRange(2, 1, n - 1, 1).getValues().map(function (r) { return String(r[0]).toLowerCase(); }) : [];
    var i = emails.indexOf(email);
    if (i < 0) { sh.appendRow([email, '訂閱中', now, '', now]); status = 'subscribed'; }
    else {
      var row = i + 2, cur = sh.getRange(row, 2).getValue();
      if (cur === '訂閱中') { sh.getRange(row, 2).setValue('已取消'); sh.getRange(row, 4).setValue(now); status = 'unsubscribed'; }
      else { sh.getRange(row, 2).setValue('訂閱中'); sh.getRange(row, 3).setValue(now); sh.getRange(row, 4).setValue(''); status = 'subscribed'; }
      sh.getRange(row, 5).setValue(now);
    }
    cache.put(key, status, 30);
    return { status: status };
  } finally { lock.releaseLock(); }
}
function respond_(obj, cb) {
  var json = JSON.stringify(obj);
  if (cb && /^[A-Za-z_$][\w$]{0,40}$/.test(cb))
    return ContentService.createTextOutput(cb + '(' + json + ')').setMimeType(ContentService.MimeType.JAVASCRIPT);
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}
