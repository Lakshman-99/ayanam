"use client";

const STAR_SEED = Array.from({ length: 60 }).map(() => ({
  x: Math.random() * 100,
  y: Math.random() * 100,
  s: Math.random() * 1.5 + 0.3,
  d: Math.random() * 4,
}));

export default function Starfield() {
  return (
    <div
      className="absolute inset-0 pointer-events-none overflow-hidden"
      aria-hidden="true"
    >
      {STAR_SEED.map((star, index) => (
        <div
          key={index}
          className="absolute rounded-full bg-amber-200"
          style={{
            left: `${star.x}%`,
            top: `${star.y}%`,
            width: `${star.s}px`,
            height: `${star.s}px`,
            opacity: 0.4,
            animation: `twinkle 3s ease-in-out ${star.d}s infinite`,
          }}
        />
      ))}
    </div>
  );
}
