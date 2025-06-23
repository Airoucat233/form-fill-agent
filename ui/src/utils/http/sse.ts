import { fetchEventSource, type FetchEventSourceInit } from '@microsoft/fetch-event-source'

const baseURL = import.meta.env.VITE_APP_BASE_API

export const streamFetch = async (url: string, config: FetchEventSourceInit) => {
  return fetchEventSource(baseURL + url, {
    headers: Object.assign(
      {
        // Authorization: "Bearer <access token>",
        'Content-Type': 'application/json',
      },
      config.headers ?? {},
    ),
    openWhenHidden: true,
    ...config,
  })
}
