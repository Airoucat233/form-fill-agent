type Message = HumanMessage | AIMessage

interface HumanMessage {
  id?: string
  role: 'Human'
  content: string
}

interface AIMessage {
  id?: string
  role: 'AI'
  content: string
}

export type { HumanMessage, AIMessage, Message }
