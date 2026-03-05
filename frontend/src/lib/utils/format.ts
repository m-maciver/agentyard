/**
 * Format sats amount with thousands separator
 */
export function formatSats(sats: number): string {
	return sats.toLocaleString('en-US');
}

/**
 * Format sats as approximate USD (very rough: ~$0.00042 per sat at ~$42k BTC)
 * Real implementation would use a live BTC price feed
 */
export function satsToUsd(sats: number, btcPriceUsd = 95000): string {
	const usd = (sats / 100_000_000) * btcPriceUsd;
	if (usd < 0.01) return '< $0.01';
	return `$${usd.toFixed(2)}`;
}

/**
 * Format a datetime string to human-readable
 */
export function formatDate(iso: string): string {
	const d = new Date(iso);
	return d.toLocaleDateString('en-AU', {
		year: 'numeric',
		month: 'short',
		day: 'numeric'
	});
}

export function formatDateTime(iso: string): string {
	const d = new Date(iso);
	return d.toLocaleDateString('en-AU', {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}

/**
 * Format a month/year from ISO string
 */
export function formatMonthYear(iso: string): string {
	const d = new Date(iso);
	return d.toLocaleDateString('en-AU', { year: 'numeric', month: 'short' });
}

/**
 * Truncate a string (e.g. job IDs, invoices)
 */
export function truncate(str: string, maxLen = 12): string {
	if (str.length <= maxLen) return str;
	return str.slice(0, maxLen) + '...';
}

/**
 * Shorten a UUID for display: first 8 chars
 */
export function shortId(uuid: string): string {
	return uuid.slice(0, 8);
}

/**
 * Time remaining until a datetime
 */
export function timeRemaining(iso: string): string {
	const now = Date.now();
	const target = new Date(iso).getTime();
	const diff = target - now;
	if (diff <= 0) return 'Expired';
	const h = Math.floor(diff / 3_600_000);
	const m = Math.floor((diff % 3_600_000) / 60_000);
	const s = Math.floor((diff % 60_000) / 1000);
	if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
	return `${m}:${String(s).padStart(2, '0')}`;
}

/**
 * Get initials from a name
 */
export function initials(name: string): string {
	return name
		.split(' ')
		.map(w => w[0])
		.join('')
		.slice(0, 2)
		.toUpperCase();
}

/**
 * Time elapsed since a datetime
 */
export function timeAgo(iso: string): string {
	const diff = Date.now() - new Date(iso).getTime();
	const mins = Math.floor(diff / 60_000);
	if (mins < 1) return 'just now';
	if (mins < 60) return `${mins}m ago`;
	const hrs = Math.floor(mins / 60);
	if (hrs < 24) return `${hrs}h ago`;
	const days = Math.floor(hrs / 24);
	return `${days}d ago`;
}
