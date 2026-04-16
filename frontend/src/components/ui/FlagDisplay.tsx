import { useState } from 'react';

interface FlagDisplayProps {
  svgUrl: string;
  pngUrl: string;
  altText: string;
  className?: string;
  /** Ratio-agnostic mode: fixed-height container with padding, image never stretches */
  contained?: boolean;
}

export function FlagDisplay({
  svgUrl,
  pngUrl,
  altText,
  className = '',
  contained = false,
}: FlagDisplayProps) {
  const [useFallback, setUseFallback] = useState(false);

  if (contained) {
    return (
      <div className={`country-flag-display ${className}`.trim()}>
        <img
          src={useFallback ? pngUrl : svgUrl}
          alt={altText}
          onError={() => {
            if (!useFallback) setUseFallback(true);
          }}
        />
      </div>
    );
  }

  return (
    <div className={`flag-container ${className}`.trim()}>
      <img
        className="flag-image"
        src={useFallback ? pngUrl : svgUrl}
        alt={altText}
        onError={() => {
          if (!useFallback) setUseFallback(true);
        }}
      />
    </div>
  );
}
