export default function BrandMark({ size = 34 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="goldGrad" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#f4d77a" />
          <stop offset="50%" stopColor="#d4af37" />
          <stop offset="100%" stopColor="#a07920" />
        </linearGradient>
      </defs>
      <circle
        cx="24"
        cy="24"
        r="22"
        stroke="url(#goldGrad)"
        strokeWidth="0.8"
        fill="none"
      />
      <circle
        cx="24"
        cy="24"
        r="16"
        stroke="url(#goldGrad)"
        strokeWidth="0.5"
        fill="none"
      />
      <polygon
        points="24,8 38,32 10,32"
        stroke="url(#goldGrad)"
        strokeWidth="0.8"
        fill="none"
      />
      <polygon
        points="24,40 10,16 38,16"
        stroke="url(#goldGrad)"
        strokeWidth="0.8"
        fill="none"
      />
      <circle cx="24" cy="24" r="2.5" fill="url(#goldGrad)" />
    </svg>
  );
}
