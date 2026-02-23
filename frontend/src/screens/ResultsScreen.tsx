import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { CheckCircle, XCircle, Clock } from 'lucide-react';
import { useChallengeStore } from '../stores/challengeStore';
import { SignPanel } from '../components/ui/SignPanel';
import { Wordmark } from '../components/ui/Wordmark';
import { FlagDisplay } from '../components/ui/FlagDisplay';
import { Badge } from '../components/ui/Badge';
import { DistanceRow } from '../components/ui/DistanceRow';
import { badgePop } from '../animations/variants';

export function ResultsScreen() {
  const navigate = useNavigate();
  const { challenge, lastAnswer } = useChallengeStore();

  useEffect(() => {
    if (!challenge) {
      navigate('/daily', { replace: true });
    }
  }, [challenge, navigate]);

  if (!challenge) return null;

  const { country, user_status } = challenge;
  const isCorrect = user_status.is_correct === true;

  // Extract country name from correct_answer if available
  const countryName = lastAnswer?.correct_answer
    ? (lastAnswer.correct_answer as Record<string, string>).text || 'Unknown'
    : 'Unknown';

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

      {/* Result icon */}
      <div style={{ textAlign: 'center' }}>
        <motion.div {...badgePop} style={{ display: 'inline-block' }}>
          {isCorrect ? (
            <CheckCircle size={64} color="var(--color-correct)" />
          ) : (
            <XCircle size={64} color="var(--color-incorrect)" />
          )}
        </motion.div>
      </div>

      {/* Country name reveal */}
      <h1 style={{
        fontWeight: 900,
        fontSize: isCorrect ? 'var(--text-hero)' : 'var(--text-4xl)',
        textAlign: 'center',
        letterSpacing: '-0.04em',
        color: isCorrect ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
      }}>
        {countryName}
      </h1>

      {/* Flag */}
      <FlagDisplay
        svgUrl={country.flag_svg_url}
        pngUrl={country.flag_png_url}
        altText={country.flag_alt_text}
      />

      {/* Stats */}
      <SignPanel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          <DistanceRow
            label="Attempts Used"
            value={`${user_status.attempts_used} / 3`}
          />
          <DistanceRow
            label="Result"
            value={isCorrect ? 'Correct' : 'Incorrect'}
          />
          {lastAnswer?.explanation && (
            <DistanceRow
              label="Detail"
              value={lastAnswer.explanation}
            />
          )}
        </div>
      </SignPanel>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        color: 'var(--color-text-secondary)',
        fontSize: 'var(--text-sm)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 'var(--space-2)',
      }}>
        <Clock size={16} />
        <span>Come back tomorrow for a new challenge</span>
      </div>
    </>
  );
}
