/**
 * API Client for FastAPI Healthcare Interoperability Platform Backend
 */

export const API = {
  async get(endpoint) {
    const res = await fetch(endpoint);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }
    return res.json();
  },

  async post(endpoint, data) {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }
    return res.json();
  },

  async delete(endpoint) {
    const res = await fetch(endpoint, { method: "DELETE" });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Request failed (${res.status})`);
    }
    return res.json();
  },

  async uploadFile(endpoint, formData) {
    const res = await fetch(endpoint, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Upload failed (${res.status})`);
    }
    return res.json();
  },

  // Specific API calls
  getDashboardStats() {
    return this.get("/api/dashboard/stats");
  },

  getHealth() {
    return this.get("/api/health");
  },

  getProjects() {
    return this.get("/api/projects");
  },

  createProject(data) {
    return this.post("/api/projects", data);
  },

  deleteProject(projectId) {
    return this.delete(`/api/projects/${projectId}`);
  },

  getDatabases(projectId) {
    const q = projectId ? `?project_id=${projectId}` : "";
    return this.get(`/api/databases${q}`);
  },

  getDatabase(id) {
    return this.get(`/api/databases/${id}`);
  },

  uploadDatabase(file, projectId) {
    const formData = new FormData();
    formData.append("file", file);
    if (projectId) formData.append("project_id", projectId);
    return this.uploadFile("/api/databases/upload", formData);
  },

  getAnalysisRuns(projectId) {
    const q = projectId ? `?project_id=${projectId}` : "";
    return this.get(`/api/analysis/runs${q}`);
  },

  startAnalysis(data) {
    return this.post("/api/analysis/start", data);
  },

  getMappings(params = {}) {
    const q = new URLSearchParams(params).toString();
    return this.get(`/api/mappings${q ? "?" + q : ""}`);
  },

  getMappingDetail(id) {
    return this.get(`/api/mappings/${id}`);
  },

  getReviewQueue(projectId) {
    const q = projectId ? `?project_id=${projectId}` : "";
    return this.get(`/api/reviews/queue${q}`);
  },

  submitReview(data) {
    return this.post("/api/reviews", data);
  },

  getReports() {
    return this.get("/api/reports");
  },

  getReportContent(filename) {
    return fetch(`/api/reports/${filename}`).then((r) => r.text());
  },

  getEvaluationCharts() {
    return this.get("/api/reports/evaluation/charts");
  },

  getEvaluationSummary() {
    return this.get("/api/reports/evaluation/summary");
  },

  getResources() {
    return this.get("/api/resources");
  },

  getAuditEvents(projectId, limit = 50) {
    const q = projectId ? `?project_id=${projectId}&limit=${limit}` : `?limit=${limit}`;
    return this.get(`/api/audit${q}`);
  },
};
