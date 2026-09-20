<script lang="ts">
	import { apiFetch } from '$lib/api';

	interface Message {
		role: 'user' | 'assistant';
		content: string;
	}

	let messages = $state<Message[]>([]);
	let input = $state('');
	let loading = $state(false);
	let messagesEl: HTMLDivElement;

	function generateUUID(): string {
		const bytes = crypto.getRandomValues(new Uint8Array(16));
		bytes[6] = (bytes[6] & 0x0f) | 0x40;
		bytes[8] = (bytes[8] & 0x3f) | 0x80;
		const hex = [...bytes].map((b) => b.toString(16).padStart(2, '0')).join('');
		return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
	}

	function getThreadId(): string {
		let id = sessionStorage.getItem('chat_thread_id');
		if (!id) {
			id = generateUUID();
			sessionStorage.setItem('chat_thread_id', id);
		}
		return id;
	}

	const threadId = getThreadId();

	function scrollToBottom() {
		if (messagesEl) {
			messagesEl.scrollTop = messagesEl.scrollHeight;
		}
	}

	async function handleSend(e: SubmitEvent) {
		e.preventDefault();
		const text = input.trim();
		if (!text || loading) return;

		messages = [...messages, { role: 'user', content: text }];
		input = '';
		loading = true;

		// Scroll after DOM update
		await tick();
		scrollToBottom();

		try {
			const res = await apiFetch('/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ message: text, thread_id: threadId })
			});

			if (!res.ok) {
				const body = await res.json().catch(() => null);
				throw new Error(body?.detail ?? 'Failed to get response');
			}

			const data = await res.json();
			messages = [...messages, { role: 'assistant', content: data.response }];
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Something went wrong';
			messages = [...messages, { role: 'assistant', content: `Error: ${msg}` }];
		} finally {
			loading = false;
			await tick();
			scrollToBottom();
		}
	}

	function tick(): Promise<void> {
		return new Promise((resolve) => setTimeout(resolve, 0));
	}
</script>

<svelte:head>
	<title>Search and Book Flights</title>
</svelte:head>

<div class="chat-container">
	<h1>Search and Book Flights</h1>

	<div class="messages" bind:this={messagesEl}>
		{#if messages.length === 0 && !loading}
			<p class="empty">Ask about flights — for example, "Are there any direct flights from JFK to LAX?"</p>
		{/if}

		{#each messages as msg}
			<div class="message {msg.role}">
				<div class="bubble">{msg.content}</div>
			</div>
		{/each}

		{#if loading}
			<div class="message assistant">
				<div class="bubble loading">Thinking...</div>
			</div>
		{/if}
	</div>

	<form onsubmit={handleSend}>
		<input
			type="text"
			bind:value={input}
			placeholder="Ask about flights..."
			disabled={loading}
		/>
		<button type="submit" disabled={loading || !input.trim()}>Send</button>
	</form>
</div>

<style>
	h1 {
		font-size: 1.4rem;
		margin-bottom: 1rem;
	}

	.chat-container {
		display: flex;
		flex-direction: column;
		height: calc(100vh - 120px);
	}

	.messages {
		flex: 1;
		overflow-y: auto;
		padding: 0.5rem 0;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.empty {
		color: #888;
		font-size: 0.9rem;
		text-align: center;
		margin-top: 2rem;
	}

	.message {
		display: flex;
	}

	.message.user {
		justify-content: flex-end;
	}

	.message.assistant {
		justify-content: flex-start;
	}

	.bubble {
		max-width: 75%;
		padding: 0.6rem 0.9rem;
		border-radius: 8px;
		font-size: 0.9rem;
		line-height: 1.5;
		white-space: pre-wrap;
		word-break: break-word;
	}

	.message.user .bubble {
		background: #1a1a1a;
		color: #fff;
	}

	.message.assistant .bubble {
		background: #f0f0f0;
		color: #1a1a1a;
	}

	.bubble.loading {
		color: #888;
		font-style: italic;
	}

	form {
		display: flex;
		gap: 0.5rem;
		padding-top: 0.75rem;
		border-top: 1px solid #e0e0e0;
	}

	form input {
		flex: 1;
		padding: 0.55rem 0.75rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	form button {
		padding: 0.55rem 1.25rem;
		border: none;
		border-radius: 4px;
		background: #1a1a1a;
		color: #fff;
		font-size: 0.9rem;
		cursor: pointer;
		white-space: nowrap;
	}

	form button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
