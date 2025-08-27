import { useTheme } from "../App";

export default function ThemeIconToggleGhost() {
  const { isDarkMode, toggleDarkMode } = useTheme();

  return (
    <button
      onClick={toggleDarkMode}
      className="p-1 hover:bg-gray-600 rounded-full transition-colors"
      title={`Switch to ${isDarkMode ? "light" : "dark"} mode`}
    >
      {isDarkMode ? (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-amber-400">
          <path d="M21 12.79A9 9 0 1 1 11.21 3c.2 0 .4.01.6.03A7 7 0 1 0 21 12.79z"/>
        </svg>
      ) : (
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="text-yellow-500">
          <path d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.8 1.42-1.42zM1 13h3v-2H1v2zm10 10h2v-3h-2v3zm9-10v-2h-3v2h3zm-3.95 7.95l1.79 1.8 1.41-1.41-1.8-1.79-1.4 1.4zM13 1h-2v3h2V1zm-7.95 3.05L3.05 5.1l1.8 1.79 1.41-1.41-1.79-1.8zM12 7a5 5 0 100 10 5 5 0 000-10z"/>
        </svg>
      )}
    </button>
  );
}