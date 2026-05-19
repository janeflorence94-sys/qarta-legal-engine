import { Router } from 'express';
import multer from 'multer';
import { randomUUID } from 'node:crypto';
import path from 'node:path';
import { clientDb } from '../lib/supabase.js';
import { logInvocation } from '../lib/logInvocation.js';
import { requireAuth } from '../middleware/auth.js';

const router = Router();

// Multer — store file in memory so we can stream it to Supabase Storage.
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 20 * 1024 * 1024 }, // 20 MB cap
});

// All legal-job routes require authentication.
router.use(requireAuth);

// ── Helpers ───────────────────────────────────────────────────────────────────

async function getOrgId(user_id) {
  const { data, error } = await clientDb
    .from('user_profiles')
    .select('org_id')
    .eq('user_id', user_id)
    .single();

  if (error || !data) return null;
  return data.org_id;
}

async function uploadToStorage(buffer, storagePath, contentType) {
  const { error } = await clientDb.storage
    .from('legal-documents')
    .upload(storagePath, buffer, {
      contentType,
      upsert: false,
    });

  if (error) throw new Error(`Storage upload failed: ${error.message}`);
}

// ── POST /legal-jobs ──────────────────────────────────────────────────────────

router.post('/', upload.single('file'), async (req, res, next) => {
  try {
    const org_id = await getOrgId(req.user.id);
    if (!org_id) {
      return res.status(403).json({ error: 'User profile not found or no org assigned.' });
    }

    if (!req.file) {
      return res.status(400).json({ error: 'A file upload is required.' });
    }

    const {
      corridor,
      origin_country,
      target_country,
      sector,
      document_type,
      assessment_id,
      jurisdiction_config_version,
    } = req.body;

    const job_id = randomUUID();
    const ext = path.extname(req.file.originalname).toLowerCase().replace('.', '') || 'bin';
    const origin_storage_path = `${org_id}/${job_id}/origin.${ext}`;

    // Upload origin document to Supabase Storage.
    await uploadToStorage(req.file.buffer, origin_storage_path, req.file.mimetype);

    // Insert legal_jobs row.
    const { data, error } = await clientDb
      .from('legal_jobs')
      .insert({
        id: job_id,
        org_id,
        corridor,
        origin_country,
        target_country,
        sector,
        document_type,
        assessment_id: assessment_id || null,
        jurisdiction_config_version: jurisdiction_config_version || null,
        origin_storage_path,
        status: 'pending',
      })
      .select('id')
      .single();

    if (error) throw error;

    return res.status(201).json({ id: data.id });
  } catch (err) {
    next(err);
  }
});

// ── POST /legal-jobs/:id/run ──────────────────────────────────────────────────

router.post('/:id/run', async (req, res, next) => {
  try {
    const { id } = req.params;
    const org_id = await getOrgId(req.user.id);
    if (!org_id) {
      return res.status(403).json({ error: 'User profile not found or no org assigned.' });
    }

    // Fetch job and verify ownership.
    const { data: job, error: fetchErr } = await clientDb
      .from('legal_jobs')
      .select('*')
      .eq('id', id)
      .single();

    if (fetchErr?.code === 'PGRST116' || !job) {
      return res.status(404).json({ error: 'Legal job not found.' });
    }
    if (fetchErr) throw fetchErr;
    if (job.org_id !== org_id) {
      return res.status(403).json({ error: 'Access denied.' });
    }

    // Mark processing.
    await clientDb
      .from('legal_jobs')
      .update({ status: 'processing' })
      .eq('id', id);

    // ── Legal engine placeholder ───────────────────────────────────────────────
    console.log(`[legal-jobs] Legal engine called for job ${id} (placeholder)`);
    // TODO: replace with real Legal engine call (adapt_contract / pipeline.py proxy).
    // const engineResult = await callLegalEngine({ ...job });
    const engineResult = {
      outputBuffer: Buffer.from('placeholder docx content'),
      clause_count_adapted: 0,
      clauses_fired: [],
    };
    // ─────────────────────────────────────────────────────────────────────────

    // (a) Write output to Storage.
    const output_storage_path = `${org_id}/${id}/output.docx`;
    await uploadToStorage(
      engineResult.outputBuffer,
      output_storage_path,
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    );

    // (b) Update legal_jobs row.
    const { data: updated, error: updateErr } = await clientDb
      .from('legal_jobs')
      .update({
        output_storage_path,
        clause_count_adapted: engineResult.clause_count_adapted,
        status: 'complete',
        completed_at: new Date().toISOString(),
      })
      .eq('id', id)
      .select()
      .single();

    if (updateErr) throw updateErr;

    // (c) Fire-and-forget invocation log — never awaited in a way that blocks the response.
    logInvocation({
      org_id,
      corridor:                    job.corridor,
      sector:                      job.sector,
      document_type:               job.document_type,
      clauses_fired:               engineResult.clauses_fired,
      jurisdiction_config_version: job.jurisdiction_config_version,
      outcome:                     'adapted',
    });

    return res.json(updated);
  } catch (err) {
    next(err);
  }
});

// ── GET /legal-jobs ───────────────────────────────────────────────────────────

router.get('/', async (req, res, next) => {
  try {
    const { data, error } = await clientDb
      .from('legal_jobs')
      .select(
        // Deliberately exclude output_storage_path and origin_storage_path from list view.
        'id, org_id, corridor, origin_country, target_country, sector, document_type, ' +
        'assessment_id, jurisdiction_config_version, clause_count_adapted, ' +
        'status, created_at, completed_at',
      )
      .order('created_at', { ascending: false });

    if (error) throw error;

    return res.json(data);
  } catch (err) {
    next(err);
  }
});

// ── GET /legal-jobs/:id/download ──────────────────────────────────────────────

router.get('/:id/download', async (req, res, next) => {
  try {
    const { id } = req.params;
    const org_id = await getOrgId(req.user.id);
    if (!org_id) {
      return res.status(403).json({ error: 'User profile not found or no org assigned.' });
    }

    // Fetch job and verify ownership.
    const { data: job, error: fetchErr } = await clientDb
      .from('legal_jobs')
      .select('id, org_id, output_storage_path, status')
      .eq('id', id)
      .single();

    if (fetchErr?.code === 'PGRST116' || !job) {
      return res.status(404).json({ error: 'Legal job not found.' });
    }
    if (fetchErr) throw fetchErr;
    if (job.org_id !== org_id) {
      return res.status(403).json({ error: 'Access denied.' });
    }
    if (job.status !== 'complete' || !job.output_storage_path) {
      return res.status(409).json({ error: 'Output is not ready yet.' });
    }

    // Enforce that the storage path belongs to this org (defence-in-depth).
    if (!job.output_storage_path.startsWith(`${org_id}/`)) {
      return res.status(403).json({ error: 'Storage path org mismatch.' });
    }

    const { data: signedData, error: signErr } = await clientDb.storage
      .from('legal-documents')
      .createSignedUrl(job.output_storage_path, 3600); // 1-hour expiry

    if (signErr) throw signErr;

    return res.json({ signed_url: signedData.signedUrl });
  } catch (err) {
    next(err);
  }
});

export default router;
