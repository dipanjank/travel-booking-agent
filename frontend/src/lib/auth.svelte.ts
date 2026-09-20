/** Reactive auth state using Svelte 5 runes. */

interface AuthState {
	accessToken: string | null;
	expiresAt: number | null;
	role: string | null;
}

const STORAGE_KEY = 'auth';

function parseJwtPayload(token: string): Record<string, unknown> | null {
	try {
		const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
		return JSON.parse(atob(base64));
	} catch {
		return null;
	}
}

function loadFromStorage(): AuthState {
	if (typeof window === 'undefined') return { accessToken: null, expiresAt: null, role: null };
	try {
		const raw = sessionStorage.getItem(STORAGE_KEY);
		if (raw) return JSON.parse(raw);
	} catch {
		// Corrupted storage — start fresh.
	}
	return { accessToken: null, expiresAt: null, role: null };
}

function saveToStorage(state: AuthState): void {
	if (typeof window === 'undefined') return;
	if (state.accessToken) {
		sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
	} else {
		sessionStorage.removeItem(STORAGE_KEY);
	}
}

const initial = loadFromStorage();
let accessToken = $state<string | null>(initial.accessToken);
let expiresAt = $state<number | null>(initial.expiresAt);
let role = $state<string | null>(initial.role);

export const auth = {
	get accessToken() {
		return accessToken;
	},
	get isAuthenticated() {
		return accessToken !== null;
	},
	get expiresAt() {
		return expiresAt;
	},
	get role() {
		return role;
	},
	get isAdmin() {
		return role === 'ADMIN_USER';
	},

	setToken(token: string, expiresIn: number) {
		accessToken = token;
		expiresAt = Date.now() + expiresIn * 1000;
		const payload = parseJwtPayload(token);
		role = (payload?.role as string) ?? null;
		saveToStorage({ accessToken, expiresAt, role });
	},

	clear() {
		accessToken = null;
		expiresAt = null;
		role = null;
		saveToStorage({ accessToken: null, expiresAt: null, role: null });
	}
};
