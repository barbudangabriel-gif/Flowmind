// Global bootstrap hook pentru inițializarea aplicației (fără UI blocking)
import { useState, useEffect } from 'react';
import { useOptionsStore } from '../stores/optionsStore';

let globalInitialized = false; // Prevent multiple initializations

export function useBootstrapApp(params = {}) {
 const [ready, setReady] = useState(globalInitialized); // Start ready if already initialized
 const [initializing, setInitializing] = useState(false);
 
 // Access options store
 const store = useOptionsStore();
 
 useEffect(() => {
 if (globalInitialized || initializing) {
 setReady(true);
 return;
 }
 
 console.log('useBootstrapApp: Starting initialization...', params);
 setInitializing(true);
 
 // Initialize application state (non-blocking)
 const bootstrap = async () => {
 try {
 // Initialize store if needed
 if (store && store.setPreviewItem) {
 console.log('Bootstrap: Store available, setting ready');
 globalInitialized = true;
 setReady(true);
 } else {
 // Fallback - still mark as ready after short delay
 console.log('Bootstrap: Store not ready, using fallback');
 setTimeout(() => {
 globalInitialized = true;
 setReady(true);
 }, 100);
 }
 
 } catch (error) {
 console.error('Bootstrap failed:', error);
 // Still mark as ready to prevent infinite loading
 globalInitialized = true;
 setReady(true);
 } finally {
 setInitializing(false);
 }
 };
 
 bootstrap();
 }, [initializing, store]);
 
 return { ready, initializing };
}