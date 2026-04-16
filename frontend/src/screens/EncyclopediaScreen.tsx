import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchCountries } from '../api/encyclopedia';
import { SignPanel } from '../components/ui/SignPanel';
import { staggerContainer, staggerChild } from '../animations/variants';
import type { CountryListItem } from '../types/encyclopedia';

function formatPopulation(pop: number): string {
  if (pop >= 1_000_000_000) return `${(pop / 1_000_000_000).toFixed(1)}B`;
  if (pop >= 1_000_000) return `${(pop / 1_000_000).toFixed(1)}M`;
  if (pop >= 1_000) return `${(pop / 1_000).toFixed(0)}K`;
  return pop.toLocaleString();
}

export function EncyclopediaScreen() {
  const [countries, setCountries] = useState<CountryListItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchCountries()
      .then((data) => {
        if (!cancelled) {
          setCountries(data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('Failed to load countries.');
          setLoading(false);
        }
      });
    return () => { cancelled = true; };
  }, []);

  const filtered = useMemo(() => {
    if (!search.trim()) return countries;
    const q = search.toLowerCase();
    return countries.filter((c) => c.name.toLowerCase().includes(q));
  }, [countries, search]);

  if (loading) {
    return (
      <div className="encyclopedia-loading">
        <div className="skeleton-row" style={{ width: '100%' }} />
        <div className="skeleton-row" />
        <div className="skeleton-row" />
      </div>
    );
  }

  if (error) {
    return (
      <SignPanel>
        <p className="encyclopedia-empty">{error}</p>
      </SignPanel>
    );
  }

  return (
    <>
      <div className="encyclopedia-search">
        <input
          className="encyclopedia-search-input"
          type="text"
          placeholder="Search countries…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          autoComplete="off"
        />
      </div>

      <SignPanel animate={false}>
        {filtered.length === 0 ? (
          <p className="encyclopedia-empty">No countries found</p>
        ) : (
          <motion.div
            className="country-list"
            variants={staggerContainer}
            initial="initial"
            animate="animate"
          >
            {filtered.map((country) => (
              <motion.div key={country.code} variants={staggerChild}>
                <Link to={`/encyclopedia/${country.code}`} className="country-row">
                  <div className="country-row-flag">
                    <img src={country.flag_svg_url} alt={country.name} />
                  </div>
                  <span className="country-row-name">{country.name}</span>
                  <span className="country-row-meta">
                    {country.capital && <span>{country.capital}</span>}
                    {country.population > 0 && (
                      <span>{formatPopulation(country.population)}</span>
                    )}
                  </span>
                  <span className="country-row-chevron">›</span>
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </SignPanel>
    </>
  );
}
