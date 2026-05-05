import { create } from 'zustand'
import apiClient from '../api/client'

export const useStudyCardStore = create((set, get) => ({
  cards: {}, // { topicId: cardData }
  isLoading: false,
  isRegenerating: false,
  error: null,

  fetchCard: async (topicId) => {
    // Skip if already cached
    if (get().cards[topicId]) return get().cards[topicId]
    
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get(`/study-cards/${topicId}`)
      set((state) => ({
        cards: { ...state.cards, [topicId]: response.data },
        isLoading: false
      }))
      return response.data
    } catch (err) {
      set({ error: 'Failed to load study card', isLoading: false })
      throw err
    }
  },

  regenerateCard: async (topicId) => {
    set({ isRegenerating: true, error: null })
    try {
      const response = await apiClient.post(`/study-cards/${topicId}/regenerate`)
      set((state) => ({
        cards: { ...state.cards, [topicId]: response.data },
        isRegenerating: false
      }))
      return response.data
    } catch (err) {
      set({ error: 'Failed to regenerate study card', isRegenerating: false })
      throw err
    }
  },

  streamCard: async (topicId) => {
    set({ isLoading: true, error: null })
    try {
      const token = localStorage.getItem('token')
      const eventSource = new EventSource(
        `${import.meta.env.VITE_API_URL}/study-cards/${topicId}/stream?token=${token}`
      )
      
      let fullContent = ''
      
      eventSource.onmessage = (event) => {
        if (event.data === '[DONE]') {
          eventSource.close()
          set({ isLoading: false })
          return
        }
        
        fullContent += event.data
        try {
          // Attempt to parse partially (this is hard for JSON, so we just store raw for now)
          // or just show a loading indicator with "Synthesizing..."
          set((state) => ({
            cards: { 
              ...state.cards, 
              [topicId]: { ...state.cards[topicId], isStreaming: true, raw: fullContent } 
            }
          }))
        } catch (e) {}
      }
      
      eventSource.onerror = () => {
        eventSource.close()
        set({ isLoading: false })
      }
      
      return eventSource
    } catch (err) {
      set({ error: 'Streaming failed', isLoading: false })
    }
  }
}))
