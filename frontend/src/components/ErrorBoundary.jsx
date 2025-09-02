// ---------------------------
// ErrorBoundary.jsx (Safe Wrapper)
// ---------------------------
import React from "react";

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, err: null };
  }

  static getDerivedStateFromError(err) {
    return { hasError: true, err };
  }

  componentDidCatch(err, info) {
    console.error("Sidebar error:", err, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
          <div className="font-semibold">Sidebar crashed</div>
          <div className="text-xs mt-1">Check console for details</div>
          <button 
            onClick={() => this.setState({ hasError: false, err: null })}
            className="mt-2 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 rounded"
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}