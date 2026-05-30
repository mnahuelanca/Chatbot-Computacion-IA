const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const messagesEl = document.getElementById('messages');

function appendMessage(role, text){
  const div = document.createElement('div');
  div.className = 'message ' + role;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

sendBtn.addEventListener('click', async () => {
  const text = inputEl.value.trim();
  if(!text) return;
  appendMessage('user', text);
  inputEl.value = '';

  try{
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({message: text})
    });
    const j = await res.json();
    appendMessage('bot', j.response);
  }catch(e){
    appendMessage('bot', 'Error de conexión con el servidor.');
  }
});

inputEl.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter') sendBtn.click();
});
