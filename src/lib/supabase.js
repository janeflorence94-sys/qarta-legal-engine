import { createClient } from '@supabase/supabase-js';

const { SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY } = process.env;

if (!SUPABASE_URL)       throw new Error('Missing env var: SUPABASE_URL');
if (!SUPABASE_ANON_KEY)  throw new Error('Missing env var: SUPABASE_ANON_KEY');
if (!SUPABASE_SERVICE_KEY) throw new Error('Missing env var: SUPABASE_SERVICE_KEY');

/**
 * clientDb — uses the anon key.
 * All tenant operations (assessments, legal_jobs, user_profiles) go through this client.
 * Supabase RLS policies apply automatically.
 */
export const clientDb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { persistSession: false },
});

/**
 * serviceDb — uses the service-role key.
 * ONLY used by logInvocation() to write to rule_invocation_log.
 * Never expose this client to route handlers or pass it to untrusted code.
 */
export const serviceDb = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { persistSession: false },
});
