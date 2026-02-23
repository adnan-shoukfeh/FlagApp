import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useChallengeStore } from '../stores/challengeStore';
import { SignPanel } from '../components/ui/SignPanel';
import { Wordmark } from '../components/ui/Wordmark';
import { FlagDisplay } from '../components/ui/FlagDisplay';
import { AnswerInput } from '../components/ui/AnswerInput';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { incorrectShake } from '../animations/variants';

export function DailyChallengeScreen() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [guess, setGuess] = useState('');
  const [inputStatus, setInputStatus] = useState<'idle' | 'correct' | 'incorrect'>('idle');
  const [panelFeedback, setPanelFeedback] = useState<'correct' | 'incorrect' | null>(null);

  const {
    challenge,
    isLoading,
    isSubmitting,
    error,
    loadChallenge,
    submit,
    startTimer,
  } = useChallengeStore();

  useEffect(() => {
    loadChallenge();
    startTimer();
  }, [loadChallenge, startTimer]);

  // If challenge is already completed on load, go to results
  useEffect(() => {
    if (challenge?.user_status.has_completed) {
      navigate('/results', { replace: true });
    }
  }, [challenge?.user_status.has_completed, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guess.trim() || isSubmitting) return;

    try {
      const result = await submit(guess.trim());

      if (result.is_correct) {
        setInputStatus('correct');
        setPanelFeedback('correct');
        setTimeout(() => navigate('/results'), 1200);
      } else {
        setInputStatus('incorrect');
        setPanelFeedback('incorrect');
        setTimeout(() => {
          setInputStatus('idle');
          setPanelFeedback(null);
          setGuess('');
          inputRef.current?.focus();
        }, 800);

        // Navigate to results if no attempts remaining
        if (result.attempts_remaining === 0) {
          setTimeout(() => navigate('/results'), 1200);
        }
      }
    } catch {
      // Error is set in the store
    }
  };

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
      }}>
        <SignPanel animate={false}>
          <p style={{ color: 'var(--color-text-secondary)' }}>Loading challenge...</p>
        </SignPanel>
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flex: 1,
      }}>
        <SignPanel animate={false}>
          <p style={{ color: 'var(--color-incorrect)' }}>
            {error || 'No challenge available'}
          </p>
        </SignPanel>
      </div>
    );
  }

  const { country, question, user_status } = challenge;

  return (
    <>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <Wordmark />
        <Badge variant="euro">{challenge.date}</Badge>
      </div>

      {/* Flag */}
      <FlagDisplay
        svgUrl={country.flag_svg_url}
        pngUrl={country.flag_png_url}
        altText={country.flag_alt_text}
      />

      {/* Question + Answer */}
      <SignPanel feedback={panelFeedback}>
        <p style={{
          fontWeight: 700,
          fontSize: 'var(--text-xl)',
          textAlign: 'center',
          marginBottom: 'var(--space-6)',
        }}>
          {question.question_text}
        </p>

        <form onSubmit={handleSubmit}>
          <motion.div
            {...(inputStatus === 'incorrect' ? incorrectShake : {})}
          >
            <AnswerInput
              ref={inputRef}
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              status={inputStatus}
              placeholder="Type your answer..."
              disabled={isSubmitting}
              autoFocus
            />
          </motion.div>

          <div style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
            <Button
              type="submit"
              variant="primary"
              disabled={!guess.trim() || isSubmitting}
              style={{ width: '100%' }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </Button>
          </div>
        </form>

        {/* Attempt indicators */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 'var(--space-2)',
          marginTop: 'var(--space-6)',
        }}>
          {Array.from({ length: 3 }).map((_, i) => (
            <Badge
              key={i}
              variant={i < user_status.attempts_used ? 'national' : 'euro'}
            >
              {i + 1}
            </Badge>
          ))}
        </div>
      </SignPanel>
    </>
  );
}
