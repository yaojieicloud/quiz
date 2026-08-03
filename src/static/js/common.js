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
  const links = [
    { key: 'home', href: 'home.html', text: '🏠 首页', roles: ['student','parent','admin'] },
    { key: 'records', href: 'records.html', text: '📋 答题记录', roles: ['student'] },
    { key: 'wrong', href: 'wrong.html', text: '❌ 错题本', roles: ['student'] },
    { key: 'stats', href: 'stats.html', text: '📊 学习统计', roles: ['student'] },
    { key: 'parent', href: 'parent.html', text: '👶 孩子情况', roles: ['parent'] },
    { key: 'admin', href: 'admin.html', text: '⚙️ 管理后台', roles: ['admin'] },
  ];
  const navHtml = links
    .filter(l => l.roles.includes(user.role))
    .map(l => `<a href="${l.href}" class="${active === l.key ? 'active' : ''}">${l.text}</a>`)
    .join('');
  const avatarText = (user.nickname || user.username || '?').charAt(0).toUpperCase();
  return `
    <div class="topbar">
      <div class="logo" onclick="location.href='home.html'">🎯 题库闯关</div>
      <div class="nav-links">${navHtml}</div>
      <div class="user-info">
        <div class="avatar">${avatarText}</div>
        <span>${esc(user.nickname)}</span>
        <button class="btn-logout" onclick="logout()">退出</button>
      </div>
    </div>`;
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
    userPairs.forEach(pair => {
      const [left, right] = pair.split(':').map(Number);
      if (options[left] && matchOptions[right]) {
        const isCorrectPair = correctPairs.includes(pair);
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
