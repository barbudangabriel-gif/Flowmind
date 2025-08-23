import React, { useState, useEffect, Suspense, useMemo } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
// ... existing imports remain ...

// within component where navigate is used in sidebar
// helper to fallback to hard navigation if client routing fails
function navigateWithFallback(navigate, route) {
  try { navigate(route); } catch (e) { /* ignore */ }
  setTimeout(() => {
    try {
      if (window && window.location && window.location.pathname !== route) {
        window.location.assign(route);
      }
    } catch (e) { /* ignore */ }
  }, 300);
}

// ... rest of App.js, ensure to replace navigate(item.route) with navigateWithFallback(navigate, item.route)