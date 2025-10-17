/**
 * Unusual Whales Inspired Theme - Tailwind Configuration
 * 
 * Color Palette extracted from unusualwhales.com
 * Dark blue-black theme optimized for trading/finance applications
 */

module.exports = {
 theme: {
 extend: {
 colors: {
 // Unusual Whales Primary Palette
 uw: {
 // Backgrounds (blue-black gradient)
 'bg-darkest': '#0a0e1a', // Almost black with blue tint
 'bg-darker': '#0f1419', // Very dark blue-black
 'bg-dark': '#151922', // Dark blue
 'bg-medium': '#1a1f2e', // Medium dark blue
 'bg-card': '#1e2430', // Card background
 'bg-elevated': '#242b3d', // Elevated elements
 
 // Accents
 'blue': '#3b82f6', // Primary blue (CTAs)
 'blue-light': '#60a5fa', // Lighter blue (hover)
 'blue-dark': '#2563eb', // Darker blue (active)
 
 // Success/Bull
 'success': '#10b981', // Emerald green
 'success-light': '#34d399', // Light green
 'teal': '#14b8a6', // Teal accent
 
 // Danger/Bear
 'danger': '#ef4444', // Red
 'danger-light': '#f87171', // Light red
 'pink': '#f43f5e', // Pink accent
 
 // Text
 'text-primary': '#ffffff', // White
 'text-secondary': '#cbd5e1', // Light grey-blue
 'text-muted': '#94a3b8', // Muted grey-blue
 'text-disabled': '#64748b', // Disabled grey
 
 // Borders
 'border-subtle': '#1e293b', // Very subtle border
 'border': '#334155', // Standard border
 'border-strong': '#475569', // Strong border
 }
 },
 
 // UW-specific shadows
 boxShadow: {
 'uw-sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
 'uw': '0 2px 8px 0 rgba(0, 0, 0, 0.4)',
 'uw-md': '0 4px 12px 0 rgba(0, 0, 0, 0.5)',
 'uw-lg': '0 8px 24px 0 rgba(0, 0, 0, 0.6)',
 'uw-xl': '0 12px 32px 0 rgba(0, 0, 0, 0.7)',
 },
 
 // UW-specific border radius
 borderRadius: {
 'uw-sm': '6px',
 'uw': '8px',
 'uw-md': '10px',
 'uw-lg': '12px',
 },
 
 // Dense spacing for trading layouts
 spacing: {
 '18': '4.5rem', // 72px
 '22': '5.5rem', // 88px
 }
 }
 }
};

/**
 * USAGE EXAMPLES:
 * 
 * Background:
 * bg-uw-bg-darkest → Main app background
 * bg-uw-bg-dark → Sidebar background
 * bg-uw-bg-card → Card background
 * 
 * Text:
 * text-uw-text-primary → White text
 * text-uw-text-secondary → Grey-blue text
 * text-uw-text-muted → Subtle text
 * 
 * Accents:
 * bg-uw-blue → Primary blue buttons
 * text-uw-success → Bull/positive numbers
 * text-uw-danger → Bear/negative numbers
 * 
 * Borders:
 * border-uw-border-subtle → Very subtle borders
 * border-uw-border → Standard borders
 * 
 * Shadows:
 * shadow-uw → Standard card shadow
 * shadow-uw-lg → Elevated elements
 */
