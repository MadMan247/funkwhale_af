---
layout: page
---

<script setup lang="ts">
import FormsA11y from '@/examples/Forms.a11y.vue'
</script>

<div id="is-overview-page" />

# Forms

### Form fields

- [Input](components/ui/input)
- [Pill](components/ui/pill) / [Pills](components/ui/pills)
- [Select](components/ui/select)
- [Slider](components/ui/slider)
- [Textarea](components/ui/textarea)
- [Toggle](components/ui/toggle)

### Other useful components

- [Button](components/ui/button)
- [Layout](components/ui/layout)
- [Heading](components/ui/heading)

::: tip Using forms

## Accessible forms

- Help the user fill a form by providing guidance, suggestions and appropriate error messages ([`Alert` component](components/ui/alert)). Use the `role` prop to make the announcement more polite or more intrusive. Test with a screenreader.
- Make fields in a form predictable by announcing their effects and cross-connections early. Never just disable a field that is incompatible with the data a user entered in other fields - always make the reason for automatic changes and input errors very clear.
- Provide easy steps and instructions for recovery from errors and incompatibilities.
- Provide Undo and/or Reset functionality where appropriate.

<FormsA11y />

---

### Model

<<<@/examples/Forms.a11y.vue#model{ts}

### Template

<<<@/examples/Forms.a11y.vue#snippet{vue-html}

[Test these components in isolation against WCAG2 criteria](/maintaining-accessibility#form-fields)
:::
