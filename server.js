/*
 Node Gateway Stub for TripGenie
 - Proxies frontend requests to Python FastAPI microservice
 - Enforces single in-flight itinerary generation (queue size 1)
 - Provides health aggregation
*/

const express = require('express');
const axios = require('axios');
const cors = require('cors');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const PORT = process.env.PORT || 3000;
const PY_BACKEND_URL = process.env.PY_BACKEND_URL || 'http://localhost:8000';

// Single-flight control
let inProgress = false;

app.get('/', (req, res) => {
  res.json({
    message: 'TripGenie Node Gateway',
    python_backend: PY_BACKEND_URL,
    single_request_locked: inProgress
  });
});

app.get('/health', async (req, res) => {
  try {
    const py = await axios.get(`${PY_BACKEND_URL}/health`);
    res.json({ gateway: 'ok', python: py.data });
  } catch (e) {
    res.status(500).json({ gateway: 'ok', python_error: e.message });
  }
});

app.post('/api/generate-itinerary', async (req, res) => {
  if (inProgress) {
    return res.status(429).json({ success: false, error: 'Another request is currently being processed' });
  }
  inProgress = true;
  try {
    const response = await axios.post(`${PY_BACKEND_URL}/api/generate-itinerary`, req.body, { timeout: 120000 });
    res.json(response.data);
  } catch (e) {
    if (e.response) {
      res.status(e.response.status).json(e.response.data);
    } else {
      res.status(500).json({ success: false, error: e.message });
    }
  } finally {
    inProgress = false;
  }
});

// Pass-through endpoints for autocomplete, interests, location validation
app.get('/api/interests', async (req, res) => {
  try {
    const r = await axios.get(`${PY_BACKEND_URL}/api/interests`);
    res.json(r.data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/autocomplete-location', async (req, res) => {
  const { query } = req.query;
  try {
    const r = await axios.get(`${PY_BACKEND_URL}/api/autocomplete-location`, { params: { query } });
    res.json(r.data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/validate-location', async (req, res) => {
  const { location } = req.body;
  try {
    const r = await axios.post(`${PY_BACKEND_URL}/api/validate-location`, null, { params: { location } });
    res.json(r.data);
  } catch (e) {
    res.status(e.response?.status || 500).json({ error: e.message });
  }
});

// Basic error handler
app.use((err, req, res, next) => {
  console.error('Unhandled gateway error:', err);
  res.status(500).json({ success: false, error: 'Gateway internal error' });
});

app.listen(PORT, () => {
  console.log(`TripGenie Node Gateway running on port ${PORT}`);
});
