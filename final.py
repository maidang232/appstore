# -*- coding: utf-8 -*-
log = []

# ========== admin.html ==========
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    h = f.read()

# 1. 清除背景按钮 + 背景显示方式
if 'clearCardBg' not in h and 'edit-preview' in h:
    key = 'onclick="document.getElementById(\'edit-image-input\').click()"><span>点击上传背景图片</span></div>'
    if key in h:
        add = key + '''
<button type="button" class="btn-danger" style="margin-top:6px;font-size:11px;padding:4px 10px" onclick="clearCardBg()">清除背景图</button>
<div style="margin-top:12px"><label style="font-size:13px;font-weight:600;color:#333">背景显示方式</label><select id="edit-bg-fit" style="width:100%;padding:10px;border-radius:8px;border:1.5px solid #e8eaf0;background:#fafbfd;font-size:13px"><option value="contain">完整显示</option><option value="cover">铺满</option><option value="100% 100%">拉伸</option></select></div>'''
        h = h.replace(key, add, 1)
        log.append('OK admin: 清除按钮+显示方式')

# 2. 图标上传（只加到 group-icon 后面，靠 JS 控制显示）
if 'edit-icon-file' not in h and 'group-icon' in h:
    key = '<div class="form-group" id="group-icon"><label>图标 Emoji</label><input id="edit-icon" placeholder="输入一个 Emoji"></div>'
    alt_key = '<div class="form-group" id="group-icon">'
    pos = h.find(alt_key)
    if key in h:
        add = '''<div class="form-group" id="group-icon"><label>图标 Emoji</label><input id="edit-icon" placeholder="输入一个 Emoji">
<input type="file" id="edit-icon-file" accept="image/*" style="display:none" onchange="uploadIcon()">
<button type="button" class="btn-add" style="margin-top:6px" onclick="document.getElementById('edit-icon-file').click()">📷 上传图标（1:1 PNG）</button>
<div id="edit-icon-preview" style="width:60px;height:60px;background-size:contain;background-repeat:no-repeat;background-position:center;border-radius:8px;margin-top:8px;background-color:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:10px">未设置</div>
<input id="edit-icon-url" type="hidden">
<button type="button" class="btn-danger" style="margin-top:6px;font-size:11px;padding:4px 10px" onclick="clearIcon()">清除图标</button></div>'''
        h = h.replace(key, add, 1)
        log.append('OK admin: 图标上传区')

# 3. JS 函数
if 'async function uploadIcon' not in h:
    fn = '''
async function uploadIcon(){
  var fi=document.getElementById('edit-icon-file'); var f=fi.files[0]; if(!f)return;
  var fd=new FormData(); fd.append('file',f);
  var res=await fetch('/api/upload',{method:'POST',headers:{'X-Admin-Token':'admin123'},body:fd});
  var data=await res.json();
  if(data.url){document.getElementById('edit-icon-url').value=data.url;var pv=document.getElementById('edit-icon-preview');pv.style.backgroundImage='url('+data.url+')';pv.innerHTML='';}
}
function clearIcon(){document.getElementById('edit-icon-url').value='';var pv=document.getElementById('edit-icon-preview');pv.style.backgroundImage='';pv.innerHTML='未设置';}
function clearCardBg(){document.getElementById('edit-image-url').value='';var pv=document.getElementById('edit-preview');pv.style.backgroundImage='';pv.innerHTML='<span>点击上传背景图片</span>';}
'''
    h = h.replace('function openModal(', fn + 'function openModal(', 1)
    log.append('OK admin: 3个JS函数')

# 4. openModal 控制图标显示
if "icon-upload" not in h:
    old = "if (type === 'tool') document.getElementById('group-icon').style.display = 'block';"
    if old in h:
        new = old + "\n  document.getElementById('group-icon').style.display = (type === 'notice' || type === 'banner') ? 'none' : 'block';"
        h = h.replace(old, new, 1)
        log.append('OK admin: 公告不显示图标')

# 5. 保存 icon_url
if "icon_url: document.getElementById('edit-icon-url')" not in h:
    old = "color: document.getElementById('edit-color').value"
    if old in h:
        h = h.replace(old, old + ",\n    icon_url: document.getElementById('edit-icon-url').value,\n    bg_fit: document.getElementById('edit-bg-fit') ? document.getElementById('edit-bg-fit').value : 'contain'", 1)
        log.append('OK admin: saveItem 加字段')

# 6. saveAll 加字段
if "icon_url: item.icon_url" not in h:
    old = "color: item.color || '#f0f0f0' }"
    if old in h:
        h = h.replace(old, "color: item.color || '#f0f0f0', icon_url: item.icon_url || '', bg_fit: item.bg_fit || 'contain' }", 1)
        log.append('OK admin: saveAll 加字段')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(h)

# ========== store.html ==========
with open('templates/store.html', 'r', encoding='utf-8') as f:
    s = f.read()

# 工具卡片：背景 size + 显示图标
if 'background-size:${bgFit}' not in s:
    old = "background-position:${bgPos};${bgClr?'background-color:'+bgClr:''}"
    if old in s:
        new = "background-position:${bgPos};background-size:${x.bg_fit||'contain'};${bgClr?'background-color:'+bgClr:''}"
        s = s.replace(old, new, 1)
        log.append('OK store: 工具卡片背景size')

# 应用列表显示 icon_url
if "a.icon_url ? `<img src=\"${a.icon_url}\"" not in s:
    old = "${a.icon_url ? `<img src=\"${a.icon_url}\" style=\"width:100%;height:100%;object-fit:cover;border-radius:12px\">` : '📦'}"
    if old in s:
        new = "${a.icon_url ? `<img src=\"${a.icon_url}\" style=\"width:100%;height:100%;object-fit:contain;border-radius:12px\">` : '📦'}"
        s = s.replace(old, new, 1)
        log.append('OK store: 应用图标 contain')

# 公告卡片背景size
old2 = "style=\"background-image:url('${bgImg}');background-position:${bgPos};${bgClr?'background-color:'+bgClr:''}\" onclick=\"openNotice"
new2 = "style=\"background-image:url('${bgImg}');background-position:${bgPos};background-size:${x.bg_fit||'contain'};${bgClr?'background-color:'+bgClr:''}\" onclick=\"openNotice"
if old2 in s:
    s = s.replace(old2, new2, 1)
    log.append('OK store: 公告背景size')

with open('templates/store.html', 'w', encoding='utf-8') as f:
    f.write(s)

print('\n'.join(log))
print('=== 完成 ===')
