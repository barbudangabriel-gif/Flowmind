import ExpiryRail from "../ExpiryRail";
import { StrikeRailPro } from "../StrikeRailPro";

export default function RailsBar({ 
  symbol = '', 
  expiry = '', 
  onExpiry = () => {}, 
  chain = [], 
  onStrike = () => {},
  expirations = []
}) {
  return (
    <div className="space-y-3 py-3">
      {/* Expiry Rail */}
      <div data-testid="expiry-rail">
        <div className="text-xs text-slate-400 mb-2 uppercase tracking-wide">
          Expiration • {expirations.length} available
        </div>
        <ExpiryRail 
          variant="builder" 
          expirations={expirations}
          value={expiry} 
          onChange={onExpiry} 
        />
      </div>

      {/* Strike Rail */}
      <div data-testid="strike-rail-pro">
        <div className="text-xs text-slate-400 mb-2 uppercase tracking-wide">
          Strike Prices • {chain?.length || 0} strikes
        </div>
        <StrikeRailPro 
          chain={chain} 
          onPick={onStrike}
        />
      </div>
    </div>
  );
}