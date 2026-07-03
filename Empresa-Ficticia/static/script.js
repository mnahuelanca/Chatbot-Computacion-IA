const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('send');
const messagesEl = document.getElementById('messages');
const v2ScoreEl = document.getElementById('v2-score');
const v2DetailEl = document.getElementById('v2-detail');

function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = 'message ' + role;
  div.textContent = text;
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function loadSmokeMetrics() {
  if (!v2ScoreEl || !v2DetailEl) return;
  try {
    const res = await fetch('/smoke');
    if (!res.ok) throw new Error('No se obtuvo métricas');
    const data = await res.json();
    v2ScoreEl.textContent = `V2.0: ${data.score}% (${data.hits}/${data.total})`;
    if (data.errors === 0) {
      v2DetailEl.textContent = 'El smoketest automático no detectó errores en las 30 preguntas.';
    } else {
      const firstFailure = data.failures && data.failures.length > 0 ? data.failures[0] : null;
      if (firstFailure) {
        v2DetailEl.textContent = `Fallo en ${data.errors} pregunta(s). Ejemplo: ID ${firstFailure.id} - "${firstFailure.pregunta}".`;
      } else {
        v2DetailEl.textContent = `Fallo en ${data.errors} pregunta(s). Revise los detalles de la prueba.`;
      }
    }
  } catch (error) {
    v2ScoreEl.textContent = 'No disponible';
    v2DetailEl.textContent = 'No se pudo cargar el resultado del smoketest dinámico.';
  }
}

sendBtn.addEventListener('click', async () => {
  const text = inputEl.value.trim();
  if (!text) return;
  appendMessage('user', text);
  inputEl.value = '';

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const json = await res.json();
    appendMessage('bot', json.response);
  } catch (e) {
    appendMessage('bot', 'Error de conexión con el servidor.');
  }
});

inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendBtn.click();
});

window.addEventListener('DOMContentLoaded', loadSmokeMetrics);
