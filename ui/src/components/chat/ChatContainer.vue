<template>
  <div class="chat-container flex h-full w-full flex-col items-center p-4">
    <slot name="header"></slot>
    <slot name="messages"></slot>
    <slot name="input"></slot>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped></style>
