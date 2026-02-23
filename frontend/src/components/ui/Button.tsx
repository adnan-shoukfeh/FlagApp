import { Slot } from '@radix-ui/react-slot';
import type { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost';
  asChild?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  asChild,
  className = '',
  children,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot : 'button';
  const variantClass = `btn-${variant}`;

  return (
    <Comp className={`btn ${variantClass} ${className}`.trim()} {...props}>
      {children}
    </Comp>
  );
}
