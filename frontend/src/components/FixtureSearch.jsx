import React, { useRef, useState } from 'react';
import { searchTeams, getTeamFixtures, getFixtureSquads, uploadSquadCsv } from '../api';

export default function FixtureSearch({ onSelectFixtureSquad, onManualSquad }) {
  const [query, setQuery] = useState('');
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [fixtures, setFixtures] = useState([]);
  const [searching, setSearching] = useState(false);
  const [loadingFixtures, setLoadingFixtures] = useState(false);
  const [loadingFixtureId, setLoadingFixtureId] = useState(null);
  const [error, setError] = useState(null);

  const debounceRef = useRef(null);
  const fileInputRef = useRef(null);

  const handleQueryChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    setError(null);
    clearTimeout(debounceRef.current);

    if (value.trim().length < 2) {
      setTeams([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setSearching(true);
      try {
        const results = await searchTeams(value.trim());
        setTeams(results);
      } catch (err) {
        setError(err.message);
      } finally {
        setSearching(false);
      }
    }, 350);
  };

  const handlePickTeam = async (team) => {
    setSelectedTeam(team);
    setFixtures([]);
    setLoadingFixtures(true);
    setError(null);
    try {
      const results = await getTeamFixtures(team.id);
      setFixtures(results);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingFixtures(false);
    }
  };

  const handlePickFixture = async (fixture) => {
    setLoadingFixtureId(fixture.fixture_id);
    setError(null);
    try {
      const { data, synced_at } = await getFixtureSquads(fixture.fixture_id);
      if (!data.length) {
        setError('No lineup or squad data available for this fixture yet — try another, or upload a CSV.');
        return;
      }
      onSelectFixtureSquad(
        {
          fixtureId: fixture.fixture_id,
          homeTeam: fixture.home_team,
          awayTeam: fixture.away_team,
          date: fixture.date,
        },
        data,
        synced_at
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingFixtureId(null);
    }
  };

  const handleManualFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setError(null);
    try {
      const { data } = await uploadSquadCsv(file);
      onManualSquad(data);
    } catch (err) {
      setError(err.message);
    } finally {
      e.target.value = '';
    }
  };

  const formatDate = (iso) => {
    const d = new Date(iso);
    return {
      weekday: d.toLocaleDateString(undefined, { weekday: 'short' }).toUpperCase(),
      day: d.toLocaleDateString(undefined, { day: '2-digit', month: 'short' }).toUpperCase(),
    };
  };

  return (
    <section className="screen active">
      <div className="eyebrow">Squad source</div>
      <h2 className="title">Find your match</h2>
      <p className="subtitle">
        Search by team. We&rsquo;ll pull the confirmed lineup straight from API-Football — no manual typing.
      </p>

      <div className="search-row">
        <div className="search-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Search team, e.g. Arsenal"
            value={query}
            onChange={handleQueryChange}
          />
        </div>
        <span className="api-tag">⚡ API-FOOTBALL</span>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {searching && <div className="hint-text">Searching…</div>}

      {!selectedTeam && teams.length > 0 && (
        <>
          <div className="section-label">Teams</div>
          <div className="fixture-list">
            {teams.map((team) => (
              <div className="fixture" key={team.id}>
                <div className="crest">
                  {team.logo ? (
                    <img src={team.logo} alt="" width="22" height="22" />
                  ) : (
                    team.name.slice(0, 3).toUpperCase()
                  )}
                </div>
                <div className="matchup">
                  <div className="team-name">{team.name}</div>
                </div>
                <button className="pick" onClick={() => handlePickTeam(team)}>
                  Select
                </button>
              </div>
            ))}
          </div>
        </>
      )}

      {selectedTeam && (
        <>
          <div className="section-label">
            Fixtures · {selectedTeam.name}{' '}
            <button
              className="text-btn"
              onClick={() => {
                setSelectedTeam(null);
                setFixtures([]);
              }}
            >
              change team
            </button>
          </div>

          {loadingFixtures && <div className="hint-text">Loading fixtures…</div>}

          <div className="fixture-list">
            {fixtures.map((fx) => {
              const { weekday, day } = formatDate(fx.date);
              return (
                <div className="fixture" key={fx.fixture_id}>
                  <div className="date">
                    {weekday}
                    <br />
                    <b>{day}</b>
                  </div>
                  <div className="matchup">
                    <div className="team-name">{fx.home_team}</div>
                    <span className="vs">vs</span>
                    <div className="team-name">{fx.away_team}</div>
                  </div>
                  <button
                    className="pick"
                    onClick={() => handlePickFixture(fx)}
                    disabled={loadingFixtureId === fx.fixture_id}
                  >
                    {loadingFixtureId === fx.fixture_id ? 'Loading…' : 'Select'}
                  </button>
                </div>
              );
            })}
            {!loadingFixtures && fixtures.length === 0 && (
              <div className="fixture muted">No recent fixtures found for this team.</div>
            )}
          </div>
        </>
      )}

      <div className="manual-fallback">
        <div className="txt">
          <b>Can&rsquo;t find your match?</b>
          Upload a squad list manually as a CSV instead.
        </div>
        <button className="ghost-btn" onClick={() => fileInputRef.current?.click()}>
          Upload CSV
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleManualFile}
        />
      </div>
    </section>
  );
}