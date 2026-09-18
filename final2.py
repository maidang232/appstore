with open('static/slime.css', 'r', encoding='utf-8') as f:
    c = f.read()
if '.tool-card' not in c or 'background-size' not in c.split('.tool-card')[1][:200]:
    c += '''

/* 卡片背景完整显示 */
.tool-card, .notice-card, .swiper-item, .app-icon img {
  background-size: contain !important;
  background-repeat: no-repeat !important;
  background-position: center !important;
}
'''
    with open('static/slime.css', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK CSS 已加规则')
else:
    print('SKIP 已存在')
