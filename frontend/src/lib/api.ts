/**
 * API wrapper that attaches the Bearer token, sends credentials (for
 * HttpOnly refresh cookie), and auto-refreshes on 401.
 */

import { auth } from '$lib/auth.svelte';

const BASE = '/api';

interface TokenResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
}

async function refreshToken(): Promise<boolean> {
	try {
		const res = await fetch(`${BASE}/auth/refresh`, {
			method: 'POST',
			credentials: 'include'
		});
		if (!res.ok) return false;
		const data: TokenResponse = await res.json();
		auth.setToken(data.access_token, data.expires_in);
		return true;
	} catch {
		return false;
	}
}

/** Send an authenticated request. Retries once on 401 after refreshing. */
export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
	const headers = new Headers(init.headers);
	if (auth.accessToken) {
		headers.set('Authorization', `Bearer ${auth.accessToken}`);
	}

	const res = await fetch(`${BASE}${path}`, {
		...init,
		headers,
		credentials: 'include'
	});

	if (res.status === 401 && auth.accessToken) {
		const refreshed = await refreshToken();
		if (refreshed) {
			headers.set('Authorization', `Bearer ${auth.accessToken}`);
			return fetch(`${BASE}${path}`, {
				...init,
				headers,
				credentials: 'include'
			});
		}
		auth.clear();
	}

	return res;
}

/** Log in and store the access token. Returns an error message on failure. */
export async function login(username: string, password: string): Promise<string | null> {
	const res = await fetch(`${BASE}/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		credentials: 'include',
		body: JSON.stringify({ username, password })
	});

	if (!res.ok) {
		const body = await res.json().catch(() => null);
		return body?.detail ?? 'Login failed';
	}

	const data: TokenResponse = await res.json();
	auth.setToken(data.access_token, data.expires_in);
	return null;
}

/** Log out: call the backend and clear local state. */
export async function logout(): Promise<void> {
	await apiFetch('/auth/logout', { method: 'POST' }).catch(() => {});
	auth.clear();
}
