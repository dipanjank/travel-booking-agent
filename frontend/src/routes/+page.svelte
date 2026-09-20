<script lang="ts">
	import { auth } from '$lib/auth.svelte';
</script>

<svelte:head>
	<title>Travel Booking Agent</title>
</svelte:head>

<h1>Travel Booking Agent</h1>

<div class="menu">
	{#if auth.isAdmin}
		<a href="/admin/users" class="menu-card">
			<span class="menu-icon">&#128101;</span>
			<span class="menu-label">Manage Users</span>
			<span class="menu-desc">Create, view and delete user accounts</span>
		</a>
	{/if}
	<a href="/flights" class="menu-card">
		<span class="menu-icon">&#9992;</span>
		<span class="menu-label">Search and Book Flights</span>
		<span class="menu-desc">Find and book flights using the chat assistant</span>
	</a>
	<a href="/bookings" class="menu-card">
		<span class="menu-icon">&#128196;</span>
		<span class="menu-label">My Bookings</span>
		<span class="menu-desc">View your booking history</span>
	</a>
</div>

<style>
	h1 {
		font-size: 1.4rem;
		margin-bottom: 1.5rem;
	}

	.menu {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: 1rem;
	}

	.menu-card {
		display: flex;
		flex-direction: column;
		padding: 1.25rem;
		border: 1px solid #e0e0e0;
		border-radius: 8px;
		text-decoration: none;
		color: #1a1a1a;
		transition: border-color 0.15s, box-shadow 0.15s;
	}

	.menu-card:hover {
		border-color: #999;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	}

	.menu-icon {
		font-size: 1.75rem;
		margin-bottom: 0.5rem;
	}

	.menu-label {
		font-weight: 600;
		font-size: 1rem;
		margin-bottom: 0.35rem;
	}

	.menu-desc {
		font-size: 0.85rem;
		color: #666;
	}
</style>
