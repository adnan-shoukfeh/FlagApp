import { useState } from 'react';

interface FlagDisplayProps {
  svgUrl: string;
  pngUrl: string;
  altText: string;
  className?: string;
}

export function FlagDisplay({ svgUrl, pngUrl, altText, className = '' }: FlagDisplayProps) {
  const [useFallback, setUseFallback] = useState(false);

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
