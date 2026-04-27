import { create } from 'zustand'
import apiClient from '../api/client'

export const useTestStore = create((set) => ({
  activeTest: null,
  history: [],
  isLoading: false,
  isSubmitting: false,
  error: null,

  generateTest: async (topicId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get(`/tests/generate/${topicId}`)
      set({ activeTest: response.data, isLoading: false })
      return response.data
    } catch (err) {
      set({ error: 'Failed to initialize neural assessment', isLoading: false })
      throw err
    }
  },

  submitTest: async (results) => {
    set({ isSubmitting: true })
    try {
      const response = await apiClient.post('/tests/submit', results)
      set({ isSubmitting: false, activeTest: null })
      return response.data
    } catch (err) {
      set({ error: 'Failed to synchronize assessment results', isSubmitting: false })
      throw err
    }
  },

  fetchHistory: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/tests/history')
      set({ history: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch assessment history', isLoading: false })
    }
  },

  clearActiveTest: () => set({ activeTest: null })
}))
