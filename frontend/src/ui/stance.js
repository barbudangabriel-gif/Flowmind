// ui/stance.js
export const STANCE_THEME = {
 bullish: { 
 btn: 'bg-red-600 hover:bg-red-500 text-[rgb(252, 251, 255)]', 
 ring: 'ring-red-400/40', 
 icon: '▲' 
 },
 bearish: { 
 btn: 'bg-green-600 hover:bg-green-500 text-[rgb(252, 251, 255)]', 
 ring: 'ring-green-400/40', 
 icon: '▼' 
 },
 neutral: { 
 btn: 'bg-gray-600 hover:bg-gray-500 text-[rgb(252, 251, 255)]', 
 ring: 'ring-gray-400/40', 
 icon: '→' 
 },
 directional: { 
 btn: 'bg-fuchsia-600 hover:bg-fuchsia-500 text-[rgb(252, 251, 255)]', 
 ring: 'ring-fuchsia-400/40', 
 icon: '⇄' 
 },
};

export function intensify(clz, strength) {
 // „Very" = inel mai pronunțat + shadow
 return strength === 'very'
 ? `${clz} ring-4 shadow-lg`
 : `${clz} ring-2`;
}