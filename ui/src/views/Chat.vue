<template>
  <div class="flex h-full w-full">
    <!-- <div
      :class="[
        'flex-shrink-0',
        'overflow-y-auto',
        'border-r',
        'bg-gray-100',
        'transition-width',
        'duration-300',
        'ease-in-out',
        showHistory ? 'w-64' : 'w-16',
      ]"
    >
      <div class="p-4">
        <button
          @click="toggleHistory"
          class="w-full rounded-lg bg-blue-500 px-4 py-2 text-white transition hover:bg-blue-600"
        >
          <span v-if="showHistory">收起历史</span>
          <span v-else>展开历史</span>
        </button>
      </div>
      <ChatHistory
        v-if="showHistory"
        :history-sessions="historySessions"
        :current-session-id="currentSessionId"
        @select-session="handleSelectSession"
        @create-new-chat="handleCreateNewChat"
      />
    </div> -->

    <!-- Main Chat Area -->
    <div class="flex flex-1 flex-col">
      <ChatContainer>
        <template #header>
          <ChatHeader />
        </template>
        <template #messages>
          <ChatMessages :messages="messages" />
        </template>
        <template #input>
          <ChatInput @send-message="handleSendMessage" />
        </template>
        <div @click="changeAccept">111->{{ current.interrupt }}</div>
      </ChatContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import ChatContainer from '@/components/chat/ChatContainer.vue'
import ChatHeader from '@/components/chat/ChatHeader.vue'
import ChatMessages from '@/components/chat/ChatMessages.vue'
import ChatInput from '@/components/chat/ChatInput.vue'
import ChatHistory from '@/components/chat/ChatHistory.vue'
import type { AIMessage, AIStreamEvent, Message } from '@/types/chat'
import { streamFetch } from '@/utils/http/sse'

interface HistorySession {
  id: string
  preview: string
}

const messages = ref<Message[]>([
  {
    role: 'Human',
    content: `你好请给我一些md示例`,
  },

  {
    role: 'AI',
    // thinkingContent: '',
    content: '',
    observation: [
      {
        type: 'references',
        data: [
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股份有限公司软件开发管理制度20240719',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股管理制度20240719',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股份有',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股份有限公司软件开发管理',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股份有限公司软件开发管理制度20240719',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
          {
            score: 0.23173391819000244,
            imagesUrl: [],
            documentName: '千金药业股份',
            title:
              '千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队',
            content:
              '【文档名】:千金药业股份有限公司软件开发管理制度20240719\n【标题】:千金药业股份有限公司软件开发管理制度 （三）项目经理|（四）设计团队|（五）开发团队|（六）测试团队\n【正文】:负责制定详细的项目计划，包括目标、范围、预算、时间表和里程碑；负责组建合适的项目团队，包括开发人员、测试人员、设计师等，明确团队成员的职责和分工，确保团队的高效协作；负责定期监控项目进度，确保各项任务按计划完成，使用项目管理工具（如甘特图、看板）跟踪任务状态，及时识别并解决进度偏差，调整计划以应对变化；负责组织代码审查、测试和验收等活动，确保软件代码质量；负责定期识别和评估项目风险，制定相关应对策略。\n（四）设计团队\n根据需求规格说明书进行系统设计，包括架构设计、数据库设计、界面设计、接口设计等，并输出设计文档。\n（五）开发团队\n参加需求和设计评审会议，确保对项目的整体理解和设计意图的清晰把握，按照设计文档使用适当的开发框架、工具和编程语言进行开发实现，遵循编码规范，保证代码质量。遵循安全编码规范，防止常见安全漏洞（如 SQL注入、XSS、弱密码等）。\n（六）测试团队\n负责搭建和配置测试环境，确保与生产环境尽可能一致，并准备测试数据；制定测试计划，设计测试用例，确保测试用例覆盖所有功能需求、非功能需求和边界条件；负责使用自动化测试工具，执行自动化测试，提高测试效率。\n',
          },
        ],
      },
      {
        type: 'mcp',
        data: {
          name: '查询流程列表',
          input: { aaa: 111 },
          result: {
            userId: '01202104027',
            workflowId: 'leave',
            workflowFormData: {
              reason: '21',
              endDate: '2025-05-16',
              type: '事假',
              startDate: '2025-05-08',
            },
          },
        },
      },
      {
        type: 'mcp',
        data: { name: '创建流程', input: { aaa: 222 }, result: "{res:'sss'}" },
      },
    ],
    streaming: false,
    nodeStatus: 'LLM',
  },
])

const current = reactive<{
  aiMessage: AIMessage | null
  interrupt: any
  sessionId: string
}>({
  aiMessage: null,
  interrupt: null,
  sessionId: '',
})

const changeAccept = () => {
  current.interrupt[0].value.user_accept = true
  console.log(111)
}

const ctrl = ref()

// 新增历史记录相关的响应式状态
const showHistory = ref(true) // 控制历史记录侧边栏的显示与隐藏
const currentSessionId = ref('session-1') // 追踪当前活跃的聊天会话
const historySessions = ref<HistorySession[]>([
  { id: 'session-1', preview: '会话 1: 你好' },
  { id: 'session-2', preview: '会话 2: 关于AI的问题' },
  { id: 'session-3', preview: '会话 3: 技术讨论' },
])

// 新增历史记录管理函数
const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const handleSelectSession = (id: string) => {
  currentSessionId.value = id
  // 在这里，您通常会从数据源加载所选会话的消息。
  // 在此示例中，我们仅记录它，如果它是不同的会话，则可能重置消息。
  console.log(`Selected session: ${id}`)
}

const handleCreateNewChat = () => {
  const newId = `session-${historySessions.value.length + 1}`
  historySessions.value.push({ id: newId, preview: `新会话 ${historySessions.value.length + 1}` })
  currentSessionId.value = newId
  messages.value = [] // 清空当前消息，开始新会话
  console.log('Created new chat session')
}

const handleSendMessage = (input: string) => {
  ctrl.value?.abort()
  ctrl.value = new AbortController()
  let resume = null
  if (current.interrupt) {
    resume = { ...current.interrupt[0].value }
    // current.interrupt = null
  }
  messages.value.push({ content: input, role: 'Human' })

  streamFetch('/chat', {
    method: 'POST',
    body: JSON.stringify({
      messages: messages.value,
      session_id: current.sessionId,
      resume,
    }),
    signal: ctrl.value.signal,
    async onopen(res) {
      console.log('连接开始>', res)
      current.aiMessage = { role: 'AI', content: '' }
      messages.value.push(current.aiMessage)
    },
    async onmessage(ev) {
      if (!ev.event) return
      if (!current.aiMessage) {
        console.warn('aiMessage not initialized before streaming')
        return
      }
      if (current.interrupt) {
        current.interrupt = null
      }
      if (ev.event == 'session_id') {
        current.sessionId = ev.data
      } else if (ev.event == 'message') {
        current.aiMessage.content += ev.data
      } else if (['tool_start', 'tool_end'].includes(ev.event)) {
        const res: { name: string } = JSON.parse(ev.data)
        current.aiMessage.content += `\n${ev.event}:${res.name}\n`
      } else {
        try {
          const res: any = JSON.parse(ev.data)
          current.aiMessage.content += `\n${ev.event}:\n\`\`\`json\n${ev.data}\n\`\`\`\n`
          if (ev.event == 'interrupt') {
            current.interrupt = res
          }
        } catch (err) {
          console.error('解析json失败:' + ev)
        }
      }
    },
    onclose() {},
    onerror(err) {
      console.log('发生错误->')
      throw err
    },
  })
}
import { useTypewriter } from '@/components/markdown/hooks/useTypewriter'
const { startTyping } = useTypewriter()
onMounted(() => {
  messages.value = []
  // current.aiMessage = messages.value[messages.value.length - 1] as AIMessage
  let template = `
# Markdown 常用样式示例
## 1. 标题
# H1
## H2
### H3

## 2. 文本样式
**加粗文本**
*斜体文本*
~~删除线文本~~
这是\`行内代码\`的示例
长文本长文本长文本长文本长文本长文本长文本长文本长文本长文本

## 3. 列表
### 无序列表
- 项目1
- 项目2
- 子项目2.1
- 子项目2.2

### 有序列表
1. 第一项
2. 第二项
1. 子项2.1
2. 子项2.2

## 4. 链接与图片
[普通链接](https://example.com)
![图片描述](https://example.com/image.jpg)

## 5. 表格
| 左对齐 | 居中对齐 | 右对齐 |
| :------ | :------: | ------: |
| 单元格 | 单元格 | 单元格 |
| 数据1 | 数据2 | 数据3 |

## 6. 代码块
\`\`\`javascript
// JavaScript 示例
function hello() {
console.log("Hello World!");
}
\`\`\`
## 7. emoji
\`:smile:\` -> :smile:
## 8. 上标和下标
\`E=mc^2^\` -> E=mc^2^

\`H~2~O\` -> H~2~O
## 8. ehcarts

\`\`\`echarts
{
"title": {
"text": "ECharts 示例图表"
},
"tooltip": {},
"legend": {
"data": ["销量"]
},
"xAxis": {
"data": ["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋"]
},
"yAxis": {},
"series": [{
"name": "销量",
"type": "bar",
"data": [5, 20, 36, 10, 10]
}]
}
\`\`\`
## 9. 流程图
\`\`\`mermaid
graph TD
A[开始] --> B(节点)
B --> C{分支节点}
C -->|描述| D[节点]
C -->|描述| E[节点]
C -->|描述| F[节点]
\`\`\`
## 视频
\`\`\`video
{
"url":"https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4https://ai-assistant-obs.qjyy.com/Vedio/video1.mp4"
}
\`\`\`
## iframe
\`\`\`iframe
{
"url":"https://www.qjyy.com"
}
\`\`\``
  //   template = `
  // ## 9. 流程图
  // \`\`\`mermaid
  // graph TD
  // A[开始] --> B(节点)
  // B --> C{分支节点}
  // C -->|描述| D[节点]
  // C -->|描述| E[节点]
  // C -->|描述| F[节点]
  // \`\`\``
  // startTyping(template, 100, [1, 10], (text) => {
  //   if (current.aiMessage) {
  //     current.aiMessage.content += text
  //   }
  // })
})
</script>

<style lang="scss" scoped>
/* 您可能需要为侧边栏宽度添加过渡效果 */
.flex-shrink-0 {
  transition: width 0.3s ease-in-out;
}
</style>
