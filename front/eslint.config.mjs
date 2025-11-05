import vueI18n from '@intlify/eslint-plugin-vue-i18n'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import html from 'eslint-plugin-html'
import vue from 'eslint-plugin-vue'
import globals from 'globals'
import jsoncParser from 'jsonc-eslint-parser'

export default defineConfigWithVueTs(
  vueTsConfigs.recommended,
  vue.configs['flat/recommended'],
  vueI18n.configs['flat/recommended'],

  {
    files: [['./src', '*.vue']],
    extends: [vueTsConfigs.recommendedTypeChecked]
  },

  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2015,
        SharedArrayBuffer: 'readonly',
        Atomics: 'readonly'
      }
    },

    plugins: {
      html
    },

    rules: {
      // NOTE: Nicer for the eye
      'operator-linebreak': ['error', 'before'],

      // NOTE: We have a logger instance
      'no-console': 'error',

      // NOTE: Handled by typescript
      '@typescript-eslint/no-unused-vars': 'off',
      'no-use-before-define': 'off',
      'no-unused-vars': 'off',
      'no-redeclare': 'off',
      'no-undef': 'off',

      // NOTE: i18n
      '@intlify/vue-i18n/no-deprecated-i18n-component': 'error',
      '@intlify/vue-i18n/valid-message-syntax': 'error',
      '@intlify/vue-i18n/no-i18n-t-path-prop': 'error',
      '@intlify/vue-i18n/no-missing-keys': 'error',
      '@intlify/vue-i18n/no-dynamic-keys': 'error',
      '@intlify/vue-i18n/no-unused-keys': [
        'error',
        {
          extensions: ['.ts', '.vue'],
          enableFix: true
        }
      ],

      // TODO (wvffle): Remove after VUI and #1618
      'vue/multi-word-component-names': 'off',
      'import/extensions': 'off',

      // TODO (wvffle): Remove after embedded player migration
      '@typescript-eslint/no-this-alias': 'off',

      // TODO (wvffle): Remove after API Client
      '@typescript-eslint/no-explicit-any': 'off',

      // Configure TypeScript style
      'comma-dangle': ['error', 'never'],

      // TODO: How should these new findings be handled?
      'vue/prop-name-casing': 'off',
      'vue/require-default-prop': 'off'
    },

    settings: {
      'vue-i18n': {
        localeDir: './src/locales/*.json',
        messageSyntaxVersion: '^9.0.0'
      }
    }
  },

  {
    files: ['public/embed.html'],

    rules: {
      'vue/comment-directive': 'off'
    }
  },
  {
    files: ['**/*.json'],

    languageOptions: {
      parser: jsoncParser
    }
  },
  {
    files: ['src/locales/*.json'],

    rules: {
      'no-irregular-whitespace': 'off'
    }
  },

  {
    ignores: ['src/locales/*.json', '**/dist', '**/stats.html', 'ui-docs/.vitepress', 'ui-docs/components']
  }
)
