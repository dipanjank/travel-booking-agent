import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';
import { auth } from '$lib/auth.svelte';

export const ssr = false;

const PUBLIC_ROUTES = ['/login'];

export const load: LayoutLoad = ({ url }) => {
	if (!PUBLIC_ROUTES.includes(url.pathname) && !auth.isAuthenticated) {
		redirect(302, '/login');
	}
};
