<template>
  <div class="h-[500px]" ref="echartsContainer"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  config: {
    type: String,
    default: '{}',
  },
})

const option = ref()
const echartsContainer = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

watch(
  () => props.config,
  (val) => {
    try {
      option.value = JSON.parse(val)
      if (chart && option.value) {
        chart.setOption(option.value)
      }
    } catch (err) {
      console.log('loading')
    }
  },
  { immediate: true },
)

onMounted(() => {
  if (!echartsContainer.value) return
  chart = echarts.init(echartsContainer.value)
  if (option.value) {
    chart.setOption(option.value)
  }

  const observer = new ResizeObserver(() => {
    chart?.resize()
  })
  observer.observe(echartsContainer.value)

  onBeforeUnmount(() => {
    observer.disconnect()
    chart?.dispose()
  })
})
</script>
