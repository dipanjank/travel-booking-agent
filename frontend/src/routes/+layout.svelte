<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import { auth } from '$lib/auth.svelte';
	import { logout } from '$lib/api';
	import { goto } from '$app/navigation';

	let { children } = $props();

	async function handleLogout() {
		await logout();
		goto('/login');
	}
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if auth.isAuthenticated}
	<nav>
		<span class="brand">Travel Booking Agent</span>
		<button onclick={handleLogout}>Logout</button>
	</nav>
{/if}

<main>
	{@render children()}
</main>

<style>
	:global(body) {
		margin: 0;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
		color: #1a1a1a;
	}

	nav {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.75rem 1.5rem;
		border-bottom: 1px solid #e0e0e0;
	}

	.brand {
		font-weight: 600;
		font-size: 1rem;
	}

	nav button {
		padding: 0.4rem 0.8rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		background: #fff;
		cursor: pointer;
		font-size: 0.85rem;
	}

	main {
		max-width: 960px;
		margin: 0 auto;
		padding: 1rem 1.5rem;
	}
</style>
