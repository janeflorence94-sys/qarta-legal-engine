import { Router } from 'express';
import { clientDb } from '../lib/supabase.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

// All assessment routes require authentication.
router.use(requireAuth);

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Resolve org_id for the authenticated user.
 * Returns null if the profile is not found.
 */
async function getOrgId(user_id) {
  const { data, error } = await clientDb
    .from('user_profiles')
    .select('org_id')
    .eq('user_id', user_id)
    .single();

  if (error || !data) return null;
  return data.org_id;
}

// ── POST /assessments ─────────────────────────────────────────────────────────

router.post('/', async (req, res, next) => {
  try {
    const org_id = await getOrgId(req.user.id);
    if (!org_id) {
      return res.status(403).json({ error: 'User profile not found or no org assigned.' });
    }

    const {
      corridor,
      origin_country,
      target_country,
      sector,
      assessment_type,
    } = req.body;

    const { data, error } = await clientDb
      .from('assessments')
      .insert({
        org_id,
        corridor,
        origin_country,
        target_country,
        sector,
        assessment_type,
        status: 'draft',
      })
      .select('id')
      .single();

    if (error) throw error;

    return res.status(201).json({ id: data.id });
  } catch (err) {
    next(err);
  }
});

// ── POST /assessments/:id/run ─────────────────────────────────────────────────

router.post('/:id/run', async (req, res, next) => {
  try {
    const { id } = req.params;
    const org_id = await getOrgId(req.user.id);
    if (!org_id) {
      return res.status(403).json({ error: 'User profile not found or no org assigned.' });
    }

    // Confirm ownership (belt-and-suspenders on top of RLS).
    const { data: existing, error: fetchErr } = await clientDb
      .from('assessments')
      .select('id, org_id, status')
      .eq('id', id)
      .single();

    if (fetchErr || !existing) {
      return res.status(404).json({ error: 'Assessment not found.' });
    }
    if (existing.org_id !== org_id) {
      return res.status(403).json({ error: 'Access denied.' });
    }

    // Mark processing.
    await clientDb
      .from('assessments')
      .update({ status: 'processing' })
      .eq('id', id);

    // ── Compass engine placeholder ────────────────────────────────────────────
    console.log(`[assessments] Compass engine called for assessment ${id} (placeholder)`);
    // TODO: replace with real Compass engine call.
    // const compassResult = await runCompassEngine({ ...existing });
    const compassResult = {
      mess_score: null,
      verdict: 'pending',
      report_json: {},
    };
    // ─────────────────────────────────────────────────────────────────────────

    const { data: updated, error: updateErr } = await clientDb
      .from('assessments')
      .update({
        mess_score: compassResult.mess_score,
        verdict: compassResult.verdict,
        report_json: compassResult.report_json,
        status: 'complete',
        completed_at: new Date().toISOString(),
      })
      .eq('id', id)
      .select()
      .single();

    if (updateErr) throw updateErr;

    return res.json(updated);
  } catch (err) {
    next(err);
  }
});

// ── GET /assessments ──────────────────────────────────────────────────────────

router.get('/', async (req, res, next) => {
  try {
    // RLS automatically scopes to the authenticated user's org.
    const { data, error } = await clientDb
      .from('assessments')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) throw error;

    return res.json(data);
  } catch (err) {
    next(err);
  }
});

// ── GET /assessments/:id ──────────────────────────────────────────────────────

router.get('/:id', async (req, res, next) => {
  try {
    const { data, error } = await clientDb
      .from('assessments')
      .select('*')
      .eq('id', req.params.id)
      .single();

    // RLS will return no row (PGRST116) if the org doesn't own it.
    if (error?.code === 'PGRST116' || !data) {
      return res.status(404).json({ error: 'Assessment not found.' });
    }
    if (error) throw error;

    return res.json(data);
  } catch (err) {
    next(err);
  }
});

export default router;
