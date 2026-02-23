import type { Variants } from 'framer-motion';

/* framer-motion props for SignPanel entrance */
export const signReveal = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: 'easeOut' },
};

/* Badge pop-in (spring) */
export const badgePop = {
  initial: { scale: 0, opacity: 0 },
  animate: { scale: 1, opacity: 1 },
  transition: { type: 'spring', stiffness: 400, damping: 15 },
};

/* Correct answer flash — use as CSS animation via className */
export const correctFlash = {
  animate: { background: ['var(--color-surface)', 'rgba(74, 222, 128, 0.2)', 'var(--color-surface)'] },
  transition: { duration: 0.5 },
};

/* Incorrect shake */
export const incorrectShake = {
  animate: { x: [0, -8, 8, -4, 4, 0] },
  transition: { duration: 0.4 },
};

/* Streak fire — looping scale + rotate */
export const streakFire: Variants = {
  animate: {
    scale: [1, 1.15, 1],
    rotate: [-3, 3, -3],
    transition: {
      duration: 1.5,
      ease: 'easeInOut',
      repeat: Infinity,
    },
  },
};

/* Stagger children container */
export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: 0.08,
    },
  },
};

export const staggerChild: Variants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: 'easeOut' },
  },
};
