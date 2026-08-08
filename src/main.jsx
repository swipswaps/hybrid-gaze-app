import React, { Component } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null, errorInfo: null }; }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, errorInfo) {
    console.error("[RUNTIME_ERROR_FLAG]:", error, errorInfo);
    this.setState({ errorInfo });
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '30px', background: '#310', color: '#ff8888', fontFamily: 'monospace' }}>
          <h3>[CRITICAL ROUTE BLOCKER CAUGHT]</h3>
          <p>{this.state.error && this.state.error.toString()}</p>
          <pre>{this.state.errorInfo && this.state.errorInfo.componentStack}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

export const dbManager = {
  dbName: "HybridGazeLocalDB",
  storeName: "telemetry_logs",
  open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);
      request.onerror = () => { console.error("[DB_READ_WRITE_ERROR]:", request.error); reject(request.error); };
      request.onsuccess = () => resolve(request.result);
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: "id", autoIncrement: true });
        }
      };
    });
  },
  async writeLog(payload) {
    try {
      const db = await this.open();
      const transaction = db.transaction(this.storeName, "readwrite");
      const store = transaction.objectStore(this.storeName);
      store.add({ timestamp: Date.now(), ...payload });
    } catch (e) {
      console.error("[DB_WRITE_BLOCKER]:", e);
    }
  }
};

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
