// Global bootstrap hook pentru inițializarea aplicației
import { useState, useEffect } from 'react';
import { useOptionsStore } from '../stores/optionsStore';

export function useBootstrapApp(params = {}) {
  const [ready, setReady] = useState(false);
  const [initializing, setInitializing] = useState(false);
  
  // Access options store
  const { setPreviewItem } = useOptionsStore();
  
  useEffect(() => {
    if (ready || initializing) return;
    
    setInitializing(true);
    
    // Initialize application state
    const bootstrap = async () => {
      try {
        // Set default values if needed
        if (params.symbol) {
          // Future: set symbol in global store
          console.log('Bootstrap: setting symbol', params.symbol);
        }
        
        if (params.expiry) {
          // Future: set expiry in global store  
          console.log('Bootstrap: setting expiry', params.expiry);
        }
        
        // Initialize store if needed
        if (setPreviewItem) {
          // Store is available - ready to go
          setReady(true);
        } else {
          // Fallback - still mark as ready
          setTimeout(() => setReady(true), 100);
        }
        
      } catch (error) {
        console.error('Bootstrap failed:', error);
        // Still mark as ready to prevent infinite loading
        setReady(true);
      } finally {
        setInitializing(false);
      }
    };
    
    bootstrap();
  }, [ready, initializing, params.symbol, params.expiry, setPreviewItem]);
  
  return { ready, initializing };
}