import React, { useEffect, useRef, useState } from "react";

export default function Tooltip({ content, children, delay = 120 }) {
  const [open, setOpen] = useState(false);
  const tRef = useRef(null);
  const wrapRef = useRef(null);

  const show = () => {
    clearTimeout(tRef.current);
    tRef.current = setTimeout(() => setOpen(true), delay);
  };
  const hide = () => {
    clearTimeout(tRef.current);
    setOpen(false);
  };

  useEffect(() => () => clearTimeout(tRef.current), []);

  return (
    <span
      ref={wrapRef}
      style={{ position:"relative", display:"inline-flex", alignItems:"center" }}
      onMouseEnter={show}
      onMouseLeave={hide}
      onFocus={show}
      onBlur={hide}
      tabIndex={0}
      role="button"
      aria-haspopup="dialog"
      aria-expanded={open}
    >
      {children}
      {open && (
        <span
          role="dialog"
          style={{
            position:"absolute", top:"120%", right:0, zIndex:50,
            background:"var(--tooltip-bg, #111827)", color:"var(--tooltip-fg, #fff)",
            padding:"8px 10px", borderRadius:8, fontSize:12, minWidth:180,
            boxShadow:"0 6px 20px rgba(0,0,0,.25)"
          }}
        >
          {content}
          <span style={{
            position:"absolute", top:-6, right:12, width:0, height:0,
            borderLeft:"6px solid transparent", borderRight:"6px solid transparent",
            borderBottom:"6px solid var(--tooltip-bg, #111827)"
          }}/>
        </span>
      )}
    </span>
  );
}
