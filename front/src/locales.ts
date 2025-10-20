import type { VueI18nOptions } from 'vue-i18n'

export type SupportedLanguages = 'ar' | 'ca' | 'ca@valencia' | 'cs' | 'de' | 'en_GB' | 'en_US' | 'eo' | 'es' | 'eu' | 'fr_FR'
  | 'gl' | 'hu' | 'it' | 'ja_JP' | 'kab_DZ' | 'ko_KR' | 'nb_NO' | 'nl' | 'oc' | 'pl' | 'pt_BR' | 'pt_PT'
  | 'ru' | 'sq' | 'zh_Hans' | 'zh_Hant' | 'fa_IR' | 'ml' | 'sv' | 'el' | 'nn_NO'

export interface Locale {
  label: string
  direction: 'ltr' | 'rtl'
  pluralizationRule?: Exclude<VueI18nOptions['pluralizationRules'], undefined>[string]
}

export const locales: Record<SupportedLanguages, Locale> = {
  ar: {
    label: 'العربية',
    direction: 'rtl'
  },
  ca: {
    label: 'Català',
    direction: 'ltr'
  },
  'ca@valencia': {
    label: 'Català (Valencia)',
    direction: 'ltr'
  },
  cs: {
    label: 'Čeština',
    direction: 'ltr'
  },
  de: {
    label: 'Deutsch',
    direction: 'ltr'
  },
  en_GB: {
    label: 'English (UK)',
    direction: 'ltr'
  },
  en_US: {
    label: 'English (United-States)',
    direction: 'ltr'
  },
  eo: {
    label: 'Esperanto',
    direction: 'ltr'
  },
  es: {
    label: 'Español',
    direction: 'ltr'
  },
  eu: {
    label: 'Euskara',
    direction: 'ltr'
  },
  fr_FR: {
    label: 'Français',
    direction: 'ltr'
  },
  gl: {
    label: 'Galego',
    direction: 'ltr'
  },
  hu: {
    label: 'Magyar',
    direction: 'ltr'
  },
  it: {
    label: 'Italiano',
    direction: 'ltr'
  },
  ja_JP: {
    label: '日本語',
    direction: 'ltr'
  },
  kab_DZ: {
    label: 'Taqbaylit',
    direction: 'ltr'
  },
  ko_KR: {
    label: '한국어',
    direction: 'ltr'
  },
  nb_NO: {
    label: 'Bokmål',
    direction: 'ltr'
  },
  nn_NO: {
    label: 'Nynorsk',
    direction: 'ltr'
  },
  nl: {
    label: 'Nederlands',
    direction: 'ltr'
  },
  oc: {
    label: 'Occitan',
    direction: 'ltr'
  },
  pl: {
    label: 'Polski',
    direction: 'ltr',
    pluralizationRule: (n, choices) => {
      // 0 rowerow | 1 rower | 2-4 rowery | 5-21 rowerow
      // 1 rower | 2-4 rowery | 5-21 rowerow

      const isFew = (n % 10 >= 2 && n % 10 <= 4) && (n % 100 < 10 || n % 100 >= 20)

      if (choices === 3) {
        if (n === 0) return 2
        if (n === 1) return 0
        return isFew ? 1 : 2
      }

      if (n === 0 || n === 1) return n
      return isFew ? 2 : 3
    }
  },
  pt_BR: {
    label: 'Português (Brasil)',
    direction: 'ltr'
  },
  pt_PT: {
    label: 'Português (Portugal)',
    direction: 'ltr'
  },
  ru: {
    label: 'Русский',
    direction: 'ltr'
  },
  sq: {
    label: 'Shqip',
    direction: 'ltr'
  },
  zh_Hans: {
    label: '中文(简体)',
    direction: 'ltr'
  },
  zh_Hant: {
    label: '中文(繁體)',
    direction: 'ltr'
  },
  fa_IR: {
    label: 'فارسی',
    direction: 'rtl'
  },
  ml: {
    label: 'മലയാളം',
    direction: 'ltr'
  },
  sv: {
    label: 'Svenska',
    direction: 'ltr'
  },
  el: {
    label: 'Ελληνικά',
    direction: 'ltr'
  }
}
