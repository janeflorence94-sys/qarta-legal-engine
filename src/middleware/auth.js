import { clientDb } from '../lib/supabase.js';

/**
 * requireAuth — Express middleware.
 * Extracts and verifies the Bearer JWT from the Authorization header.
 * Attaches { id } to req.user on success; returns 401 on failure.
 */
export async function requireAuth(req, res, next) {
  const header = req.headers['authorization'] ?? '';

  if (!header.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header.' });
  }

  const token = header.slice(7); // strip "Bearer "

  const { data, error } = await clientDb.auth.getUser(token);

  if (error || !data?.user) {
    return res.status(401).json({ error: 'Invalid or expired token.' });
  }

  req.user = { id: data.user.id };
  next();
}
