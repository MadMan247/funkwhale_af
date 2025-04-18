<script setup>
import Alert from "~/components/ui/Alert.vue"
import Button from "~/components/ui/Button.vue"
</script>

```ts
import Alert from "~/components/ui/Alert.vue"
```

# Alert

| Prop    | Data type                                          | Required? | Default     | Description                      |
| ------- | -------------------------------------------------- | --------- | ----------- | -------------------------------- |
| `color` | `blue` \| `red` \| `purple` \| `green` \| `yellow` | No        | `secondary` | The color of the alert container |

## Alert colors

Funkwhale alerts support a range of pastel colors for visual appeal.

### Blue

```vue-html
<Alert blue>
  Blue alert
</Alert>
```

<Alert blue>
  Blue alert
</Alert>

### Red

```vue-html
<Alert red>
  Red alert
</Alert>
```

<Alert red>
  Red alert
</Alert>

### Purple

```vue-html
<Alert purple>
  Purple alert
</Alert>
```

<Alert purple>
  Purple burglar alert
</Alert>

### Green

```vue-html
<Alert green>
  Green alert
</Alert>
```

<Alert green>
  Green alert
</Alert>

### Yellow

```vue-html
<Alert yellow>
  Yellow alert
</Alert>
```

<Alert yellow>
  Yellow alert
</Alert>

## Alert actions

```vue-html{3-6}
<Alert blue>
  Awesome artist
  <template #actions>
    <Button disabled>Deny</Button>
    <Button>Got it</Button>
  </template>
</Alert>
```

<Alert blue>
  Awesome artist
  <template #actions>
    <Button disabled>Deny</Button>
    <Button>Got it</Button>
  </template>
</Alert>
