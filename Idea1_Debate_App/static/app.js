const startBtn = document.getElementById('start-btn');
const topicInput = document.getElementById('topic-input');
const turnsInput = document.getElementById('turns-input');
const messagesContainer = document.getElementById('messages-container');
const typingIndicator = document.getElementById('typing-indicator');
const currentDebater = document.getElementById('current-debater');

let eventSource = null;
let currentMessageBubble = null;

startBtn.addEventListener('click', startDebate);

function startDebate() {
    const topic = encodeURIComponent(topicInput.value.trim() || 'What is the most important skill for a software engineer in the age of AI?');
    const turns = turnsInput.value;
    
    // Reset UI
    messagesContainer.innerHTML = '';
    startBtn.disabled = true;
    startBtn.textContent = 'Debating...';
    
    if (eventSource) {
        eventSource.close();
    }
    
    eventSource = new EventSource(`/stream-debate?topic=${topic}&turns=${turns}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        switch(data.type) {
            case 'system':
                appendSystemMessage(data.content);
                typingIndicator.classList.add('hidden');
                break;
            case 'speaker':
                createNewMessageBubble(data.name, data.model);
                typingIndicator.classList.remove('hidden');
                currentDebater.textContent = data.name;
                currentDebater.style.color = data.name === 'Llama' ? 'var(--llama-color)' : 'var(--mixtral-color)';
                break;
            case 'token':
                if (currentMessageBubble) {
                    const cleanToken = data.content.replace(/\\n/g, '<br>');
                    currentMessageBubble.innerHTML += cleanToken;
                    scrollToBottom();
                }
                break;
            case 'done':
                // Turn finished
                currentMessageBubble = null;
                break;
            case 'error':
                appendSystemMessage('Error: ' + data.content);
                finishDebate();
                break;
        }
    };
    
    eventSource.onerror = function(err) {
        console.error("SSE Error:", err);
        finishDebate();
    };
}

function appendSystemMessage(text) {
    const el = document.createElement('div');
    el.className = 'system-message';
    el.textContent = text;
    messagesContainer.appendChild(el);
    scrollToBottom();
}

function createNewMessageBubble(speaker, model) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${speaker.toLowerCase()}`;
    
    const nameEl = document.createElement('div');
    nameEl.className = 'speaker-name';
    nameEl.textContent = `${speaker} (${model.split('/').pop()})`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    wrapper.appendChild(nameEl);
    wrapper.appendChild(bubble);
    messagesContainer.appendChild(wrapper);
    
    currentMessageBubble = bubble;
    scrollToBottom();
}

function finishDebate() {
    if (eventSource) {
        eventSource.close();
    }
    startBtn.disabled = false;
    startBtn.textContent = 'Start Debate';
    typingIndicator.classList.add('hidden');
}

function scrollToBottom() {
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}
