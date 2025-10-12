export default function FISSkeleton({ width = 80, height = 24 }) {
  return (
    <span style={{
      display: "inline-block",
      width,
      height,
      borderRadius: 999,
      background: "linear-gradient(90deg,#f3f3f3 25%,#e0e0e0 50%,#f3f3f3 75%)",
      backgroundSize: "200% 100%",
      animation: "skeleton 1.2s infinite linear"
    }} />
  );
}
