import re
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    h = f.read()
if 'clearCardBg' not in h:
    old = '<input type="hidden" id="edit-image-url">'
    new = '<input type="hidden" id="edit-image-url">\n<button type="button" class="btn-danger" style="margin-top:6px;font-size:11px;padding:4px 10px" onclick="clearCardBg()">清除背景图</button>\n<label style="display:block;margin-top:12px;font-size:13px;font-weight:600;color:#333">卡片图标（1:1 PNG 透明）</label>\n<input type="file" id="edit-icon-input" accept="image/*" style="display:none" onchange="uploadIcon()">\n<button type="button" class="btn-add" onclick="document.getElementById(&apos;edit-icon-input&apos;).click()">上传图标图</button>\n<div id="edit-icon-preview" style="width:60px;height:60px;background-size:contain;background-repeat:no-repeat;background-position:center;border-radius:8px;margin-top:8px;background-color:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:10px">未设置</div>\n<input id="edit-icon-url" type="hidden">\n<button type="button" class="btn-danger" style="margin-top:6px;font-size:11px;padding:4px 10px" onclick="clearIcon()">清除图标</button>'
    if old in h:
        h = h.replace(old, new, 1)
        print('OK 弹窗已改')
    else:
        print('SKIP 找不到 edit-image-url')
if 'async function uploadIcon' not in h:
    fn = "\nfunction clearCardBg(){\n  document.getElementById('edit-image-url').value='';\n  var pv=document.getElementById('edit-preview');\n  pv.style.backgroundImage='';\n  pv.innerHTML='<span>点击上传背景图片</span>';\n}\nasync function uploadIcon(){\n  var fi=document.getElementById('edit-icon-input');\n  var f=fi.files[0];\n  if(!f)return;\n  var fd=new FormData();\n  fd.append('file',f);\n  var res=await fetch('/api/upload',{method:'POST',headers:{'X-Admin-Token':'admin123'},body:fd});\n  var data=await res.json();\n  if(data.url){\n    document.getElementById('edit-icon-url').value=data.url;\n    var pv=document.getElementById('edit-icon-preview');\n    pv.style.backgroundImage='url('+data.url+')';\n    pv.innerHTML='';\n  }\n}\nfunction clearIcon(){\n  document.getElementById('edit-icon-url').value='';\n  var pv=document.getElementById('edit-icon-preview');\n  pv.style.backgroundImage='';\n  pv.innerHTML='未设置';\n}\n"
    if 'function openModal(' in h:
        h = h.replace('function openModal(', fn + 'function openModal(', 1)
        print('OK JS 已加')
if "icon_url: document.getElementById('edit-icon-url')" not in h:
    old_s = "color: document.getElementById('edit-color').value"
    if old_s in h:
        h = h.replace(old_s, old_s + ",\n    icon_url: document.getElementById('edit-icon-url').value", 1)
        print('OK saveItem 已改')
if "icon_url: item.icon_url" not in h:
    old_f = "color: item.color || '#f0f0f0' }"
    if old_f in h:
        h = h.replace(old_f, "color: item.color || '#f0f0f0', icon_url: item.icon_url || '' }", 1)
        print('OK saveAll 已改')
with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(h)
with open('templates/store.html', 'r', encoding='utf-8') as f:
    s = f.read()
if 'const bgFit = x.bg_fit' not in s:
    old_line = "const bgImg = x.bg || x.image || '';"
    idx = s.find('renderToolsContent')
    if idx > 0:
        seg = s[idx:idx+2500]
        if old_line in seg:
            new_line = old_line + "\n    const bgFit = x.bg_fit || 'cover';\n    const iconPart = x.icon_url ? '<img src=\"'+x.icon_url+'\" style=\"width:44px;height:44px;object-fit:contain;position:absolute;right:10px;bottom:10px;z-index:2\">' : '<div class=\"tool-icon\">'+(x.icon||'🔧')+'</div>';"
            new_seg = seg.replace(old_line, new_line, 1)
            new_seg = new_seg.replace('background-position:${bgPos};background-color:${bgClr}', 'background-position:${bgPos};background-size:${bgFit};background-color:${bgClr}')
            new_seg = new_seg.replace("<div class=\"tool-icon\">${x.icon||'🔧'}</div></div>`", "${iconPart}</div>`")
            s = s[:idx] + new_seg + s[idx+2500:]
            print('OK store.html 已改')
with open('templates/store.html', 'w', encoding='utf-8') as f:
    f.write(s)
print('=== 全部完成 ===')
