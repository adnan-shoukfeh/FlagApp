import { Globe } from 'lucide-react';

interface WordmarkProps {
  className?: string;
}

export function Wordmark({ className = '' }: WordmarkProps) {
  return (
    <div
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 'var(--space-2)',
      }}
    >
      <Globe size={20} />
      <span
        style={{
          fontFamily: 'var(--font-primary)',
          fontWeight: 800,
          fontSize: 'var(--text-lg)',
          letterSpacing: '0.12em',
          textTransform: 'uppercase' as const,
          color: 'var(--color-text-primary)',
        }}
      >
        Globule
      </span>
    </div>
  );
}
