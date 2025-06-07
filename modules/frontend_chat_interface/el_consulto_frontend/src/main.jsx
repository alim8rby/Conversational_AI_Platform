import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';   // ← your updated index styles
import './App.css';     // ← your updated app styles

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
