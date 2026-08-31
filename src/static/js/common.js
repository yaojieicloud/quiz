// ============ 题库闯关系统 - 公共脚本 ============

const API = {
  // 封装 fetch，自动带 token
  async request(url, options = {}) {
    const token = localStorage.getItem('quiz_token');
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401) {
      localStorage.removeItem('quiz_token');
      localStorage.removeItem('quiz_user');
      location.href = 'index.html';
      throw new Error('未登录');
    }
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || '请求失败');
    return data;
  },
  get(url) { return this.request(url); },
  post(url, body) { return this.request(url, { method: 'POST', body: JSON.stringify(body) }); },
  put(url, body) { return this.request(url, { method: 'PUT', body: JSON.stringify(body) }); },
  patch(url, body) { return this.request(url, { method: 'PATCH', body: JSON.stringify(body) }); },
  del(url) { return this.request(url, { method: 'DELETE' }); },
};

function getUser() {
  try { return JSON.parse(localStorage.getItem('quiz_user')); } catch { return null; }
}

function requireAuth() {
  if (!localStorage.getItem('quiz_token')) {
    location.href = 'index.html';
    return null;
  }
  return getUser();
}

function logout() {
  localStorage.removeItem('quiz_token');
  localStorage.removeItem('quiz_user');
  location.href = 'index.html';
}

function toast(msg, type = '') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2500);
}

function fmtTime(iso) {
  if (!iso) return '-';
  const d = new Date(iso);
  const pad = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function fmtDuration(sec) {
  if (!sec) return '-';
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return m > 0 ? `${m}分${s}秒` : `${s}秒`;
}

function scoreRank(score) {
  if (score >= 90) return { emoji: '🏆', text: '太厉害了，小天才！', cls: 'score-high' };
  if (score >= 75) return { emoji: '🎉', text: '不错哦，小达人！', cls: 'score-high' };
  if (score >= 60) return { emoji: '💪', text: '及格啦，继续加油！', cls: 'score-mid' };
  return { emoji: '🌱', text: '别灰心，多练几次就棒了！', cls: 'score-low' };
}

// 渲染顶部导航栏（各页面复用）
function renderTopbar(active = '') {
  const user = getUser();
  if (!user) { location.href = 'index.html'; return; }
  // embed 模式：被 admin.html 的 iframe 内嵌时，不渲染独立导航（避免双重顶栏），
  // 由父页面 tab-bar 提供导航。直接访问独立页（非 iframe、无 embed 参数）仍正常渲染。
  const embed = new URLSearchParams(location.search).get('embed') === '1' || window.self !== window.top;
  if (embed) return '';
  const links = [
    { key: 'home', href: 'home.html', text: '🏠 首页', roles: ['student','parent','admin'] },
    { key: 'lottery', href: 'lottery.html', text: '🎡 大转盘', roles: ['student','admin'] },
    { key: 'redeem', href: 'redeem.html', text: '🎁 兑换商城', roles: ['student','admin'] },
    { key: 'records', href: 'records.html', text: '📋 答题记录', roles: ['student'] },
    { key: 'wrong', href: 'wrong.html', text: '❌ 错题本', roles: ['student'] },
    { key: 'stats', href: 'stats.html', text: '🕒 最新动态', roles: ['student'] },
    { key: 'mastery', href: 'mastery.html', text: '🎯 精通度', roles: ['student', 'parent'] },
    { key: 'parent', href: 'parent.html', text: '👶 孩子情况', roles: ['parent'] },
    { key: 'admin', href: 'admin.html', text: '⚙️ 管理后台', roles: ['admin'] },
  ];
  const navHtml = links
    .filter(l => l.roles.includes(user.role))
    .map(l => `<a href="${l.href}" class="${active === l.key ? 'active' : ''}">${l.text}</a>`)
    .join('');
  const avatarText = (user.nickname || user.username || '?').charAt(0).toUpperCase();
  // 学员/管理员均显示积分徽章（点击跳转大转盘）
  const pointsChip = (user.role === 'student' || user.role === 'admin')
    ? `<span class="points-chip" id="pointsChip" onclick="location.href='lottery.html'" title="我的积分">⭐ <span id="pointsVal">…</span></span>`
    : '';
  return `
    <div class="topbar">
      <div class="logo" onclick="location.href='home.html'">🎯 题库闯关</div>
      <div class="nav-links">${navHtml}</div>
      <div class="user-info">
        ${pointsChip}
        <div class="avatar">${avatarText}</div>
        <span>${esc(user.nickname)}</span>
        <button class="btn-logout" onclick="logout()">退出</button>
      </div>
    </div>`;
}

// 拉取并渲染学员积分徽章（每个学员端页面渲染顶栏后调用）
async function initPoints() {
  const user = getUser();
  if (!user || (user.role !== 'student' && user.role !== 'admin')) return;
  const val = document.getElementById('pointsVal');
  if (!val) return;
  try {
    const d = await API.get('/api/points/balance');
    val.textContent = d.balance;
  } catch (e) {
    val.textContent = '—';
  }
}

// 上线弹窗：版本更新后首次进入弹出（可爱 / 醒目 / 小动画）
async function maybeShowLaunchPopup() {
  const user = getUser();
  if (!user || user.role !== 'student') return;
  const KEY = 'quiz_launch_v';
  let latest = 'v1';
  try {
    const meta = await API.get('/api/meta');
    latest = meta.launch_popup_version || 'v1';
  } catch (e) { /* 取不到则用默认版本 */ }
  const seen = localStorage.getItem(KEY);
  if (seen === latest) return;       // 已看过此版本，不再弹
  showLaunchPopup();
  localStorage.setItem(KEY, latest); // 标记已看，避免重复弹
}

function showLaunchPopup() {
  if (document.getElementById('launchPopup')) return;
  const style = `
    <style id="launchPopupStyle">
      @keyframes lp-bounce { 0%{transform:scale(.6);opacity:0} 60%{transform:scale(1.08)} 100%{transform:scale(1);opacity:1} }
      @keyframes lp-star { 0%,100%{transform:rotate(-12deg) scale(1)} 50%{transform:rotate(12deg) scale(1.15)} }
      @keyframes lp-float { 0%{transform:translateY(0) rotate(0)} 100%{transform:translateY(-40px) rotate(360deg);opacity:0} }
      @keyframes lp-glow { 0%,100%{text-shadow:0 0 12px #ffd43b} 50%{text-shadow:0 0 26px #ff922b} }
      #launchPopup { position:fixed; inset:0; z-index:999; display:flex; align-items:center; justify-content:center;
        background:rgba(60,40,90,0.45); backdrop-filter:blur(3px); }
      #launchPopup .lp-card { position:relative; width:min(86vw,420px); padding:30px 26px 24px; border-radius:28px; text-align:center;
        background:linear-gradient(160deg,#fff0f6 0%,#fff9db 55%,#e7f5ff 100%);
        box-shadow:0 24px 60px rgba(120,80,160,0.35); animation:lp-bounce .5s cubic-bezier(.2,1.2,.4,1) both; }
      #launchPopup .lp-title { font-size:26px; font-weight:bold; margin:8px 0 4px; color:#e8590c;
        background:linear-gradient(90deg,#f06595,#fab005,#4dabf7); -webkit-background-clip:text; background-clip:text;
        -webkit-text-fill-color:transparent; animation:lp-glow 1.8s ease-in-out infinite; }
      #launchPopup .lp-sub { font-size:15px; color:#7a6c8c; line-height:1.7; margin:6px 4px 16px; }
      #launchPopup .lp-emojis { font-size:40px; letter-spacing:6px; }
      #launchPopup .lp-emojis span { display:inline-block; animation:lp-star 1.6s ease-in-out infinite; }
      #launchPopup .lp-emojis span:nth-child(2){ animation-delay:.3s } #launchPopup .lp-emojis span:nth-child(3){ animation-delay:.6s }
      #launchPopup .lp-btns { display:flex; gap:12px; justify-content:center; margin-top:6px; }
      #launchPopup .lp-confetti { position:absolute; top:-10px; font-size:18px; animation:lp-float 2.4s linear infinite; }
    </style>`;
  const confetti = ['🎉','⭐','🎊','💫','🌟','🍬'].map((e,i)=>
    `<span class="lp-confetti" style="left:${10+i*15}%;animation-delay:${i*0.3}s">${e}</span>`).join('');
  const html = `
    <div id="launchPopup">
      ${style}
      <div class="lp-card">
        ${confetti}
        <div class="lp-emojis"><span>🎉</span><span>🏆</span><span>⭐</span></div>
        <div class="lp-title">积分奖励系统上线啦！</div>
        <div class="lp-sub">做完题就能赚积分～<br>攒够积分来转大转盘🎡<br>换小礼物🎁和零花钱💰哦！</div>
        <div class="lp-btns">
          <button class="btn btn-yellow" onclick="document.getElementById('launchPopup').remove()">去赚积分 🚀</button>
          <button class="btn btn-green" onclick="location.href='lottery.html'">看看大转盘 🎡</button>
        </div>
      </div>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', html);
}

// HTML 转义（用于显示用户输入内容时防注入）
function esc(s) {
  if (s == null) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// 换行符转 <br>（题目内容含 \n 时用于正确显示）
function nl2br(s) {
  return String(s || '').replace(/\n/g, '<br>');
}

// 题型标签
function typeTag(type) {
  const map = { choice: ['tag tag-choice','🔵 选择题'], judge: ['tag tag-judge','🟢 判断题'], calc: ['tag tag-calc','🟠 计算题'], code: ['tag tag-code','💻 编程题'], fill: ['tag tag-calc','✏️ 填空题'], essay: ['tag tag-calc','📝 应用题'], match: ['tag tag-blue','🔗 连线题'], sort: ['tag tag-blue','📋 排序题'], reading: ['tag tag-blue','📖 阅读理解'] };
  return map[type] || ['tag tag-gray', type];
}

// 显示答案文本（选择/判断题把索引转成选项文字）
function answerText(question, answer) {
  if (answer == null || answer === '') return '（未作答）';
  if (question && question.options && (question.type === 'choice' || question.type === 'judge')) {
    if (question.is_multiple) {
      const indices = answer.split(',').map(s => parseInt(s.trim()));
      return indices.map(idx => question.options[idx] || idx).join('、');
    }
    const idx = parseInt(answer);
    return question.options[idx] || answer;
  }
  if (question && question.type === 'fill' && (question.blank_count || 1) > 1) {
    return answer.split('|').map((a, i) => `空${i+1}: ${a}`).join('；');
  }
  if (question && question.type === 'reading' && question.reading_items) {
    // 索引串 "1,0,2" → 逐子题显示所选选项文字
    return answer.split(',').map((idx, i) => {
      const it = question.reading_items[i];
      const opt = it && it.options ? it.options[parseInt(idx)] : null;
      return `题${i+1}:${opt != null ? opt : idx}`;
    }).join('；');
  }
  return answer;
}

// 渲染答题记录中单题详情（学员端 / 管理员端共用同一份渲染逻辑）
// opts.showRefCode: bool —— 是否显示编程题参考代码（学员端默认 false，管理员端 true）
// opts.skipQuestion: bool —— 跳过题干渲染（调用方已在外层卡片里渲染了题干，避免重复）
function renderAnswerCard(q, ar, opts) {
  opts = opts || {};
  const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
  // 对错判断：优先用 is_correct 字段（准确），降级用 llm_score>=60（兼容老数据/NULL）
  const isRight = (ar.is_correct === true) || (ar.is_correct === null && ar.llm_score != null && ar.llm_score >= 60);
  let html = '';
  if (!opts.skipQuestion) {
    html += `<div class="explain-q">${nl2br(esc(q.content || ''))}</div>`;
  }

  if (q.type === 'choice' || q.type === 'judge') {
    const optList = q.options || (q.type === 'judge' ? ['对', '错'] : []);
    const userIdx = (ar.user_answer != null && ar.user_answer !== '') ? String(ar.user_answer) : null;
    const correctIdx = String(q.answer);
    html += `<div class="opts-list">` + optList.map((opt, oi) => {
      const isCorrect = correctIdx === String(oi);
      const isUser = userIdx !== null && userIdx === String(oi);
      let cls = 'opt-row';
      let tag = '';
      if (isCorrect) {
        cls += ' opt-correct';
        tag = '<span class="opt-tag opt-tag-correct">✓ 正确答案</span>';
      }
      if (isUser) {
        cls += isRight ? ' opt-user-correct' : ' opt-user-wrong';
        tag += ` <span class="opt-tag opt-tag-user">${isRight ? '✓ 你的选择' : '✗ 你的选择'}</span>`;
      }
      const letter = q.type === 'judge'
        ? (oi === 0 ? '✓ 对' : '✗ 错')
        : (letters[oi] || (oi + 1));
      return `<div class="${cls}"><span class="opt-letter">${letter}</span><span class="opt-text">${esc(opt)}</span>${tag}</div>`;
    }).join('') + `</div>`;

    // 摘要：你的答案 / 正确答案（即使选项列表很长也方便一眼看到）
    const yourAns = answerText(q, ar.user_answer);
    const correctAns = answerText(q, q.answer);
    html += `<div style="margin:8px 0 6px;font-size:14px;display:flex;gap:14px;flex-wrap:wrap;">
      <span><span class="ans-label ${isRight ? 'label-correct' : 'label-your'}">${isRight ? '✓ 你的答案' : '✗ 你的答案'}</span><b style="margin-left:6px;">${esc(yourAns)}</b></span>
      <span><span class="ans-label label-correct">✓ 正确答案</span><b style="margin-left:6px;">${esc(correctAns)}</b></span>
    </div>`;
    if (q.explanation) html += `<div class="explain-text">💡 ${nl2br(esc(q.explanation))}</div>`;
  } else if (q.type === 'calc') {
    html += `<div style="margin:10px 0;font-size:14px;">
      <span class="ans-label ${isRight ? 'label-correct' : 'label-your'}">${isRight ? '✓ 你的答案' : '✗ 你的答案'}</span> <b>${esc(ar.user_answer || '（未填）')}</b>
      &nbsp;&nbsp;<span class="ans-label label-correct">✓ 正确答案</span> <b>${esc(q.answer)}</b>
    </div>`;
    if (q.explanation) html += `<div class="explain-text">💡 ${nl2br(esc(q.explanation))}</div>`;
  } else if (q.type === 'code') {
    // 编程题：必须显示学员提交的代码，方便复盘/评判
    // 老师点评：优先用 llm_feedback 字段；为空时从 run_output 提取"老师点评"段落（兼容降级拼接的旧 run_output）
    const feedback = (ar.llm_feedback && String(ar.llm_feedback).trim())
      || _extractFeedbackFromRunOutput(ar.run_output);
    if (feedback) {
      html += `<div class="ans-label ans-label-feedback">🌟 老师点评</div>`;
      html += `<div class="teacher-feedback">${esc(feedback)}</div>`;
    }
    html += `<div class="ans-label ans-label-code">🧒 学员提交的代码</div>`;
    html += `<pre class="code-pre">${esc(ar.user_answer || '（未提交代码）')}</pre>`;
    if (ar.run_output) {
      // 若 feedback 缺失，run_output 中可能含 "★ X分 + 老师点评 + 运行结果" 拼接内容，仍全量展示
      const cleanRun = feedback ? _stripFeedbackFromRunOutput(ar.run_output) : ar.run_output;
      html += `<div class="ans-label ans-label-run">🖥 后台运行结果</div>`;
      html += `<pre class="code-pre code-pre-run">${esc(cleanRun || '（无运行结果）')}</pre>`;
    }
    if (opts.showRefCode && q.answer) {
      html += `<div class="ans-label ans-label-ref">📗 参考代码</div>`;
      html += `<pre class="code-pre">${esc(q.answer)}</pre>`;
    }
    if (q.explanation) html += `<div class="explain-text">💡 指导思路：${nl2br(esc(q.explanation))}</div>`;
  } else if (q.type === 'match') {
    // 连线题：显示左右项目和匹配关系
    const options = q.options || [];
    const matchOptions = q.match_options || [];
    const userPairs = (ar.user_answer || '').split(',').filter(s => s.includes(':'));
    const correctPairs = (q.answer || '').split(',').filter(s => s.includes(':'));
    
    html += `<div class="match-display" style="margin:10px 0;">`;
    html += `<div style="display:flex;gap:20px;justify-content:center;">`;
    html += `<div class="match-left">`;
    options.forEach((opt, i) => {
      html += `<div class="match-item" style="padding:8px 16px;background:#e7f5ff;border-radius:8px;margin:4px 0;">${esc(opt)}</div>`;
    });
    html += `</div>`;
    html += `<div class="match-right">`;
    matchOptions.forEach((opt, i) => {
      html += `<div class="match-item" style="padding:8px 16px;background:#fff3bf;border-radius:8px;margin:4px 0;">${esc(opt)}</div>`;
    });
    html += `</div>`;
    html += `</div>`;
    
    // 显示用户的匹配
    html += `<div style="margin-top:10px;font-size:14px;">`;
    html += `<span class="ans-label ${isRight ? 'label-correct' : 'label-your'}">${isRight ? '✓ 你的连线' : '✗ 你的连线'}</span><br>`;
    // 构造正确答案的 (左索引, 右项文本) 集合，消除右侧重复标签歧义，与后端判分一致
    const correctSet = new Set();
    correctPairs.forEach(p => {
      const [l, r] = p.split(':');
      const ri = Number(r);
      correctSet.add(matchOptions.length && matchOptions[ri] !== undefined ? (l + ':' + matchOptions[ri]) : p);
    });

    userPairs.forEach(pair => {
      const [left, right] = pair.split(':').map(Number);
      if (options[left] !== undefined && matchOptions[right] !== undefined) {
        const key = matchOptions.length ? (left + ':' + matchOptions[right]) : pair;
        const isCorrectPair = correctSet.has(key);
        const color = isCorrectPair ? '#2b8a3e' : '#c92a2a';
        html += `<span style="color:${color};">${esc(options[left])} → ${esc(matchOptions[right])} ${isCorrectPair ? '✓' : '✗'}</span><br>`;
      }
    });
    if (!isRight) {
      html += `<span class="ans-label label-correct">✓ 正确答案</span><br>`;
      correctPairs.forEach(pair => {
        const [left, right] = pair.split(':').map(Number);
        if (options[left] && matchOptions[right]) {
          html += `<span style="color:#2b8a3e;">${esc(options[left])} → ${esc(matchOptions[right])}</span><br>`;
        }
      });
    }
    html += `</div></div>`;
    if (q.explanation) html += `<div class="explain-text">💡 ${nl2br(esc(q.explanation))}</div>`;
  } else if (q.type === 'sort') {
    // 排序题：显示项目和顺序
    const options = q.options || [];
    const userOrder = (ar.user_answer || '').split(',').filter(s => s !== '').map(Number);
    const correctOrder = (q.answer || '').split(',').filter(s => s !== '').map(Number);
    
    html += `<div class="sort-display" style="margin:10px 0;">`;
    
    // 显示原始项目
    html += `<div style="margin-bottom:10px;font-size:14px;color:#7a6c8c;">原始项目：</div>`;
    html += `<div style="display:flex;flex-direction:column;gap:4px;">`;
    options.forEach((opt, i) => {
      html += `<div style="padding:8px 16px;background:#f8f9fa;border-radius:8px;">${esc(opt)}</div>`;
    });
    html += `</div>`;
    
    // 显示用户的排序
    html += `<div style="margin-top:10px;font-size:14px;">`;
    html += `<span class="ans-label ${isRight ? 'label-correct' : 'label-your'}">${isRight ? '✓ 你的排序' : '✗ 你的排序'}</span><br>`;
    html += `<div style="display:flex;flex-direction:column;gap:4px;margin-top:4px;">`;
    userOrder.forEach((idx, pos) => {
      if (options[idx]) {
        const isCorrectPos = correctOrder[pos] === idx;
        const color = isCorrectPos ? '#2b8a3e' : '#c92a2a';
        html += `<div style="padding:8px 16px;background:${isCorrectPos ? '#d3f9d8' : '#ffe3e3'};border-radius:8px;color:${color};">${pos + 1}. ${esc(options[idx])} ${isCorrectPos ? '✓' : '✗'}</div>`;
      }
    });
    html += `</div>`;
    
    if (!isRight) {
      html += `<div style="margin-top:10px;"><span class="ans-label label-correct">✓ 正确答案</span></div>`;
      html += `<div style="display:flex;flex-direction:column;gap:4px;margin-top:4px;">`;
      correctOrder.forEach((idx, pos) => {
        if (options[idx]) {
          html += `<div style="padding:8px 16px;background:#d3f9d8;border-radius:8px;color:#2b8a3e;">${pos + 1}. ${esc(options[idx])}</div>`;
        }
      });
      html += `</div>`;
    }
    html += `</div></div>`;
    if (q.explanation) html += `<div class="explain-text">💡 ${nl2br(esc(q.explanation))}</div>`;
  } else if (q.type === 'reading') {
    // 阅读理解：逐子题显示作答对错与正确答案
    const items = q.reading_items || [];
    const userAns = (ar.user_answer || '').split(',');
    const correctAns = (q.answer || '').split(',');
    html += `<div style="margin:10px 0;">`;
    items.forEach((it, i) => {
      const uIdx = userAns[i] != null && userAns[i] !== '' ? parseInt(userAns[i]) : -1;
      const cIdx = correctAns[i] != null ? parseInt(correctAns[i]) : -1;
      const ok = uIdx === cIdx;
      html += `<div style="margin:10px 0;padding:10px 12px;border-radius:10px;background:${ok ? '#f4fce3' : '#fff5f5'};border:1px solid ${ok ? '#c0eb75' : '#ffc9c9'};">`;
      html += `<div style="font-size:14px;font-weight:bold;margin-bottom:6px;">${ok ? '✅' : '❌'} 第${i+1}小题：${esc(it.q || '')}</div>`;
      html += `<div class="opts-list">` + (it.options || []).map((opt, oi) => {
        const isCorrect = oi === cIdx;
        const isUser = oi === uIdx;
        let cls = 'opt-row';
        let tag = '';
        if (isCorrect) { cls += ' opt-correct'; tag = '<span class="opt-tag opt-tag-correct">✓ 正确答案</span>'; }
        if (isUser) { cls += ok ? ' opt-user-correct' : ' opt-user-wrong'; tag += ` <span class="opt-tag opt-tag-user">${ok ? '✓' : '✗'} 你的选择</span>`; }
        return `<div class="${cls}"><span class="opt-letter">${letters[oi] || (oi+1)}</span><span class="opt-text">${esc(opt)}</span>${tag}</div>`;
      }).join('') + `</div>`;
      if (it.explanation) html += `<div class="explain-text" style="margin-top:6px;">💡 ${nl2br(esc(it.explanation))}</div>`;
      html += `</div>`;
    });
    html += `</div>`;
  }
  return html;
}

// 从历史 run_output 字符串里抠出"【老师点评】"段落（兼容以前拼接的格式）
function _extractFeedbackFromRunOutput(runOutput) {
  if (!runOutput) return '';
  const m = String(runOutput).match(/【老师点评】\s*([\s\S]*?)(?:\n\n【运行结果】|$)/);
  if (m) return m[1].trim();
  return '';
}

// 从历史 run_output 里把"★ X分 + 老师点评 + 运行结果"那一段抹掉，仅保留"运行结果"部分
function _stripFeedbackFromRunOutput(runOutput) {
  if (!runOutput) return '';
  let s = String(runOutput);
  // 去掉最顶部的星级行 "★★★★☆  80分"
  s = s.replace(/^[★☆\s]+(?:\d+分)?\s*\n+/, '');
  // 去掉中间的 "【老师点评】...【运行结果】" 整段，只留尾部运行结果
  s = s.replace(/【老师点评】[\s\S]*?(?=\n\n【运行结果】)/, '');
  // 如果上面没匹配到（老数据格式不严格），尝试兜底
  if (s.includes('【运行结果】')) {
    s = s.split('【运行结果】').pop();
  }
  return s.trim();
}

// ================= 精通奖励惊喜弹窗（烟花特效） =================
// showMasteryRewardPopup(nickname, rewards)
//   rewards: [{subject_name, topic_name, tier, points, mode}]  mode: new=新达成 / retroactive=补发
// 烟花：canvas 全屏粒子，无外部依赖，自动随弹窗关闭销毁。
function showMasteryRewardPopup(nickname, rewards) {
  if (!rewards || !rewards.length) return;
  const total = rewards.reduce((s, r) => s + (r.points || 0), 0);
  const tierName = { 1: '初级', 2: '进阶', 3: '挑战' };

  const mask = document.createElement('div');
  mask.className = 'mrp-mask';
  mask.innerHTML = `
    <canvas class="mrp-fireworks"></canvas>
    <div class="mrp-card">
      <div class="mrp-emoji">🎉</div>
      <div class="mrp-title">恭喜 <b>${esc(nickname || '学员')}</b>！</div>
      <div class="mrp-sub">课程达成精通，奖励「玩转大转盘」积分！</div>
      <div class="mrp-list">
        ${rewards.map(r => `
          <div class="mrp-item">
            <span class="mrp-item-tag">${r.mode === 'retroactive' ? '补发' : '精通'}</span>
            <span class="mrp-item-name">${esc(r.subject_name)} · ${esc(r.topic_name)}${r.tier > 1 ? '（' + (tierName[r.tier] || '') + '）' : ''}</span>
            <span class="mrp-item-pts">+${r.points}积分</span>
          </div>`).join('')}
      </div>
      <div class="mrp-total">本次共获得 <b>${total}</b> 积分</div>
      <button class="mrp-btn" onclick="this.closest('.mrp-mask').remove()">太棒啦！收下了 🎁</button>
    </div>
    <style>
      .mrp-mask{position:fixed;inset:0;background:rgba(20,10,40,.82);z-index:99999;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(3px)}
      .mrp-fireworks{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
      .mrp-card{position:relative;background:linear-gradient(160deg,#fffdf5,#fff3d6);border-radius:24px;padding:26px 30px 22px;max-width:420px;width:calc(100% - 48px);box-shadow:0 20px 60px rgba(0,0,0,.45),0 0 0 4px rgba(255,200,80,.35);text-align:center;animation:mrpPop .5s cubic-bezier(.2,1.6,.4,1)}
      @keyframes mrpPop{0%{transform:scale(.5);opacity:0}100%{transform:scale(1);opacity:1}}
      .mrp-emoji{font-size:52px;line-height:1;animation:mrpBounce 1.2s ease infinite}
      @keyframes mrpBounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
      .mrp-title{font-size:22px;font-weight:800;color:#8a5a00;margin-top:8px}
      .mrp-title b{color:#e8590c}
      .mrp-sub{font-size:13px;color:#a87f2e;margin-top:4px}
      .mrp-list{margin:14px 0 4px;display:flex;flex-direction:column;gap:8px;max-height:200px;overflow-y:auto}
      .mrp-item{display:flex;align-items:center;gap:8px;background:#fff;border:1px solid #ffe29a;border-radius:12px;padding:9px 12px;font-size:13px}
      .mrp-item-tag{flex-shrink:0;font-size:11px;font-weight:700;color:#fff;background:#ffa94d;border-radius:8px;padding:2px 8px}
      .mrp-item-name{flex:1;text-align:left;color:#5c4a1e;font-weight:600}
      .mrp-item-pts{color:#e8590c;font-weight:800}
      .mrp-total{font-size:15px;color:#8a5a00;margin:12px 0}
      .mrp-total b{font-size:22px;color:#e8590c}
      .mrp-btn{border:none;background:linear-gradient(135deg,#ffa94d,#ff922b);color:#fff;font-size:16px;font-weight:700;padding:12px 34px;border-radius:24px;cursor:pointer;box-shadow:0 6px 16px rgba(255,146,43,.5);font-family:inherit}
      .mrp-btn:hover{filter:brightness(1.06)}
    </style>`;
  document.body.appendChild(mask);

  // 补发条目换蓝色标签
  mask.querySelectorAll('.mrp-item').forEach((el, i) => {
    if (rewards[i] && rewards[i].mode === 'retroactive') el.querySelector('.mrp-item-tag').style.background = '#74c0fc';
  });

  // ---- 烟花粒子 ----
  const canvas = mask.querySelector('.mrp-fireworks');
  const ctx = canvas.getContext('2d');
  let W, H, raf, particles = [], running = true;
  const COLORS = ['#ffd43b', '#ff922b', '#ff6b6b', '#74c0fc', '#69db7c', '#f783ac', '#ffffff'];
  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  resize(); window.addEventListener('resize', resize);
  function burst(x, y) {
    const n = 36 + Math.floor(Math.random() * 30);
    const hue = COLORS[Math.floor(Math.random() * COLORS.length)];
    for (let i = 0; i < n; i++) {
      const ang = (Math.PI * 2 * i) / n + Math.random() * 0.2;
      const sp = 2 + Math.random() * 4.5;
      particles.push({ x, y, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp, life: 1, decay: 0.012 + Math.random() * 0.012, color: Math.random() < 0.7 ? hue : COLORS[Math.floor(Math.random() * COLORS.length)], size: 1.5 + Math.random() * 2 });
    }
  }
  function loop() {
    if (!running) return;
    ctx.clearRect(0, 0, W, H);
    particles = particles.filter(p => p.life > 0);
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy; p.vy += 0.045; p.vx *= 0.985; p.life -= p.decay;
      ctx.globalAlpha = Math.max(p.life, 0);
      ctx.fillStyle = p.color;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
    raf = requestAnimationFrame(loop);
  }
  // 开场连续烟花
  let count = 0;
  const opener = setInterval(() => {
    burst(W * (0.2 + Math.random() * 0.6), H * (0.15 + Math.random() * 0.35));
    if (++count >= 6) clearInterval(opener);
  }, 380);
  // 之后随机补烟花
  const ambient = setInterval(() => {
    if (Math.random() < 0.7) burst(W * Math.random(), H * (0.1 + Math.random() * 0.4));
  }, 1200);
  loop();
  // 关闭时清理
  new MutationObserver((_, obs) => {
    if (!document.body.contains(mask)) {
      running = false; cancelAnimationFrame(raf);
      clearInterval(opener); clearInterval(ambient);
      window.removeEventListener('resize', resize);
      obs.disconnect();
    }
  }).observe(document.body, { childList: true });
}
