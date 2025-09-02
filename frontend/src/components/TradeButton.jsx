// components/TradeButton.jsx
import React from 'react';
import { STANCE_THEME, intensify } from '../ui/stance';

export function TradeButton({
  stance, 
  strength = 'normal', 
  disabled = false, 
  onClick
}) {
  const theme = STANCE_THEME[stance];
  
  return (
    <button
      className={`px-4 py-2 rounded-xl font-semibold ${intensify(theme.btn, strength)} ${theme.ring} transition disabled:opacity-50 disabled:cursor-not-allowed`}
      disabled={disabled}
      onClick={onClick}
      title={`Trade (${stance}${strength === 'very' ? ' • VERY' : ''})`}
    >
      <span className="mr-2">{theme.icon}</span>
      TRADE
    </button>
  );
}

export default TradeButton;