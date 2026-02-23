import type { ReactNode } from 'react';

interface BadgeProps {
  variant: 'national' | 'euro';
  children: ReactNode;
  className?: string;
  revealed?: boolean;
}

export function Badge({ variant, children, className = '', revealed }: BadgeProps) {
  const baseClass = variant === 'national' ? 'badge-national' : 'badge-euro';
  const revealedClass = revealed ? 'revealed' : '';

  return (
    <span className={`${baseClass} ${revealedClass} ${className}`.trim()}>
      {children}
    </span>
  );
}
