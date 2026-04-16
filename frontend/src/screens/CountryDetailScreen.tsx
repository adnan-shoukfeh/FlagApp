import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchCountryDetail } from '../api/encyclopedia';
import { FlagDisplay } from '../components/ui/FlagDisplay';
import { SignPanel } from '../components/ui/SignPanel';
import { DistanceRow } from '../components/ui/DistanceRow';
import { staggerContainer, staggerChild } from '../animations/variants';
import type { CountryDetail } from '../types/encyclopedia';

function formatNumber(n: number): string {
  return n.toLocaleString();
}

function formatArea(km2: number): string {
  return `${km2.toLocaleString()} km²`;
}

function formatCurrency(currencies: Record<string, { name: string; symbol: string }>): string {
  return Object.values(currencies)
    .map((c) => `${c.name} (${c.symbol})`)
    .join(', ');
}

interface PanelField {
  label: string;
  value: string | number;
}

function DataPanel({ title, fields }: { title: string; fields: PanelField[] }) {
  if (fields.length === 0) return null;
  return (
    <SignPanel>
      <div className="country-panel-title">{title}</div>
      <div className="country-panel-rows">
        {fields.map((f) => (
          <DistanceRow key={f.label} label={f.label} value={f.value} />
        ))}
      </div>
    </SignPanel>
  );
}

function ListPanel({ title, items }: { title: string; items: string[] }) {
  if (items.length === 0) return null;
  return (
    <SignPanel>
      <div className="country-panel-title">{title}</div>
      <div className="country-list-panel">
        {items.map((item) => (
          <div key={item} className="country-list-item">
            <span className="country-list-bullet">–</span>
            {item}
          </div>
        ))}
      </div>
    </SignPanel>
  );
}

function CountryDetailInner({ code }: { code: string }) {
  const [country, setCountry] = useState<CountryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchCountryDetail(code)
      .then((data) => {
        if (!cancelled) {
          setCountry(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Failed to load country details.');
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, [code]);

  if (loading) {
    return (
      <div className="encyclopedia-loading">
        <div className="skeleton-row" style={{ width: '100%' }} />
        <div className="skeleton-row" />
        <div className="skeleton-row" />
      </div>
    );
  }

  if (error || !country) {
    return (
      <SignPanel>
        <p className="encyclopedia-empty">{error ?? 'Country not found.'}</p>
      </SignPanel>
    );
  }

  const geographyFields: PanelField[] = [
    country.capital ? { label: 'Capital', value: country.capital } : null,
    country.largest_city ? { label: 'Largest City', value: country.largest_city } : null,
    country.area_km2 != null ? { label: 'Area', value: formatArea(country.area_km2) } : null,
    country.highest_point ? { label: 'Highest Point', value: country.highest_point } : null,
  ].filter((f): f is PanelField => f !== null);

  const peopleFields: PanelField[] = [
    country.population ? { label: 'Population', value: formatNumber(country.population) } : null,
    country.median_age != null ? { label: 'Median Age', value: `${country.median_age} years` } : null,
    country.life_expectancy != null ? { label: 'Life Expectancy', value: `${country.life_expectancy} years` } : null,
    country.fertility_rate != null ? { label: 'Fertility Rate', value: country.fertility_rate.toFixed(2) } : null,
  ].filter((f): f is PanelField => f !== null);

  const economyFields: PanelField[] = [
    country.gdp_ppp_per_capita != null
      ? { label: 'GDP (PPP) Per Capita', value: `$${formatNumber(country.gdp_ppp_per_capita)}` }
      : null,
    country.currencies && Object.keys(country.currencies).length > 0
      ? { label: 'Currency', value: formatCurrency(country.currencies) }
      : null,
  ].filter((f): f is PanelField => f !== null);

  const languages = Array.isArray(country.languages) ? country.languages : [];
  const religions = Array.isArray(country.religions) ? country.religions : [];

  return (
    <motion.div
      className="country-detail"
      variants={staggerContainer}
      initial="initial"
      animate="animate"
    >
      <motion.div variants={staggerChild}>
        <Link to="/encyclopedia" className="country-back-link">
          ‹ All countries
        </Link>
      </motion.div>

      <motion.div variants={staggerChild}>
        <FlagDisplay
          svgUrl={country.flag_svg_url}
          pngUrl={country.flag_png_url}
          altText={country.flag_alt_text ?? country.name}
          contained
        />
      </motion.div>

      <motion.div variants={staggerChild} className="country-header">
        <div className="country-header-name">{country.name}</div>
        <div className="country-header-code">{country.code}</div>
      </motion.div>

      <motion.div variants={staggerChild}>
        <DataPanel title="Geography" fields={geographyFields} />
      </motion.div>

      <motion.div variants={staggerChild}>
        <DataPanel title="People" fields={peopleFields} />
      </motion.div>

      <motion.div variants={staggerChild}>
        <DataPanel title="Economy" fields={economyFields} />
      </motion.div>

      {languages.length > 0 && (
        <motion.div variants={staggerChild}>
          <ListPanel title="Languages" items={languages} />
        </motion.div>
      )}

      {religions.length > 0 && (
        <motion.div variants={staggerChild}>
          <ListPanel title="Religions" items={religions} />
        </motion.div>
      )}
    </motion.div>
  );
}

export function CountryDetailScreen() {
  const { code } = useParams<{ code: string }>();

  if (!code) {
    return (
      <SignPanel>
        <p className="encyclopedia-empty">Country not found.</p>
      </SignPanel>
    );
  }

  return <CountryDetailInner key={code} code={code} />;
}
