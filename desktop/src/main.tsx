import React from 'react';
import ReactDOM from 'react-dom/client';
import '@fontsource-variable/inter';
import App from './App';
import { StartupExperience } from './components/StartupExperience';
import { WorkspaceBootstrapGate } from './components/WorkspaceOnboarding';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <StartupExperience>
      <WorkspaceBootstrapGate>
        <App />
      </WorkspaceBootstrapGate>
    </StartupExperience>
  </React.StrictMode>,
);
