/**
 * Maps domain URLs to icons and brand colors.
 */

type IconData = string | { type: 'svg'; svg: string }

interface DomainMeta {
  icon: IconData
  color?: string
}

const DOMAIN_META: Record<string, DomainMeta> = {
  'bandcamp.com': {
    icon: {
      type: 'svg',
      svg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="currentColor"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M320 72C183 72 72 183 72 320C72 457 183 568 320 568C457 568 568 457 568 320C568 183 457 72 320 72zM368.2 398.1L187.2 398.1L271.9 242L452.9 242L368.2 398.1z"/></svg>'
    },
    color: '#1DA1F2'
  },
  'soundcloud.com': { icon: 'bi-cloud-fog2-fill', color: '#FF5500' },
  'youtube.com': { icon: 'bi-youtube', color: '#FF0000' },
  'youtu.be': { icon: 'bi-youtube', color: '#FF0000' },
  'mixcloud.com': { icon: 'bi-speaker-fill', color: '#273B6B' },
  'discogs.com': { icon: 'bi-disc-fill', color: 'currentColor' },
  'twitter.com': { icon: 'bi-twitter', color: '#000000' },
  'x.com': { icon: 'bi-twitter-x', color: '#000000' },
  'instagram.com': { icon: 'bi-instagram', color: '#E4405F' },
  'facebook.com': { icon: 'bi-facebook', color: '#1877F2' },
  'spotify.com': { icon: 'bi-spotify', color: '#1DB954' },
  'twitch.tv': { icon: 'bi-twitch', color: '#9146FF' },
  'tiktok.com': { icon: 'bi-tiktok', color: '#000000' },
  'discord.com': { icon: 'bi-discord', color: '#5865F2' },
  'discord.gg': { icon: 'bi-discord', color: '#5865F2' },
  'reddit.com': { icon: 'bi-reddit', color: '#FF4500' },
  'mastodon.social': { icon: 'bi-mastodon', color: '#6364FF' },
  'github.com': { icon: 'bi-github', color: '#161B22' },
  'linkedin.com': { icon: 'bi-linkedin', color: '#0077B5' },
  'patreon.com': { icon: 'bi-heart-fill', color: '#FF424D' },
  'kofi.com': { icon: 'bi-heart-fill', color: '#FF5E78' },
  'ko-fi.com': { icon: 'bi-heart-fill', color: '#FF5E78' },
  'buymeacoffee.com': { icon: 'bi-cup-hot-fill', color: '#FFDD00' },
  'paypal.com': { icon: 'bi-paypal', color: '#003087' },
  'bluesky.app': { icon: 'bi-bluesky', color: '#1185FE' },
  'threads.net': { icon: 'bi-chat-dots-fill', color: '#000000' }
}

const looksLikeUrl = (value: string) => value.includes('.') && !/^\s*$/.test(value)

const normalizeHostname = (url: string): string | null => {
  try {
    const parsedUrl = url.startsWith('http://') || url.startsWith('https://') ? url : `https://${url}`
    return new URL(parsedUrl).hostname.replace('www.', '')
  } catch {
    return null
  }
}

const resolveDomainMeta = (url: string): { meta?: DomainMeta; hostname?: string } => {
  if (url.startsWith('mailto:')) return { meta: { icon: 'bi-envelope' }, hostname: 'mailto' }
  const hostname = normalizeHostname(url)
  if (!hostname) return {}

  for (const [domain, meta] of Object.entries(DOMAIN_META)) {
    if (hostname === domain || hostname.endsWith(`.${domain}`)) return { meta, hostname }
  }

  return { hostname }
}

export function resolveLinkMeta(url: string): {
  iconData: IconData
  color?: string
  svgDataUrl?: string
} {
  const { meta } = looksLikeUrl(url) ? resolveDomainMeta(url) : {}
  const iconData: IconData = meta?.icon ?? 'bi-globe'
  const color = meta?.color

  let svgDataUrl: string | undefined
  if (color && typeof iconData === 'object' && 'svg' in iconData) {
    const svgString = iconData.svg.replace(/fill="currentColor"/g, `fill="${color}"`)
    svgDataUrl = `data:image/svg+xml;base64,${btoa(svgString)}`
  }

  return {
    iconData,
    color,
    svgDataUrl
  }
}

export function mapUrlToIcon(url: string): string | null {
  const meta = resolveLinkMeta(url)
  return typeof meta.iconData === 'string' ? meta.iconData : null
}

export function getIconData(url: string): IconData {
  return resolveLinkMeta(url).iconData
}

export function getBrandColor(url: string): string | undefined {
  return resolveLinkMeta(url).color
}

export function getSvgDataUrl(url: string): string | undefined {
  return resolveLinkMeta(url).svgDataUrl
}
