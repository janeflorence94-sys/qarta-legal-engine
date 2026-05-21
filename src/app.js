import express from 'express';
import cors from 'cors';
import assessmentRoutes from './routes/assessments.js';
import legalJobRoutes from './routes/legalJobs.js';

const app = express();
const PORT = process.env.PORT || 3000;

// ── CORS ──────────────────────────────────────────────────────────────────────

const corsOptions = {
  origin: [
    'https://www.qartaintelligence.com',
    'https://qartaintelligence.com',
    'http://localhost:5173',
  ],
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
};

app.use(cors(corsOptions));
app.options('*', cors(corsOptions)); // handle preflight for all routes

// ── Global middleware ─────────────────────────────────────────────────────────

app.use(express.json());

// ── Health check (no auth) ────────────────────────────────────────────────────

app.get('/health', (_req, res) => {
  res.status(200).json({ status: 'ok', service: 'qarta-intelligence-api' });
});

// ── API routes ────────────────────────────────────────────────────────────────

// requireAuth is applied inside each router, so every route under these mounts
// is automatically protected. Nothing tenant-facing is reachable without a valid JWT.
app.use('/assessments', assessmentRoutes);
app.use('/legal-jobs',  legalJobRoutes);

// ── 404 for unknown routes ────────────────────────────────────────────────────

app.use((_req, res) => {
  res.status(404).json({ error: 'Route not found.' });
});

// ── Global error handler ──────────────────────────────────────────────────────

// eslint-disable-next-line no-unused-vars
app.use((err, _req, res, _next) => {
  console.error('[error]', err.message, err.stack);
  const status = err.status ?? err.statusCode ?? 500;
  res.status(status).json({
    error: status < 500 ? err.message : 'Internal server error.',
  });
});

// ── Start ─────────────────────────────────────────────────────────────────────

app.listen(PORT, () => {
  console.log(`Qarta Intelligence API listening on port ${PORT}`);
});

export default app;
