import { ofetch } from 'ofetch'
import type { ScrapeRequest, ScrapeResponse } from '~/types/scrape'

/**
 * Typed client for the scraper backend.
 *
 * ofetch serialises object bodies to JSON and sets the Content-Type header on
 * its own, so the client only needs the base URL from the runtime config.
 * Errors are thrown as ofetch `FetchError`s and mapped to UI state by the store.
 */
export function useScraperApi() {
  const { scraperApiUrl } = useRuntimeConfig().public
  const client = ofetch.create({ baseURL: scraperApiUrl })

  function scrape(request: ScrapeRequest): Promise<ScrapeResponse> {
    return client<ScrapeResponse>('/scrape/', { method: 'POST', body: request })
  }

  return { scrape }
}
