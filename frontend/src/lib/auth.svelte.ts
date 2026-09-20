/** Reactive auth state using Svelte 5 runes. */

interface AuthState {
	accessToken: string | null;
	expiresAt: number | null;
}

const STORAGE_KEY = 'auth';

function loadFromStorage(): AuthState {
	if (typeof window === 'undefined') return { accessToken: null, expiresAt: null };
	try {
		const raw = sessionStorage.getItem(STORAGE_KEY);
		if (raw) return JSON.parse(raw);
	} catch {
		// Corrupted storage — start fresh.
	}
	return { accessToken: null, expiresAt: null };
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

	setToken(token: string, expiresIn: number) {
		accessToken = token;
		expiresAt = Date.now() + expiresIn * 1000;
		saveToStorage({ accessToken, expiresAt });
	},

	clear() {
		accessToken = null;
		expiresAt = null;
		saveToStorage({ accessToken: null, expiresAt: null });
	}
};
