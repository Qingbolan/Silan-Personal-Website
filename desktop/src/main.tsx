import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { WorkspaceBootstrapGate } from './components/WorkspaceOnboarding';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <WorkspaceBootstrapGate>
      <App />
    </WorkspaceBootstrapGate>
  </React.StrictMode>,
);
