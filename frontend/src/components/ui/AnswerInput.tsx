import { forwardRef, type InputHTMLAttributes } from 'react';

interface AnswerInputProps extends InputHTMLAttributes<HTMLInputElement> {
  status?: 'idle' | 'correct' | 'incorrect';
}

export const AnswerInput = forwardRef<HTMLInputElement, AnswerInputProps>(
  ({ status = 'idle', className = '', ...props }, ref) => {
    const statusClass = status !== 'idle' ? status : '';

    return (
      <input
        ref={ref}
        type="text"
        autoComplete="off"
        className={`answer-input ${statusClass} ${className}`.trim()}
        {...props}
      />
    );
  }
);

AnswerInput.displayName = 'AnswerInput';
