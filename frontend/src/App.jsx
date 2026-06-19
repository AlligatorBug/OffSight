import React, { useEffect, useReducer, useState } from 'react';
import Navbar from './components/Navbar';
import Stepper from './components/Stepper';
import FixtureSearch from './components/FixtureSearch';
import SquadConfirm from './components/SquadConfirm';
import UploadZone from './components/UploadZone';
import LiveTracking from './components/LiveTracking';
import useTrackingSocket from './hooks/useTrackingSocket';
import { getVideoDimensions } from './utils/video';
import { classifyLabel } from './utils/classify';

const initialState = {
  step: 1,
  fixture: null, // { fixtureId, homeTeam, awayTeam, date } | null when squad is manual
  squad: [], // [{ number, name, side }]
  squadSource: null, // 'api' | 'manual'
  squadSyncedAt: null,
  videoFile: null,
  videoDims: null,
};

function reducer(state, action) {
  switch (action.type) {
    case 'GO_TO_STEP':
      return { ...state, step: action.step };
    case 'SET_SQUAD_SOURCE':
      return {
        ...state,
        step: 2,
        fixture: action.fixture,
        squad: action.squad,
        squadSource: action.source,
        squadSyncedAt: action.syncedAt,
      };
    case 'UPDATE_SQUAD':
      return { ...state, squad: action.squad };
    case 'CONFIRM_VIDEO':
      return { ...state, videoFile: action.file, videoDims: action.dims };
    case 'START_PROCESSING':
      return { ...state, step: 4 };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const [roster, setRoster] = useState({}); // { [trackerId]: { label, type } }
  const socket = useTrackingSocket();

  // Accumulate a running roster across every frame seen so far, so a player
  // who's identified once and then briefly occluded doesn't drop out of the
  // list — only the live overlay reflects the current frame's detections.
  useEffect(() => {
    if (!socket.detections || socket.detections.length === 0) return;
    setRoster((prev) => {
      const next = { ...prev };
      socket.detections.forEach((d) => {
        next[d.tracker_id] = { label: d.label, type: classifyLabel(d.label) };
      });
      return next;
    });
  }, [socket.detections]);

  const handleFixtureSquad = (fixture, squadData, syncedAt) => {
    dispatch({ type: 'SET_SQUAD_SOURCE', fixture, squad: squadData, source: 'api', syncedAt });
  };

  const handleManualSquad = (squadData) => {
    dispatch({ type: 'SET_SQUAD_SOURCE', fixture: null, squad: squadData, source: 'manual', syncedAt: null });
  };

  const handleSquadEdit = (squad) => dispatch({ type: 'UPDATE_SQUAD', squad });

  const handleSquadConfirm = () => dispatch({ type: 'GO_TO_STEP', step: 3 });

  const handleVideoChosen = async (file) => {
    const dims = await getVideoDimensions(file).catch(() => null);
    dispatch({ type: 'CONFIRM_VIDEO', file, dims });
  };

  const handleStartProcessing = () => {
    setRoster({});
    dispatch({ type: 'START_PROCESSING' });
    // Always send the resolved + user-confirmed squad, never a raw fixture_id —
    // this way edits made in step 2 are respected rather than silently
    // discarded by a server-side re-fetch.
    socket.start({ squad: state.squad }, state.videoFile);
  };

  const rosterList = Object.entries(roster).map(([trackerId, v]) => ({
    trackerId: Number(trackerId),
    ...v,
  }));

  return (
    <div className="app">
      <Navbar connected={socket.status !== 'idle' && socket.status !== 'error'} />
      <Stepper currentStep={state.step} />

      {state.step === 1 && (
        <FixtureSearch onSelectFixtureSquad={handleFixtureSquad} onManualSquad={handleManualSquad} />
      )}

      {state.step === 2 && (
        <SquadConfirm
          fixture={state.fixture}
          squad={state.squad}
          source={state.squadSource}
          syncedAt={state.squadSyncedAt}
          onChange={handleSquadEdit}
          onBack={() => dispatch({ type: 'GO_TO_STEP', step: 1 })}
          onConfirm={handleSquadConfirm}
        />
      )}

      {state.step === 3 && (
        <UploadZone
          linkedLabel={
            state.fixture
              ? `${state.fixture.homeTeam} vs ${state.fixture.awayTeam} (${state.squad.length} players)`
              : `Manual squad (${state.squad.length} players)`
          }
          onFileChosen={handleVideoChosen}
          onBack={() => dispatch({ type: 'GO_TO_STEP', step: 2 })}
          onStart={handleStartProcessing}
          canStart={!!state.videoFile}
        />
      )}

      {state.step === 4 && (
        <LiveTracking
          matchLabel={state.fixture ? `${state.fixture.homeTeam} vs ${state.fixture.awayTeam}` : 'Match footage'}
          videoFile={state.videoFile}
          videoDims={state.videoDims}
          status={socket.status}
          message={socket.message}
          frame={socket.frame}
          total={socket.total}
          detections={socket.detections}
          roster={rosterList}
          resultUrl={socket.resultUrl}
          error={socket.error}
        />
      )}
    </div>
  );
}
