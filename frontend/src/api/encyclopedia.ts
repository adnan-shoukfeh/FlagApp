import client from './client';
import type { CountryListItem, CountryDetail } from '../types/encyclopedia';

export async function fetchCountries(): Promise<CountryListItem[]> {
  const { data } = await client.get<CountryListItem[]>('/countries/');
  return data;
}

export async function fetchCountryDetail(code: string): Promise<CountryDetail> {
  const { data } = await client.get<CountryDetail>(`/countries/${code}/`);
  return data;
}
