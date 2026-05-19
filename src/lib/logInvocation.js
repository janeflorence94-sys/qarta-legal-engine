import { createHash } from 'node:crypto';
import { serviceDb } from './supabase.js';

/**
 * logInvocation — writes one row to rule_invocation_log via the service-role client.
 *
 * PII policy: this function must NEVER receive or log company names, user names,
 * deal sizes, storage paths, counterparty names, or any other identifying data.
 * Only the fields listed below are accepted.
 *
 * @param {object} params
 * @param {string} params.org_id                     - Tenant org UUID (hashed before storage)
 * @param {string} params.corridor                   - e.g. "CN_SG", "SG_MY"
 * @param {string} params.sector                     - e.g. "technology", "manufacturing"
 * @param {string} params.document_type              - e.g. "nda", "jv_agreement"
 * @param {string[]} params.clauses_fired            - Array of clause ID strings
 * @param {string} params.jurisdiction_config_version
 * @param {string} params.outcome                    - e.g. "adapted", "error"
 */
export async function logInvocation({
  org_id,
  corridor,
  sector,
  document_type,
  clauses_fired,
  jurisdiction_config_version,
  outcome,
}) {
  try {
    const org_id_hash = createHash('sha256').update(String(org_id)).digest('hex');

    const { error } = await serviceDb.from('rule_invocation_log').insert({
      org_id_hash,
      corridor,
      sector,
      document_type,
      clauses_fired,
      jurisdiction_config_version,
      outcome,
    });

    if (error) {
      console.error('[logInvocation] Supabase insert error:', error.message);
    }
  } catch (err) {
    // Never propagate — callers must not be blocked by logging failures.
    console.error('[logInvocation] Unexpected error:', err.message);
  }
}
