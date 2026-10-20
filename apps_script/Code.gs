/** 台灣政府補助新聞網：訂閱／取消訂閱（資安加固版，2026-10-18）
 * 變更：1) 拒絕 = + - @ 開頭與含控制字元的輸入，寫入前一律加 ' 前綴，防公式注入
 *       2) 全站速率限制：每 10 分鐘新增訂閱超過 30 筆即暫停（回 busy），防灌水
 *       3) 網頁表單只能「訂閱」；「取消」必須帶 HMAC token（電子報內的取消連結），防止別人代為取消
 * 2026-10-20：每次訂閱／取消訂閱即寄通知信（notify_），附 Email 與目前訂閱總人數。
 * 部署前：專案設定 → 指令碼屬性 新增 UNSUB_SECRET（隨機 32 字元以上）。電子報取消連結改用 unsubUrl_(email)。
 */
var HEADER = ['電子郵件', '狀態', '訂閱時間', '取消時間', '最後更新'];
var WEBAPP_URL = ScriptApp.getService().getUrl();
function doGet(e) { var p = (e && e.parameter) || {}; return respond_(handle_(p), p.callback); }
function doPost(e) {
  var p = (e && e.parameter) || {};
  if (!p.email && e && e.postData && e.postData.contents) { try { p.email = JSON.parse(e.postData.contents).email; } catch (x) {} }
  return respond_(handle_(p), p.callback);
}
function token_(email) {
  var secret = PropertiesService.getScriptProperties().getProperty('UNSUB_SECRET') || '';
  return Utilities.base64EncodeWebSafe(Utilities.computeHmacSha256Signature(email, secret)).slice(0, 22);
}
function unsubUrl_(email) { return WEBAPP_URL + '?act=unsub&email=' + encodeURIComponent(email) + '&t=' + token_(email); }
function safe_(v) { return "'" + String(v); }
function handle_(p) {
  var email = String(p.email || '').trim().toLowerCase();
  if (email.length > 254 || /[\x00-\x1f"'<>(),;:\\\[\]]/.test(email) || /^[=+\-@]/.test(email) ||
      !/^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}$/.test(email)) return { status: 'invalid' };
  var act = p.act === 'unsub' ? 'unsub' : 'sub';
  if (act === 'unsub' && p.t !== token_(email)) return { status: 'invalid' };
  var cache = CacheService.getScriptCache(), key = 'sub_' + Utilities.base64EncodeWebSafe(email);
  var lock = LockService.getScriptLock(); lock.waitLock(10000);
  try {
    if (cache.get(key)) return { status: 'wait' };
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    var head = sh.getRange(1, 1, 1, HEADER.length).getValues()[0];
    if (head.join('|') !== HEADER.join('|')) sh.getRange(1, 1, 1, HEADER.length).setValues([HEADER]);
    var now = new Date(), n = sh.getLastRow(), status;
    var emails = n > 1 ? sh.getRange(2, 1, n - 1, 1).getValues().map(function (r) { return String(r[0]).replace(/^'/, '').toLowerCase(); }) : [];
    var i = emails.indexOf(email);
    if (act === 'sub') {
      if (i < 0) {
        var cnt = Number(cache.get('rate') || 0);
        if (cnt >= 30) return { status: 'busy' };
        cache.put('rate', String(cnt + 1), 600);
        sh.appendRow([safe_(email), '訂閱中', now, '', now]); status = 'subscribed';
      } else {
        var row = i + 2;
        if (sh.getRange(row, 2).getValue() !== '訂閱中') { sh.getRange(row, 2).setValue('訂閱中'); sh.getRange(row, 3).setValue(now); sh.getRange(row, 4).setValue(''); }
        sh.getRange(row, 5).setValue(now); status = 'subscribed';
      }
    } else {
      if (i < 0) return { status: 'notfound' };
      var r2 = i + 2; sh.getRange(r2, 2).setValue('已取消'); sh.getRange(r2, 4).setValue(now); sh.getRange(r2, 5).setValue(now); status = 'unsubscribed';
    }
    cache.put(key, status, 30);
    try { notify_(email, status, sh); } catch (err) { console.error('notify_ 失敗：' + err); }
    return { status: status };
  } finally { lock.releaseLock(); }
}
function respond_(obj, cb) {
  var json = JSON.stringify(obj);
  if (cb && /^[A-Za-z_$][\w$]{0,40}$/.test(cb))
    return ContentService.createTextOutput(cb + '(' + json + ')').setMimeType(ContentService.MimeType.JAVASCRIPT);
  return ContentService.createTextOutput(json).setMimeType(ContentService.MimeType.JSON);
}

var NOTIFY_TO = 'tommyliu2009@gmail.com';
function notify_(email, status, sh) {
  var n = sh.getLastRow(), total = 0;
  if (n > 1) sh.getRange(2, 2, n - 1, 1).getValues().forEach(function (r) { if (r[0] === '訂閱中') total++; });
  var act = status === 'subscribed' ? '新訂閱' : '取消訂閱';
  var t = Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyy-MM-dd HH:mm');
  MailApp.sendEmail(NOTIFY_TO, '【台灣政府補助新聞網】' + act + '：' + email,
    '動作：' + act + '\nEmail：' + email + '\n時間：' + t + '（台北時間）\n目前訂閱總人數：' + total + ' 人\n');
}
/** 第一次部署後在編輯器手動執行一次，完成寄信授權並收到測試信 */
function testNotify() { notify_('test@example.com', 'subscribed', SpreadsheetApp.getActiveSpreadsheet().getSheets()[0]); }
