import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    {/* ✅ THIS WRAPPER IS REQUIRED FOR useNavigate() TO WORK */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
);