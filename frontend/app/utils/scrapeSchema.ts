import { z } from 'zod'
import type { ScrapeRequest } from '~/types/scrape'

export const MAX_CALL_COUNT = 10

function isHttpUrl(value: string): boolean {
  try {
    const { protocol } = new URL(value)
    return protocol === 'http:' || protocol === 'https:'
  }
  catch {
    return false
  }
}

export const scrapeRequestSchema = z.object({
  url: z
    .string({ required_error: 'Enter a URL' })
    .trim()
    .min(1, 'Enter a URL')
    .refine(isHttpUrl, 'Enter a valid http or https URL'),
  call_count: z
    .number({ required_error: 'Enter the number of attempts', invalid_type_error: 'Enter a number' })
    .int('Must be a whole number')
    .min(1, 'Must be at least 1')
    .max(MAX_CALL_COUNT, `Must be at most ${MAX_CALL_COUNT}`)
}) satisfies z.ZodType<ScrapeRequest>
