<script lang="ts">
	import { apiFetch } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { goto } from '$app/navigation';

	interface UserItem {
		id: string;
		username: string;
		email: string;
		role: string;
		created_at: string;
	}

	interface CreatedUser extends UserItem {
		password: string;
	}

	let users = $state<UserItem[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Create user form
	let newUsername = $state('');
	let newEmail = $state('');
	let newRole = $state('APPLICATION_USER');
	let creating = $state(false);
	let createError = $state<string | null>(null);
	let createdUser = $state<CreatedUser | null>(null);

	// Delete state
	let deletingId = $state<string | null>(null);

	if (!auth.isAdmin) {
		goto('/');
	}

	async function loadUsers() {
		loading = true;
		error = null;
		try {
			const res = await apiFetch('/admin/users');
			if (!res.ok) throw new Error('Failed to load users');
			const data = await res.json();
			users = data.items;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load users';
		} finally {
			loading = false;
		}
	}

	async function handleCreate(e: SubmitEvent) {
		e.preventDefault();
		creating = true;
		createError = null;
		createdUser = null;
		try {
			const res = await apiFetch('/admin/users', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username: newUsername, email: newEmail, role: newRole })
			});
			if (!res.ok) {
				const body = await res.json().catch(() => null);
				throw new Error(body?.detail ?? 'Failed to create user');
			}
			createdUser = await res.json();
			newUsername = '';
			newEmail = '';
			newRole = 'APPLICATION_USER';
			await loadUsers();
		} catch (e) {
			createError = e instanceof Error ? e.message : 'Failed to create user';
		} finally {
			creating = false;
		}
	}

	async function handleDelete(user: UserItem) {
		if (!confirm(`Delete user "${user.username}"?`)) return;
		deletingId = user.id;
		try {
			const res = await apiFetch(`/admin/users/${user.id}`, { method: 'DELETE' });
			if (!res.ok) {
				const body = await res.json().catch(() => null);
				alert(body?.detail ?? 'Failed to delete user');
				return;
			}
			await loadUsers();
		} finally {
			deletingId = null;
		}
	}

	loadUsers();
</script>

<svelte:head>
	<title>User Management</title>
</svelte:head>

<h1>User Management</h1>

<section class="create-section">
	<h2>Create User</h2>
	<form onsubmit={handleCreate}>
		<div class="form-row">
			<label>
				Username
				<input type="text" bind:value={newUsername} required />
			</label>
			<label>
				Email
				<input type="email" bind:value={newEmail} required />
			</label>
			<label>
				Role
				<select bind:value={newRole}>
					<option value="APPLICATION_USER">Application User</option>
					<option value="ADMIN_USER">Admin User</option>
				</select>
			</label>
			<button type="submit" disabled={creating}>
				{creating ? 'Creating...' : 'Create'}
			</button>
		</div>
		{#if createError}
			<p class="error">{createError}</p>
		{/if}
	</form>

	{#if createdUser}
		<div class="created-notice">
			<strong>User created:</strong> {createdUser.username}<br />
			<strong>Password:</strong> <code>{createdUser.password}</code>
			<br />
			<small>Copy this password now — it won't be shown again.</small>
		</div>
	{/if}
</section>

<section>
	<h2>Users</h2>
	{#if loading}
		<p>Loading...</p>
	{:else if error}
		<p class="error">{error}</p>
	{:else if users.length === 0}
		<p>No users found.</p>
	{:else}
		<table>
			<thead>
				<tr>
					<th>Username</th>
					<th>Email</th>
					<th>Role</th>
					<th>Created</th>
					<th></th>
				</tr>
			</thead>
			<tbody>
				{#each users as user (user.id)}
					<tr>
						<td>{user.username}</td>
						<td>{user.email}</td>
						<td><span class="role-badge" class:admin={user.role === 'ADMIN_USER'}>{user.role === 'ADMIN_USER' ? 'Admin' : 'User'}</span></td>
						<td>{new Date(user.created_at).toLocaleDateString()}</td>
						<td>
							{#if user.role !== 'ADMIN_USER'}
								<button
									class="delete-btn"
									onclick={() => handleDelete(user)}
									disabled={deletingId === user.id}
								>
									{deletingId === user.id ? 'Deleting...' : 'Delete'}
								</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</section>

<style>
	h1 {
		font-size: 1.4rem;
		margin-bottom: 1.5rem;
	}

	h2 {
		font-size: 1.1rem;
		margin-bottom: 0.75rem;
	}

	.create-section {
		margin-bottom: 2rem;
		padding-bottom: 1.5rem;
		border-bottom: 1px solid #e0e0e0;
	}

	.form-row {
		display: flex;
		gap: 0.75rem;
		align-items: flex-end;
		flex-wrap: wrap;
	}

	label {
		display: flex;
		flex-direction: column;
		font-size: 0.85rem;
		font-weight: 500;
		gap: 0.25rem;
	}

	input, select {
		padding: 0.45rem 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 0.9rem;
	}

	.form-row button {
		padding: 0.45rem 1rem;
		border: none;
		border-radius: 4px;
		background: #1a1a1a;
		color: #fff;
		font-size: 0.9rem;
		cursor: pointer;
		white-space: nowrap;
	}

	.form-row button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.error {
		color: #c00;
		font-size: 0.85rem;
		margin: 0.5rem 0 0;
	}

	.created-notice {
		margin-top: 0.75rem;
		padding: 0.75rem;
		background: #f0f9f0;
		border: 1px solid #b2d8b2;
		border-radius: 4px;
		font-size: 0.9rem;
		line-height: 1.6;
	}

	.created-notice code {
		background: #e8e8e8;
		padding: 0.15rem 0.4rem;
		border-radius: 3px;
		font-size: 0.85rem;
	}

	.created-notice small {
		color: #666;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.9rem;
	}

	th {
		text-align: left;
		padding: 0.5rem 0.75rem;
		border-bottom: 2px solid #e0e0e0;
		font-weight: 600;
		font-size: 0.85rem;
		color: #555;
	}

	td {
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid #eee;
	}

	.role-badge {
		display: inline-block;
		padding: 0.15rem 0.5rem;
		border-radius: 3px;
		font-size: 0.8rem;
		background: #eee;
		color: #555;
	}

	.role-badge.admin {
		background: #e8e0f0;
		color: #5a3d7a;
	}

	.delete-btn {
		padding: 0.25rem 0.6rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		background: #fff;
		color: #c00;
		font-size: 0.8rem;
		cursor: pointer;
	}

	.delete-btn:hover {
		background: #fff0f0;
		border-color: #c00;
	}

	.delete-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
