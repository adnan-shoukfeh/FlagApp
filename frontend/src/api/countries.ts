import client from './client';
import type { CountryListItem, CountryDetail } from '../types/api';

export async function searchCountries(
  query: string,
  limit = 10,
): Promise<CountryListItem[]> {
  const { data } = await client.get<CountryListItem[]>('/countries/search/', {
    params: { query, limit },
  });
  return data;
}

export async function fetchCountryByCode(
  code: string,
): Promise<CountryDetail> {
  const { data } = await client.get<CountryDetail>(`/countries/${code}/`);
  return data;
}
