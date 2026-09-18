(function(){
'use strict';
var SS='app_stats', SA='app_achievements';
var stats={}, unlocked={};
try{stats=JSON.parse(localStorage.getItem(SS)||'{}');}catch(e){}
try{unlocked=JSON.parse(localStorage.getItem(SA)||'{}');}catch(e){}

function saveLocal(){try{localStorage.setItem(SS,JSON.stringify(stats));localStorage.setItem(SA,JSON.stringify(unlocked));}catch(e){}}
function getUserToken(){return localStorage.getItem('user_token')||'';}
var syncing=false,pending=false;
function syncUp(){
  var t=getUserToken();if(!t)return;
  if(syncing){pending=true;return;}
  syncing=true;
  fetch('/api/user/stats',{method:'POST',headers:{'Content-Type':'application/json','X-User-Token':t},body:JSON.stringify(stats)})
    .finally(function(){syncing=false;if(pending){pending=false;setTimeout(syncUp,500);}});
}
function pullStats(){
  var t=getUserToken();if(!t)return Promise.resolve();
  return fetch('/api/user/stats',{headers:{'X-User-Token':t}})
    .then(function(r){return r.json();})
    .then(function(data){
      if(!data||typeof data!=='object')return;
      // 数值取大
      ['views','favs','shares','searches','streakDays','maxDailyViews','nightStreak'].forEach(function(k){
        stats[k]=Math.max(stats[k]||0,data[k]||0);
      });
      // 数组取并集
      ['visitDays','favCategories'].forEach(function(k){
        var a=stats[k]||[],b=data[k]||[];
        var set={};a.concat(b).forEach(function(x){set[x]=1;});
        stats[k]=Object.keys(set);
      });
      // 布尔取或
      ['early','night','theme','lucky'].forEach(function(k){
        stats[k]=stats[k]||data[k]||false;
      });
      // lastVisitDate
      if(data.lastVisitDate&&(!stats.lastVisitDate||data.lastVisitDate>stats.lastVisitDate))
        stats.lastVisitDate=data.lastVisitDate;
      saveLocal();
      checkAchv();
    }).catch(function(){});
}

// ============ 成就定义（更难！） ============
var ACHV=[
// 浏览
{id:'view_1',icon:'👀',name:'第一步',desc:'浏览 1 个应用',tier:'bronze',check:function(s){return (s.views||0)>=1;}},
{id:'view_10',icon:'🧭',name:'探索者',desc:'浏览 10 个应用',tier:'bronze',check:function(s){return (s.views||0)>=10;}},
{id:'view_30',icon:'🗺️',name:'资深探险家',desc:'浏览 30 个应用',tier:'silver',check:function(s){return (s.views||0)>=30;}},
{id:'view_100',icon:'🚀',name:'星际漫游者',desc:'浏览 100 个应用',tier:'gold',check:function(s){return (s.views||0)>=100;}},
{id:'view_500',icon:'🌌',name:'宇宙探索者',desc:'浏览 500 个应用',tier:'legend',check:function(s){return (s.views||0)>=500;}},
{id:'view_daily_20',icon:'🏃',name:'单日狂魔',desc:'单日浏览 20 个应用',tier:'silver',check:function(s){return (s.maxDailyViews||0)>=20;}},
// 收藏
{id:'fav_1',icon:'❤️',name:'第一次心动',desc:'收藏 1 个应用',tier:'bronze',check:function(s){return (s.favs||0)>=1;}},
{id:'fav_5',icon:'💖',name:'收藏家',desc:'收藏 5 个应用',tier:'bronze',check:function(s){return (s.favs||0)>=5;}},
{id:'fav_15',icon:'💝',name:'收纳大师',desc:'收藏 15 个应用',tier:'silver',check:function(s){return (s.favs||0)>=15;}},
{id:'fav_30',icon:'👑',name:'收藏之王',desc:'收藏 30 个应用',tier:'gold',check:function(s){return (s.favs||0)>=30;}},
{id:'fav_100',icon:'💎',name:'钻石收藏家',desc:'收藏 100 个应用',tier:'legend',check:function(s){return (s.favs||0)>=100;}},
{id:'fav_cat_5',icon:'🎯',name:'分类达人',desc:'收藏来自 5 个不同分类',tier:'silver',check:function(s){return ((s.favCategories||[]).length)>=5;}},
// 分享
{id:'share_1',icon:'📤',name:'分享新手',desc:'分享 1 次',tier:'bronze',check:function(s){return (s.shares||0)>=1;}},
{id:'share_5',icon:'📣',name:'分享达人',desc:'分享 5 次',tier:'silver',check:function(s){return (s.shares||0)>=5;}},
{id:'share_20',icon:'📢',name:'传播大使',desc:'分享 20 次',tier:'gold',check:function(s){return (s.shares||0)>=20;}},
// 登录/访问
{id:'days_7',icon:'📅',name:'常客',desc:'累计访问 7 天',tier:'silver',check:function(s){return ((s.visitDays||[]).length)>=7;}},
{id:'days_30',icon:'📆',name:'月度粉丝',desc:'累计访问 30 天',tier:'gold',check:function(s){return ((s.visitDays||[]).length)>=30;}},
{id:'streak_7',icon:'🔥',name:'七日不倒',desc:'连续访问 7 天',tier:'gold',check:function(s){return (s.streakDays||0)>=7;}},
{id:'streak_30',icon:'💫',name:'月度铁粉',desc:'连续访问 30 天',tier:'legend',check:function(s){return (s.streakDays||0)>=30;}},
// 时间
{id:'early',icon:'🌅',name:'早起鸟',desc:'6-9 点打开商店',tier:'bronze',check:function(s){return !!s.early;}},
{id:'night',icon:'🌙',name:'夜猫子',desc:'0-5 点打开商店',tier:'bronze',check:function(s){return !!s.night;}},
{id:'night_3',icon:'🦉',name:'熬夜王者',desc:'连续 3 天凌晨打开',tier:'gold',check:function(s){return (s.nightStreak||0)>=3;}},
// 搜索
{id:'search_20',icon:'🔍',name:'搜索狂人',desc:'搜索 20 次',tier:'silver',check:function(s){return (s.searches||0)>=20;}},
{id:'search_100',icon:'🧠',name:'搜索之神',desc:'搜索 100 次',tier:'legend',check:function(s){return (s.searches||0)>=100;}},
// 特殊
{id:'theme',icon:'🎨',name:'换装达人',desc:'切换过主题',tier:'bronze',check:function(s){return !!s.theme;}},
{id:'lucky',icon:'🎲',name:'好运星',desc:'用过"手气不错"',tier:'bronze',check:function(s){return !!s.lucky;}},
{id:'all',icon:'🏆',name:'集齐一切',desc:'解锁其他所有成就',tier:'legend',check:function(s){
  return ACHV.filter(function(a){return a.id!=='all';}).every(function(a){return !!unlocked[a.id];});
}}
];

function checkAchv(){
var newly=[];
ACHV.forEach(function(a){if(!unlocked[a.id]&&a.check(stats)){unlocked[a.id]=Date.now();newly.push(a);}});
if(newly.length){
saveLocal();syncUp();
newly.forEach(function(a){setTimeout(function(){if(typeof showToast==='function')showToast('🏆 解锁：'+a.name);},100);});
}
}

function tierColor(t){
var m={bronze:'linear-gradient(135deg,#cd7f32,#8b5a2b)',silver:'linear-gradient(135deg,#b8c6db,#6c7b8b)',gold:'linear-gradient(135deg,#ffd700,#ff9500)',legend:'linear-gradient(135deg,#a855f7,#ec4899)'};
return m[t]||m.bronze;
}

function openAchievements(){
var unCount=ACHV.filter(function(a){return !!unlocked[a.id];}).length;
var total=ACHV.length;
var html='<div style="text-align:center;padding:8px 0 16px"><div style="font-size:32px;font-weight:800;color:var(--text)">'+unCount+' / '+total+'</div><div style="font-size:12px;color:var(--text-sub)">已解锁成就</div></div>';
html+=ACHV.map(function(a){
var on=!!unlocked[a.id];
var prog='';
if(!on){
if(a.id.indexOf('view_')===0){var t=a.id==='view_10'?10:a.id==='view_30'?30:a.id==='view_100'?100:a.id==='view_500'?500:1;prog=(stats.views||0)+' / '+t;}
else if(a.id.indexOf('fav_')===0){var t2=a.id==='fav_5'?5:a.id==='fav_15'?15:a.id==='fav_30'?30:a.id==='fav_100'?100:1;prog=(stats.favs||0)+' / '+t2;}
else if(a.id.indexOf('share_')===0){var t3=a.id==='share_5'?5:a.id==='share_20'?20:1;prog=(stats.shares||0)+' / '+t3;}
else if(a.id.indexOf('streak_')===0){var t4=a.id==='streak_7'?7:30;prog=(stats.streakDays||0)+' / '+t4+' 天';}
else if(a.id.indexOf('days_')===0){var t5=a.id==='days_7'?7:30;prog=((stats.visitDays||[]).length)+' / '+t5+' 天';}
else if(a.id.indexOf('search_')===0){var t6=a.id==='search_20'?20:100;prog=(stats.searches||0)+' / '+t6;}
}
var tierTag=on?'':'<div class="achv-progress">进度 '+prog+'</div>';
return '<div class="achv-item'+(on?' unlocked':'')+'"><div class="achv-icon" style="'+(on?'background:'+tierColor(a.tier):'')+'">'+a.icon+'</div><div class="achv-info"><h4>'+a.name+(on?' ✅':'')+'</h4><p>'+a.desc+'</p>'+tierTag+'</div></div>';
}).join('');
var m=document.getElementById('achv-modal');
if(!m){
m=document.createElement('div');m.id='achv-modal';m.className='modal';
m.onclick=function(e){if(e.target===m)m.classList.remove('show');};
m.innerHTML='<div class="modal-content"><div class="modal-header"><div class="modal-title">我的成就</div><div class="modal-close" onclick="this.closest(\'.modal\').classList.remove(\'show\')">✕</div></div><div id="achv-list"></div></div>';
document.body.appendChild(m);
}
document.getElementById('achv-list').innerHTML=html;
m.classList.add('show');
}

// ============ 断网小游戏 ============
var gameInited=false;
function initGame(){
if(gameInited)return;gameInited=true;
if(document.getElementById('offline-overlay'))return;
var ov=document.createElement('div');
ov.id='offline-overlay';ov.className='offline-overlay';
ov.innerHTML='<h2>网络开小差了</h2><p>来玩个跳跃小游戏吧</p><canvas id="offline-game" width="300" height="180"></canvas><div class="offline-tip">点击屏幕 / 按空格 <b>跳跃</b></div><button class="offline-retry" onclick="location.reload()">重试连接</button>';
document.body.appendChild(ov);
var cv=document.getElementById('offline-game'),ctx=cv.getContext('2d');
var W=cv.width,H=cv.height,GROUND=H-24;
var run=false,loop=null,p={x:40,y:GROUND-16,vy:0,jump:false},obs=[],frame=0,score=0,speed=3;
var best=parseInt(localStorage.getItem('offline_best')||'0',10);
function reset(){p.y=GROUND-16;p.vy=0;p.jump=false;obs=[];frame=0;score=0;speed=3;}
function jump(){if(!p.jump&&run){p.vy=-7;p.jump=true;}}
function update(){
frame++;score=Math.floor(frame/6);
p.vy+=0.45;p.y+=p.vy;
if(p.y>=GROUND-16){p.y=GROUND-16;p.vy=0;p.jump=false;}
if(frame%60===0&&frame>0)speed+=0.12;
if(frame%80===0)obs.push({x:W,w:10+Math.random()*10,h:14+Math.random()*14});
obs.forEach(function(o){o.x-=speed;});
obs=obs.filter(function(o){return o.x+o.w>0;});
for(var i=0;i<obs.length;i++){var o=obs[i];if(o.x<p.x+16&&o.x+o.w>p.x&&GROUND-o.h<p.y+16){return over();}}
}
function draw(){
ctx.fillStyle='#222';ctx.fillRect(0,0,W,H);
ctx.strokeStyle='#444';ctx.beginPath();ctx.moveTo(0,GROUND);ctx.lineTo(W,GROUND);ctx.stroke();
ctx.fillStyle='#f4a261';ctx.fillRect(p.x,p.y,16,16);
ctx.fillStyle='#e63946';obs.forEach(function(o){ctx.fillRect(o.x,GROUND-o.h,o.w,o.h);});
ctx.fillStyle='#fff';ctx.font='bold 12px sans-serif';ctx.fillText('得分 '+score,10,20);
ctx.fillStyle='#666';ctx.fillText('最佳 '+best,W-70,20);
}
function tick(){if(!run)return;update();draw();loop=requestAnimationFrame(tick);}
function start(){reset();run=true;if(loop)cancelAnimationFrame(loop);tick();}
function over(){
run=false;if(loop)cancelAnimationFrame(loop);
if(score>best){best=score;localStorage.setItem('offline_best',String(best));}
ctx.fillStyle='rgba(0,0,0,0.75)';ctx.fillRect(0,0,W,H);
ctx.fillStyle='#fff';ctx.font='bold 16px sans-serif';ctx.textAlign='center';
ctx.fillText('游戏结束',W/2,H/2-10);
ctx.font='12px sans-serif';ctx.fillStyle='#f4a261';
ctx.fillText('得分 '+score+' · 点击重来',W/2,H/2+14);
ctx.textAlign='left';
cv.addEventListener('click',function rst(){cv.removeEventListener('click',rst);start();});
}
cv.addEventListener('click',function(){if(run)jump();});
document.addEventListener('keydown',function(e){if(e.code==='Space'&&ov.classList.contains('show')){e.preventDefault();if(run)jump();}});
window.__gameStart=start;
}
function showGame(){
initGame();
var ov=document.getElementById('offline-overlay');
ov.classList.add('show');
if(window.__gameStart)setTimeout(window.__gameStart,50);
}

// ============ 访问记录 / 连续签到 ============
function recordVisit(){
var today=new Date().toISOString().slice(0,10);
var days=stats.visitDays||[];
if(stats.lastVisitDate===today)return;
var yesterday=new Date(Date.now()-86400000).toISOString().slice(0,10);
if(stats.lastVisitDate===yesterday){stats.streakDays=(stats.streakDays||0)+1;}
else{stats.streakDays=1;}
stats.lastVisitDate=today;
if(days.indexOf(today)===-1)days.push(today);
stats.visitDays=days;
saveLocal();syncUp();
}
function recordHour(){
var hh=new Date().getHours();
var today=new Date().toISOString().slice(0,10);
if(hh>=6&&hh<9){stats.early=true;}
if(hh>=0&&hh<5){stats.night=true;
  // 连续凌晨逻辑
  var y2=new Date(Date.now()-86400000).toISOString().slice(0,10);
  if(stats.lastNightDate===y2){stats.nightStreak=(stats.nightStreak||0)+1;}
  else if(stats.lastNightDate!==today){stats.nightStreak=1;}
  stats.lastNightDate=today;
}
saveLocal();
}

// ============ 单日浏览计数 ============
function bumpDaily(){
var today=new Date().toISOString().slice(0,10);
if(stats.dailyDate!==today){stats.dailyDate=today;stats.dailyViews=0;}
stats.dailyViews=(stats.dailyViews||0)+1;
if(stats.dailyViews>(stats.maxDailyViews||0))stats.maxDailyViews=stats.dailyViews;
}

// ============ 对外接口 ============
window.extras={
bump:function(k,d){
 if(k==='views'){stats.views=(stats.views||0)+(d||1);bumpDaily();}
 else{stats[k]=(stats[k]||0)+(d||1);}
 saveLocal();syncUp();checkAchv();
},
setFavCount:function(n,cat){
 stats.favs=n;
 if(cat){
  var arr=stats.favCategories||[];
  if(arr.indexOf(cat)===-1){arr.push(cat);stats.favCategories=arr;}
 }
 saveLocal();syncUp();checkAchv();
},
setBool:function(k){stats[k]=true;saveLocal();syncUp();checkAchv();},
openAchievements:openAchievements,
showGame:showGame,
openReport:openReport,
showPoster:showPoster,
_makePoster:makePoster,
pull:function(){return pullStats();},
check:checkAchv
};

// ============ 启动 ============
recordVisit();
recordHour();
checkAchv();
syncUp();
setTimeout(function(){pullStats().then(function(){checkAchv();});},800);

// fetch 拦截：/api/apps 失败时弹游戏
var _f=window.fetch;
window.fetch=function(u,o){
var s=typeof u==='string'?u:(u&&u.url)||'';
var p=_f.apply(this,arguments);
if(s.indexOf('/api/apps')===0){
p=p.catch(function(e){showGame();throw e;});
}
return p;
};
function openReport(){
  var totalViews=stats.views||0;
  var totalFavs=stats.favs||0;
  var totalShares=stats.shares||0;
  var totalSearches=stats.searches||0;
  var unCount=ACHV.filter(function(a){return !!unlocked[a.id];}).length;
  var visitDays=stats.visitDays||[];
  var daysCount=visitDays.length;
  var streak=stats.streakDays||0;
  var firstDate='今天';
  if(visitDays.length){var sorted=visitDays.slice().sort();firstDate=sorted[0];}
  var favCats=stats.favCategories||[];
  var themeNames={light:'极简白',dark:'深色',gold:'黑金',red:'黑红',purple:'赛博紫',blue:'渐变蓝'};
  var curTheme=localStorage.getItem('app_theme')||'light';
  var hist=[];try{hist=JSON.parse(localStorage.getItem('app_history')||'[]');}catch(e){}

  var html='<div style="text-align:center;padding:10px 0 16px">';
  html+='<div style="font-size:11px;color:var(--text-sub);letter-spacing:3px;margin-bottom:8px">MY YEAR IN APPS</div>';
  html+='<div style="font-size:22px;font-weight:800;color:var(--text);margin-bottom:6px">你的年度应用报告</div>';
  html+='<div style="font-size:11px;color:var(--text-sub)">'+firstDate+' 开始</div>';
  html+='</div>';

  function row(icon,label,val){
    return '<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--border)"><div style="font-size:22px;width:36px;text-align:center">'+icon+'</div><div style="flex:1"><div style="font-size:12px;color:var(--text-sub)">'+label+'</div><div style="font-size:16px;font-weight:800;color:var(--text);margin-top:2px">'+val+'</div></div></div>';
  }
  html+=row('👀','累计浏览应用',totalViews+' 个');
  html+=row('❤️','收藏的应用',totalFavs+' 个');
  html+=row('📤','分享次数',totalShares+' 次');
  html+=row('🔍','搜索次数',totalSearches+' 次');
  html+=row('📅','使用天数',daysCount+' 天');
  html+=row('🔥','最长连续',streak+' 天');
  html+=row('🏆','解锁成就',unCount+' / '+ACHV.length);
  html+=row('🎨','当前主题',themeNames[curTheme]||'极简白');

  if(favCats.length){
    html+='<div style="margin-top:16px;padding:14px;background:var(--bg);border-radius:14px"><div style="font-size:12px;color:var(--text-sub);margin-bottom:8px">你最爱的分类</div>';
    html+=favCats.slice(0,5).map(function(c){return '<span style="display:inline-block;padding:4px 12px;background:var(--primary);color:var(--primary-text);border-radius:12px;font-size:12px;margin:3px 4px 3px 0">'+c+'</span>';}).join('');
    html+='</div>';
  }
  if(hist.length){
    html+='<div style="margin-top:14px;padding:14px;background:var(--bg);border-radius:14px"><div style="font-size:12px;color:var(--text-sub);margin-bottom:8px">最近浏览</div>';
    html+=hist.slice(0,5).map(function(h){return '<div style="font-size:13px;color:var(--text);padding:4px 0">· '+h.name+'</div>';}).join('');
    html+='</div>';
  }
  html+='<div style="text-align:center;margin-top:20px;font-size:11px;color:var(--text-sub)">继续探索，明年更精彩 ✨</div>';

  var m=document.getElementById('report-modal');
  if(!m){
    m=document.createElement('div');m.id='report-modal';m.className='modal';
    m.onclick=function(e){if(e.target===m)m.classList.remove('show');};
    m.innerHTML='<div class="modal-content"><div class="modal-header"><div class="modal-title">年度报告</div><div class="modal-close" onclick="this.closest(\'.modal\').classList.remove(\'show\')">✕</div></div><div id="report-body"></div></div>';
    document.body.appendChild(m);
  }
  document.getElementById('report-body').innerHTML=html;
  m.classList.add('show');
}

function showPoster(){
  var hist=[];try{hist=JSON.parse(localStorage.getItem('app_history')||'[]');}catch(e){}
  if(!hist.length){ if(typeof showToast==='function')showToast('先去浏览几个应用吧'); return; }
  var list='<div>'+hist.map(function(h,i){return '<div class="hist-item" onclick="extras._makePoster('+i+')"><div class="hist-icon">'+(h.icon_url?'<img src="'+h.icon_url+'">':'📦')+'</div><div class="hist-info"><h4>'+h.name+'</h4><p>点击生成海报</p></div></div>';}).join('')+'</div>';
  var m=document.getElementById('poster-pick-modal');
  if(!m){
    m=document.createElement('div');m.id='poster-pick-modal';m.className='modal';
    m.onclick=function(e){if(e.target===m)m.classList.remove('show');};
    m.innerHTML='<div class="modal-content"><div class="modal-header"><div class="modal-title">选择应用</div><div class="modal-close" onclick="this.closest(\'.modal\').classList.remove(\'show\')">✕</div></div><div id="poster-pick-list"></div></div>';
    document.body.appendChild(m);
  }
  document.getElementById('poster-pick-list').innerHTML=list;
  m.classList.add('show');
  window._posterHist=hist;
}

function makePoster(idx){
  var h=window._posterHist[idx];
  if(!h)return;
  var pick=document.getElementById('poster-pick-modal');
  if(pick)pick.classList.remove('show');

  fetch('/api/apps/'+h.id).then(function(r){return r.json();}).then(function(app){
    var W=600,H=800;
    var cv=document.createElement('canvas');cv.width=W;cv.height=H;
    var ctx=cv.getContext('2d');
    var g=ctx.createLinearGradient(0,0,W,H);
    g.addColorStop(0,'#1a1a1a');g.addColorStop(1,'#333');
    ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    ctx.fillStyle='rgba(244,162,97,0.15)';
    ctx.beginPath();ctx.arc(W,0,300,0,Math.PI*2);ctx.fill();
    ctx.fillStyle='#f4a261';ctx.font='bold 22px sans-serif';ctx.textAlign='left';
    ctx.fillText('APP OF THE DAY',50,80);
    ctx.font='bold 80px sans-serif';
    ctx.fillText('📦',50,220);
    ctx.fillStyle='#fff';ctx.font='bold 48px sans-serif';
    var name=app.name||'应用';
    var maxW=W-100;var lines=[];var line='';
    for(var i=0;i<name.length;i++){
      var test=line+name[i];
      if(ctx.measureText(test).width>maxW){lines.push(line);line=name[i];}
      else line=test;
    }
    lines.push(line);
    lines.slice(0,3).forEach(function(l,i){ctx.fillText(l,50,320+i*60);});
    ctx.fillStyle='#aaa';ctx.font='22px sans-serif';
    var desc=(app.description||'暂无描述').slice(0,80);
    var dLines=[];line='';
    for(var j=0;j<desc.length;j++){
      var t=line+desc[j];
      if(ctx.measureText(t).width>maxW){dLines.push(line);line=desc[j];}
      else line=t;
    }
    dLines.push(line);
    dLines.slice(0,3).forEach(function(l,i){ctx.fillText(l,50,520+i*34);});
    ctx.fillStyle='#666';ctx.font='18px sans-serif';
    ctx.fillText('分类：'+(app.category||'未分类'),50,H-160);
    ctx.fillText('下载量：'+app.downloads,50,H-130);
    ctx.fillStyle='#f4a261';ctx.font='bold 20px sans-serif';
    ctx.fillText('访问：',50,H-80);
    ctx.fillStyle='#fff';ctx.font='16px sans-serif';
    ctx.fillText(location.origin+'/store',50,H-50);

    var preview=document.getElementById('poster-preview-modal');
    if(!preview){
      preview=document.createElement('div');preview.id='poster-preview-modal';preview.className='modal';
      preview.onclick=function(e){if(e.target===preview)preview.classList.remove('show');};
      preview.innerHTML='<div class="modal-content"><div class="modal-header"><div class="modal-title">保存分享</div><div class="modal-close" onclick="this.closest(\'.modal\').classList.remove(\'show\')">✕</div></div><div style="text-align:center"><canvas id="poster-canvas" style="width:100%;max-width:400px;border-radius:12px"></canvas><div style="font-size:12px;color:var(--text-sub);margin-top:12px">长按图片可保存到相册</div></div></div>';
      document.body.appendChild(preview);
    }
    var pc=document.getElementById('poster-canvas');
    pc.width=W;pc.height=H;
    pc.getContext('2d').drawImage(cv,0,0);
    preview.classList.add('show');
  }).catch(function(){if(typeof showToast==='function')showToast('加载失败');});
}

})();
