import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, ArrowLeft, BookOpen, Globe } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { searchCountries, fetchCountryByCode } from '../api/countries';
import { SignPanel } from '../components/ui/SignPanel';
import { FlagDisplay } from '../components/ui/FlagDisplay';
import { DistanceRow } from '../components/ui/DistanceRow';
import { Wordmark } from '../components/ui/Wordmark';
import { staggerChild, staggerContainer } from '../animations/variants';
import type { CountryListItem, CountryDetail } from '../types/api';

function formatNumber(n: number): string {
  if (n >= 1_000_000_000) return `${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString();
}

function formatArea(km2: number): string {
  return `${km2.toLocaleString()} km²`;
}

function getLanguagesList(
  languages: string[] | Record<string, string>,
): string[] {
  if (Array.isArray(languages)) return languages;
  return Object.values(languages);
}

function getCurrenciesList(
  currencies: Record<string, { name: string; symbol: string }>,
): { code: string; name: string; symbol: string }[] {
  return Object.entries(currencies).map(([code, info]) => ({
    code,
    name: info.name,
    symbol: info.symbol,
  }));
}

export function EncyclopediaScreen() {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<CountryListItem[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedCountry, setSelectedCountry] = useState<CountryDetail | null>(
    null,
  );
  const [isLoadingSearch, setIsLoadingSearch] = useState(false);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLUListElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const performSearch = useCallback(async (q: string) => {
    if (q.trim().length === 0) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    setIsLoadingSearch(true);
    try {
      const results = await searchCountries(q, 8);
      setSuggestions(results);
      setShowSuggestions(results.length > 0);
      setActiveIndex(-1);
    } catch {
      setSuggestions([]);
    } finally {
      setIsLoadingSearch(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (selectedCountry) return;
    debounceRef.current = setTimeout(() => performSearch(query), 200);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, performSearch, selectedCountry]);

  const selectCountry = async (item: CountryListItem) => {
    setShowSuggestions(false);
    setQuery(item.name);
    setIsLoadingDetail(true);
    try {
      const detail = await fetchCountryByCode(item.code);
      setSelectedCountry(detail);
    } catch {
      setSelectedCountry(null);
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleBack = () => {
    setSelectedCountry(null);
    setQuery('');
    setSuggestions([]);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((i) => (i < suggestions.length - 1 ? i + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((i) => (i > 0 ? i - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault();
      selectCountry(suggestions[activeIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  useEffect(() => {
    if (activeIndex >= 0 && suggestionsRef.current) {
      const activeEl = suggestionsRef.current.children[activeIndex] as HTMLElement;
      activeEl?.scrollIntoView({ block: 'nearest' });
    }
  }, [activeIndex]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="encyclopedia">
      <Wordmark />

      {selectedCountry ? (
        <CountryDetailView
          country={selectedCountry}
          onBack={handleBack}
        />
      ) : (
        <>
          <div className="encyclopedia-search">
            <Search size={18} className="encyclopedia-search-icon" />
            <input
              ref={inputRef}
              type="text"
              className="encyclopedia-search-input"
              placeholder="Search countries..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => {
                if (suggestions.length > 0) setShowSuggestions(true);
              }}
              onKeyDown={handleKeyDown}
              autoComplete="off"
              spellCheck={false}
            />

            <AnimatePresence>
              {showSuggestions && suggestions.length > 0 && (
                <motion.ul
                  ref={suggestionsRef}
                  className="encyclopedia-suggestions"
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  transition={{ duration: 0.15 }}
                  role="listbox"
                >
                  {suggestions.map((item, idx) => (
                    <li
                      key={item.code}
                      className="encyclopedia-suggestion"
                      data-active={idx === activeIndex}
                      role="option"
                      aria-selected={idx === activeIndex}
                      onClick={() => selectCountry(item)}
                      onMouseEnter={() => setActiveIndex(idx)}
                    >
                      <span className="encyclopedia-suggestion-emoji">
                        {item.flag_emoji}
                      </span>
                      <div className="encyclopedia-suggestion-info">
                        <div className="encyclopedia-suggestion-name">
                          {item.name}
                        </div>
                        <div className="encyclopedia-suggestion-capital">
                          {item.capital}
                        </div>
                      </div>
                    </li>
                  ))}
                </motion.ul>
              )}
            </AnimatePresence>
          </div>

          {isLoadingSearch && query.trim().length > 0 && (
            <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', textAlign: 'center' }}>
              Searching...
            </p>
          )}

          {!isLoadingSearch && query.trim().length > 0 && suggestions.length === 0 && !showSuggestions && (
            <div className="encyclopedia-empty">
              <Globe size={48} className="encyclopedia-empty-icon" />
              <p className="encyclopedia-empty-title">No countries found</p>
              <p className="encyclopedia-empty-subtitle">
                Try a different spelling or search term
              </p>
            </div>
          )}

          {!query.trim() && (
            <div className="encyclopedia-empty">
              <BookOpen size={48} className="encyclopedia-empty-icon" />
              <p className="encyclopedia-empty-title">Encyclopedia</p>
              <p className="encyclopedia-empty-subtitle">
                Search for any country to explore its geography, demographics, and more
              </p>
            </div>
          )}
        </>
      )}

      {isLoadingDetail && (
        <p style={{ color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)', textAlign: 'center' }}>
          Loading country details...
        </p>
      )}
    </div>
  );
}

function CountryDetailView({
  country,
  onBack,
}: {
  country: CountryDetail;
  onBack: () => void;
}) {
  const languages = getLanguagesList(country.languages);
  const currencies = getCurrenciesList(country.currencies);

  return (
    <motion.div
      className="encyclopedia-detail"
      variants={staggerContainer}
      initial="initial"
      animate="animate"
    >
      <motion.div variants={staggerChild}>
        <button className="encyclopedia-back-btn" onClick={onBack}>
          <ArrowLeft size={16} />
          Back to search
        </button>
      </motion.div>

      <motion.div variants={staggerChild}>
        <FlagDisplay
          svgUrl={country.flag_svg_url}
          pngUrl={country.flag_png_url}
          altText={country.flag_alt_text || `Flag of ${country.name}`}
        />
      </motion.div>

      <motion.div variants={staggerChild}>
        <div className="encyclopedia-detail-header">
          <span className="encyclopedia-detail-emoji">{country.flag_emoji}</span>
          <div>
            <h1 className="encyclopedia-detail-title">{country.name}</h1>
            <p className="encyclopedia-detail-subtitle">{country.code}</p>
          </div>
        </div>
      </motion.div>

      <motion.div variants={staggerChild}>
        <SignPanel animate={false}>
          <p className="encyclopedia-section-title">Geography</p>
          <div className="encyclopedia-stats">
            <DistanceRow label="Capital" value={country.capital} />
            <DistanceRow label="Largest city" value={country.largest_city} />
            <DistanceRow label="Area" value={formatArea(country.area_km2)} />
            <DistanceRow
              label="Coordinates"
              value={`${country.latitude.toFixed(1)}°, ${country.longitude.toFixed(1)}°`}
            />
            {country.highest_point && (
              <DistanceRow label="Highest point" value={country.highest_point} />
            )}
          </div>
        </SignPanel>
      </motion.div>

      <motion.div variants={staggerChild}>
        <SignPanel animate={false}>
          <p className="encyclopedia-section-title">Demographics</p>
          <div className="encyclopedia-stats">
            <DistanceRow
              label="Population"
              value={formatNumber(country.population)}
            />
            {country.median_age != null && (
              <DistanceRow label="Median age" value={`${country.median_age} yr`} />
            )}
            {country.life_expectancy != null && (
              <DistanceRow
                label="Life expectancy"
                value={`${country.life_expectancy} yr`}
              />
            )}
            {country.fertility_rate != null && (
              <DistanceRow
                label="Fertility rate"
                value={country.fertility_rate.toFixed(1)}
              />
            )}
          </div>
        </SignPanel>
      </motion.div>

      {languages.length > 0 && (
        <motion.div variants={staggerChild}>
          <SignPanel animate={false}>
            <p className="encyclopedia-section-title">Languages</p>
            <div className="encyclopedia-languages">
              {languages.map((lang) => (
                <span key={lang} className="encyclopedia-language-tag">
                  {lang}
                </span>
              ))}
            </div>
          </SignPanel>
        </motion.div>
      )}

      {currencies.length > 0 && (
        <motion.div variants={staggerChild}>
          <SignPanel animate={false}>
            <p className="encyclopedia-section-title">Currencies</p>
            <div className="encyclopedia-currencies">
              {currencies.map((c) => (
                <span key={c.code} className="encyclopedia-currency-tag">
                  {c.symbol} {c.name} ({c.code})
                </span>
              ))}
            </div>
          </SignPanel>
        </motion.div>
      )}

      {(country.gdp_nominal != null || country.gdp_ppp_per_capita != null || country.arable_land_percent != null) && (
        <motion.div variants={staggerChild}>
          <SignPanel animate={false}>
            <p className="encyclopedia-section-title">Economy</p>
            <div className="encyclopedia-stats">
              {country.gdp_nominal != null && (
                <DistanceRow
                  label="GDP (nominal)"
                  value={`$${formatNumber(country.gdp_nominal)}`}
                />
              )}
              {country.gdp_ppp_per_capita != null && (
                <DistanceRow
                  label="GDP per capita (PPP)"
                  value={`$${country.gdp_ppp_per_capita.toLocaleString()}`}
                />
              )}
              {country.arable_land_percent != null && (
                <DistanceRow
                  label="Arable land"
                  value={`${country.arable_land_percent.toFixed(1)}%`}
                />
              )}
            </div>
          </SignPanel>
        </motion.div>
      )}
    </motion.div>
  );
}
