import Image from "next/image";

const zodiacGlyphs = {
  Aries: "\u2648",
  Taurus: "\u2649",
  Gemini: "\u264A",
  Cancer: "\u264B",
  Leo: "\u264C",
  Virgo: "\u264D",
  Libra: "\u264E",
  Scorpio: "\u264F",
  Sagittarius: "\u2650",
  Capricorn: "\u2651",
  Aquarius: "\u2652",
  Pisces: "\u2653",
};

const planetGlyphs = {
  Sun: "\u2609",
  Moon: "\u263D",
  Mars: "\u2642",
  Mercury: "\u263F",
  Jupiter: "\u2643",
  Venus: "\u2640",
  Saturn: "\u2644",
  Rahu: "\u260A",
  Ketu: "\u260B",
};

const zodiacToneMap = {
  Aries: "--z-aries",
  Taurus: "--z-taurus",
  Gemini: "--z-gemini",
  Cancer: "--z-cancer",
  Leo: "--z-leo",
  Virgo: "--z-virgo",
  Libra: "--z-libra",
  Scorpio: "--z-scorpio",
  Sagittarius: "--z-sagittarius",
  Capricorn: "--z-capricorn",
  Aquarius: "--z-aquarius",
  Pisces: "--z-pisces",
};

export function ZodiacSymbol({ sign, size = 28 }) {
  const key = String(sign || "").trim();
  const src = `/zodiac/${key.toLowerCase()}.svg`;
  const glyph = zodiacGlyphs[key] || "?";
  const toneVar = zodiacToneMap[key] || "--color-gold";
  const innerSize = Math.max(size - 10, 12);

  if (zodiacGlyphs[key]) {
    return (
      <div
        style={{
          width: size,
          height: size,
          borderColor: `color-mix(in srgb, var(${toneVar}) 55%, var(--line-bright))`,
          background:
            `radial-gradient(circle at 28% 26%, color-mix(in srgb, var(${toneVar}) 26%, transparent), transparent 65%),` +
            "color-mix(in srgb, var(--glass) 76%, transparent)",
        }}
        className="zodiac-symbol rounded-full border p-1 flex items-center justify-center"
      >
        <Image
          src={src}
          alt={key}
          width={innerSize}
          height={innerSize}
          className="zodiac-symbol-image"
          style={{
            filter: `var(--zodiac-icon-filter) drop-shadow(0 0 5px color-mix(in srgb, var(${toneVar}) 65%, transparent))`,
          }}
        />
      </div>
    );
  }

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-label={sign}
      role="img"
    >
      <circle
        cx="16"
        cy="16"
        r="15"
        stroke="var(--line-bright)"
        strokeWidth="1"
      />
      <text
        x="16"
        y="21"
        textAnchor="middle"
        fontFamily="var(--font-display)"
        fontSize="18"
        fill="var(--color-gold-bright)"
      >
        {glyph}
      </text>
    </svg>
  );
}

export function PlanetSymbol({ planet, size = 24 }) {
  const glyph = planetGlyphs[planet] || "?";
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 28 28"
      fill="none"
      aria-label={planet}
      role="img"
    >
      <rect
        x="1"
        y="1"
        width="26"
        height="26"
        rx="13"
        stroke="var(--line-bright)"
        strokeWidth="1"
      />
      <text
        x="14"
        y="19"
        textAnchor="middle"
        fontFamily="var(--font-display)"
        fontSize="16"
        fill="var(--color-gold-bright)"
      >
        {glyph}
      </text>
    </svg>
  );
}

export const zodiacOrder = [
  "Aries",
  "Taurus",
  "Gemini",
  "Cancer",
  "Leo",
  "Virgo",
  "Libra",
  "Scorpio",
  "Sagittarius",
  "Capricorn",
  "Aquarius",
  "Pisces",
];
