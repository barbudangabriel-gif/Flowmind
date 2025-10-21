import { useState, useEffect } from 'react';

const useMindfolioManagement = () => {
 const [mindfolios, setMindfolios] = useState([]);
 const [positions, setPositions] = useState([]);
 const [availableMindfolios, setAvailableMindfolios] = useState([]);
 const [loading, setLoading] = useState(false);
 const [error, setError] = useState(null);

 const backendUrl = process.env.REACT_APP_BACKEND_URL;

 // Fetch all mindfolios
 const fetchMindfolios = async () => {
 try {
 setLoading(true);
 const response = await fetch(`${backendUrl}/api/mindfolio-management/mindfolios`);
 const data = await response.json();
 
 if (data.status === 'success') {
 setMindfolios(data.mindfolios);
 } else {
 throw new Error('Failed to fetch mindfolios');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error fetching mindfolios:', err);
 } finally {
 setLoading(false);
 }
 };

 // Fetch positions for a specific mindfolio
 const fetchMindfolioPositions = async (mindfolioId) => {
 try {
 setLoading(true);
 const response = await fetch(`${backendUrl}/api/mindfolio-management/mindfolios/${mindfolioId}/positions`);
 const data = await response.json();
 
 if (data.status === 'success') {
 setPositions(data.positions);
 return data.positions;
 } else {
 throw new Error('Failed to fetch positions');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error fetching positions:', err);
 return [];
 } finally {
 setLoading(false);
 }
 };

 // Fetch available mindfolios for moving (excluding current mindfolio)
 const fetchAvailableMindfolios = async (currentMindfolioId) => {
 try {
 const response = await fetch(`${backendUrl}/api/mindfolio-management/available-mindfolios/${currentMindfolioId}`);
 const data = await response.json();
 
 if (data.status === 'success') {
 setAvailableMindfolios(data.available_mindfolios);
 return data.available_mindfolios;
 } else {
 throw new Error('Failed to fetch available mindfolios');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error fetching available mindfolios:', err);
 return [];
 }
 };

 // Move a position to another mindfolio
 const movePosition = async (positionId, toMindfolioId, quantityToMove = null, reason = "Manual move via context menu") => {
 try {
 setLoading(true);
 const response = await fetch(`${backendUrl}/api/mindfolio-management/move-position`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({
 position_id: positionId,
 to_mindfolio_id: toMindfolioId,
 quantity_to_move: quantityToMove,
 reason: reason
 })
 });

 const data = await response.json();
 
 if (data.status === 'success') {
 // Refresh positions after successful move
 return data.result;
 } else {
 throw new Error(data.result?.error || 'Failed to move position');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error moving position:', err);
 throw err;
 } finally {
 setLoading(false);
 }
 };

 // Create a new custom mindfolio
 const createMindfolio = async (name, description = "", category = "custom") => {
 try {
 setLoading(true);
 const response = await fetch(`${backendUrl}/api/mindfolio-management/create-mindfolio`, {
 method: 'POST',
 headers: {
 'Content-Type': 'application/json',
 },
 body: JSON.stringify({
 name,
 description,
 category
 })
 });

 const data = await response.json();
 
 if (data.status === 'success') {
 // Refresh mindfolios after creation
 await fetchMindfolios();
 return data.mindfolio;
 } else {
 throw new Error('Failed to create mindfolio');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error creating mindfolio:', err);
 throw err;
 } finally {
 setLoading(false);
 }
 };

 // Get aggregate view of all mindfolios
 const fetchAggregateView = async () => {
 try {
 const response = await fetch(`${backendUrl}/api/mindfolio-management/aggregate-view`);
 const data = await response.json();
 
 if (data.status === 'success') {
 return data.aggregate_data;
 } else {
 throw new Error('Failed to fetch aggregate view');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error fetching aggregate view:', err);
 return null;
 }
 };

 // Get move history for a mindfolio
 const fetchMoveHistory = async (mindfolioId) => {
 try {
 const response = await fetch(`${backendUrl}/api/mindfolio-management/move-history/${mindfolioId}`);
 const data = await response.json();
 
 if (data.status === 'success') {
 return data.move_history;
 } else {
 throw new Error('Failed to fetch move history');
 }
 } catch (err) {
 setError(err.message);
 console.error('Error fetching move history:', err);
 return [];
 }
 };

 // Initialize mindfolios on mount
 useEffect(() => {
 fetchMindfolios();
 }, []);

 return {
 // State
 mindfolios,
 positions,
 availableMindfolios,
 loading,
 error,
 
 // Actions
 fetchMindfolios,
 fetchMindfolioPositions,
 fetchAvailableMindfolios,
 movePosition,
 createMindfolio,
 fetchAggregateView,
 fetchMoveHistory,
 
 // Utilities
 clearError: () => setError(null)
 };
};

export default useMindfolioManagement;