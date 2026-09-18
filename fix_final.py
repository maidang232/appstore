import re
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    h = f.read()
log = []

if 'icon-upload-group' not in h:
    p = h.find('卡片图标')
    if p > 0:
        ls = h.rfind('<label', 0, p)
        em = 'onclick="clearIcon()">清除图标</button>'
        en = h.find(em, p)
        if ls > 0 and en > 0:
            en += len(em)
            seg = h[ls:en]
            h = h[:ls] + '<div id="icon-upload-group" style="display:none">' + seg + '</div>' + h[en:]
            log.append('OK 包裹图标区')

old_open = "if (type === 'tool') document.getElementById('group-icon').style.display = 'block';"
if old_open in h and "icon-upload-group').style.display" not in h:
    new_open = old_open + "\n  var iug = document.getElementById('icon-upload-group');\n  if(iug) iug.style.display = (type === 'tool') ? 'block' : 'none';"
    h = h.replace(old_open, new_open, 1)
    log.append('OK 弹窗控制图标显示')

if 'edit-bg-fit' not in h:
    a = 'onclick="clearCardBg()">清除背景图</button>'
    if a in h:
        ins = a + '''
<label style="display:block;margin-top:12px;font-size:13px;font-weight:600;color:#333">背景显示方式</label>
<select id="edit-bg-fit" style="width:100%;padding:10px;border-radius:8px;border:1.5px solid #e8eaf0;background:#fafbfd;font-size:13px">
  <option value="contain">完整显示</option>
  <option value="cover">铺满</option>
  <option value="100% 100%">拉伸</option>
</select>'''
        h = h.replace(a, ins, 1)
        log.append('OK 加背景显示下拉')

if "bg_fit: document.getElementById('edit-bg-fit')" not in h:
    a = "icon_url: document.getElementById('edit-icon-url').value"
    if a in h:
        h = h.replace(a, a + ",\n    bg_fit: document.getElementById('edit-bg-fit').value", 1)
        log.append('OK saveItem 加 bg_fit')

if "bg_fit: item.bg_fit" not in h:
    a = "color: item.color || '#f0f0f0' }"
    if a in h:
        h = h.replace(a, "color: item.color || '#f0f0f0', bg_fit: item.bg_fit || 'contain' }", 1)
        log.append('OK saveAll 加 bg_fit')

if "edit-bg-fit').value = 'contain'" not in h:
    a = "document.getElementById('edit-image-url').value = '';"
    if a in h:
        h = h.replace(a, a + "\n  var bf = document.getElementById('edit-bg-fit'); if(bf) bf.value = 'contain';", 1)
        log.append('OK openModal 回填 bg_fit')

if 'ae-icon-file' not in h:
    a = '<input id="ae-icon" placeholder="图标 URL">'
    if a in h:
        ins = a + '''
<input type="file" id="ae-icon-file" accept="image/*" style="display:none" onchange="uploadAppIcon()">
<button type="button" class="btn-add" onclick="document.getElementById('ae-icon-file').click()">📷 上传图标图</button>
<div id="ae-icon-preview" style="width:60px;height:60px;background-size:contain;background-repeat:no-repeat;background-position:center;border-radius:8px;margin-top:8px;background-color:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#999;font-size:10px">未设置</div>'''
        h = h.replace(a, ins, 1)
        log.append('OK 应用弹窗加图标上传')

if 'async function uploadAppIcon' not in h:
    fn = '''
async function uploadAppIcon(){
  var fi=document.getElementById('ae-icon-file');
  var f=fi.files[0];
  if(!f)return;
  var fd=new FormData();
  fd.append('file',f);
  var res=await fetch('/api/upload',{method:'POST',headers:{'X-Admin-Token':'admin123'},body:fd});
  var data=await res.json();
  if(data.url){
    document.getElementById('ae-icon').value=data.url;
    var pv=document.getElementById('ae-icon-preview');
    pv.style.backgroundImage='url('+data.url+')';
    pv.innerHTML='';
  }
}
'''
    h = h.replace('function openModal(', fn + 'function openModal(', 1)
    log.append('OK 加 uploadAppIcon 函数')

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(h)

with open('templates/store.html', 'r', encoding='utf-8') as f:
    s = f.read()

if "x.icon_url ? '<img" not in s:
    a = "const bgImg = x.bg || x.image || '';"
    if a in s:
        na = a + "\n    const iconPart = x.icon_url ? '<img src=\"'+x.icon_url+'\" style=\"width:40px;height:40px;object-fit:contain;position:absolute;right:10px;bottom:10px;z-index:2\">' : '<div class=\"tool-icon\">'+(x.icon||'🔧')+'</div>';"
        s = s.replace(a, na, 1)
    s = s.replace('<div class="tool-icon">${x.icon||\'🔧\'}</div></div>`', '${iconPart}</div>`')
    log.append('OK 工具卡片显示图标')

s = s.replace('background-size:cover;background-position:center;background-attachment:fixed',
              'background-size:contain;background-repeat:no-repeat;background-position:center;background-attachment:fixed')
log.append('OK 背景图改成完整显示')

with open('templates/store.html', 'w', encoding='utf-8') as f:
    f.write(s)

print('\n'.join(log))
print('=== 完成 ===')
