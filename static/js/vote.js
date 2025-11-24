// vote.js


// Build a lightweight fingerprint from device info (not perfect but combined with server-side HMAC)
function makeFingerprint(){
const parts = [
navigator.userAgent || '',
navigator.language || '',
screen.width + 'x' + screen.height,
(new Date()).getTimezoneOffset(),
];
return parts.join('||');
}


// store a local marker to prevent double-click
function markLocalVoted(presenterId){
const key = 'qrvote_voted_' + presenterId;
localStorage.setItem(key, new Date().toISOString());
}
function hasLocalVoted(presenterId){
const key = 'qrvote_voted_' + presenterId;
return !!localStorage.getItem(key);
}


async function postVote(presenterId){
const fp = makeFingerprint();
const res = await fetch('/api/vote', {
method: 'POST',
headers: {'Content-Type':'application/json'},
body: JSON.stringify({presenter_id: presenterId, fingerprint: fp, token: PAGE_TOKEN})
});
return res.json();
}


window.addEventListener('DOMContentLoaded', ()=>{
const voteBtn = document.getElementById('voteBtn');
const cancelBtn = document.getElementById('cancelBtn');
const presenterField = document.getElementById('presenter');
presenterField.textContent = PRESENTER_ID;


voteBtn.addEventListener('click', async ()=>{
if (hasLocalVoted(PRESENTER_ID)){
alert('この端末では既に投票済みです。');
return;
}
voteBtn.disabled = true;
voteBtn.textContent = '送信中...';
try{
const resp = await postVote(PRESENTER_ID);
if (resp.ok){
markLocalVoted(PRESENTER_ID);
// show thanks page
window.location.href = '/thanks';
} else {
if (resp.error === 'already_voted'){
alert('既に投票済みです（サーバ登録済）。');
} else {
alert('投票中にエラーが発生しました: ' + (resp.error||'unknown'));
}
voteBtn.disabled = false;
voteBtn.textContent = '投票する';
}
}catch(e){
alert('通信エラー');
voteBtn.disabled = false;
voteBtn.textContent = '投票する';
}
});


cancelBtn.addEventListener('click', ()=>{
// close tab if possible
window.open('','_self');
window.close();
});
});
