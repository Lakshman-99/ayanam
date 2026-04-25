import { brand } from "@/lib/config/brand";
import { cn } from "@/lib/utils";

interface BrandMarkProps {
  size?: number;
  className?: string;
  showWordmark?: boolean;
}

/**
 * Placeholder brand mark — a stylized 8-pointed star (common in Indian
 * sacred geometry) inside a circle. Easy to swap for a real logo later
 * by replacing the SVG content; the API stays the same.
 */
export function BrandMark({ size = 32, className, showWordmark = false }: BrandMarkProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label={brand.name}
      >
        <circle cx="16" cy="16" r="15" className="fill-indigo-950" />
        <g className="stroke-amber-400" strokeWidth="1.2" strokeLinecap="round">
          <line x1="16" y1="5" x2="16" y2="27" />
          <line x1="5" y1="16" x2="27" y2="16" />
          <line x1="8" y1="8" x2="24" y2="24" />
          <line x1="24" y1="8" x2="8" y2="24" />
        </g>
        <circle cx="16" cy="16" r="2" className="fill-amber-400" />
      </svg>
      {showWordmark && (
        <span className="font-semibold tracking-tight text-slate-900">{brand.name}</span>
      )}
    </div>
  );
}