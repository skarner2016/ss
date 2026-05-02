<template>
  <router-view />
</template>

<style>
:root {
  --color-primary: #ff2442;
  --color-primary-light: #fff0f2;
  --color-primary-border: #ffccd3;
  --color-bg: #f5f5f5;
  --color-card: #ffffff;
  --color-text-primary: #1a1a1a;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-divider: #f0f0f0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', Roboto, sans-serif;
  background: var(--color-bg);
  color: var(--color-text-primary);
}

a {
  text-decoration: none;
  color: inherit;
}
</style>
