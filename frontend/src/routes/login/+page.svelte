<script lang="ts">
	import { goto } from '$app/navigation';
	import { login } from '$lib/api';

	let username = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let loading = $state(false);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		error = null;
		loading = true;
		const err = await login(username, password);
		loading = false;
		if (err) {
			error = err;
		} else {
			goto('/');
		}
	}
</script>

<svelte:head>
	<title>Login</title>
</svelte:head>

<div class="login-container">
	<div class="login-card">
		<h1>Travel Booking Agent</h1>
		<form onsubmit={handleSubmit}>
			<label>
				Username
				<input type="text" bind:value={username} required autocomplete="username" />
			</label>
			<label>
				Password
				<input type="password" bind:value={password} required autocomplete="current-password" />
			</label>
			{#if error}
				<p class="error">{error}</p>
			{/if}
			<button type="submit" disabled={loading}>
				{loading ? 'Signing in...' : 'Sign in'}
			</button>
		</form>
	</div>
</div>

<style>
	.login-container {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
	}

	.login-card {
		width: 100%;
		max-width: 360px;
		padding: 2rem;
	}

	h1 {
		font-size: 1.4rem;
		margin-bottom: 1.5rem;
		text-align: center;
	}

	label {
		display: block;
		margin-bottom: 1rem;
		font-size: 0.875rem;
		font-weight: 500;
	}

	input {
		display: block;
		width: 100%;
		margin-top: 0.25rem;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 0.95rem;
		box-sizing: border-box;
	}

	button {
		width: 100%;
		padding: 0.6rem;
		margin-top: 0.5rem;
		border: none;
		border-radius: 4px;
		background: #1a1a1a;
		color: #fff;
		font-size: 0.95rem;
		cursor: pointer;
	}

	button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.error {
		color: #c00;
		font-size: 0.85rem;
		margin: 0 0 0.5rem;
	}
</style>
