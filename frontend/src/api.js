const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — fall back to statusText
    }
    throw new Error(detail);
  }

  return res.json();
}

export function searchTeams(query) {
  return request(`/api/teams/search?q=${encodeURIComponent(query)}`);
}

export function getTeamFixtures(teamId) {
  return request(`/api/teams/${teamId}/fixtures`);
}

export function getFixtureSquads(fixtureId) {
  return request(`/api/fixtures/${fixtureId}/squads`);
}

export async function uploadSquadCsv(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request('/api/squads/manual', { method: 'POST', body: formData });
}