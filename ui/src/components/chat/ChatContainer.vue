<template>
  <div class="flex h-screen w-full flex-col bg-gray-50 p-4">
    <slot name="header"></slot>
    <slot name="messages"></slot>
    <slot name="input"></slot>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped></style>
