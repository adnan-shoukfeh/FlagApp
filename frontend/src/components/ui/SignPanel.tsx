import { motion, type HTMLMotionProps } from 'framer-motion';
import { signReveal } from '../../animations/variants';

interface SignPanelProps extends HTMLMotionProps<'div'> {
  animate?: boolean;
  feedback?: 'correct' | 'incorrect' | null;
}

export function SignPanel({
  children,
  className = '',
  animate: shouldAnimate = true,
  feedback,
  ...props
}: SignPanelProps) {
  const feedbackClass = feedback === 'correct'
    ? 'feedback-correct'
    : feedback === 'incorrect'
      ? 'feedback-incorrect'
      : '';

  return (
    <motion.div
      className={`sign-panel ${feedbackClass} ${className}`.trim()}
      {...(shouldAnimate ? signReveal : {})}
      {...props}
    >
      {children}
    </motion.div>
  );
}
