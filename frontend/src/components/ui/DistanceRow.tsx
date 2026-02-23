interface DistanceRowProps {
  label: string;
  value: string | number;
  className?: string;
}

export function DistanceRow({ label, value, className = '' }: DistanceRowProps) {
  return (
    <div className={`distance-row ${className}`.trim()}>
      <span className="distance-row-label">{label}</span>
      <span className="distance-row-connector" />
      <span className="distance-row-value">{value}</span>
    </div>
  );
}
