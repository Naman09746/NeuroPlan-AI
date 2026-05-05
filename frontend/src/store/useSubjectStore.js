import { create } from 'zustand'
import apiClient from '../api/client'

export const useSubjectStore = create((set, get) => ({
  subjects: [],
  topicsBySubject: {}, // { subjectId: [topics] }
  isLoading: false,
  isDecomposing: false,
  error: null,

  fetchSubjects: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/subjects/')
      set({ subjects: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch subjects', isLoading: false })
    }
  },

  createSubject: async (name, color, target_level = 'intermediate') => {
    try {
      const response = await apiClient.post('/subjects/', { name, color, target_level })
      set((state) => ({ subjects: [...state.subjects, response.data] }))
      return response.data
    } catch (err) {
      set({ error: 'Failed to create subject' })
      throw err
    }
  },

  deleteSubject: async (id) => {
    try {
      await apiClient.delete(`/subjects/${id}`)
      set((state) => ({ subjects: state.subjects.filter((s) => s.id !== id) }))
    } catch (err) {
      set({ error: 'Failed to delete subject' })
      throw err
    }
  },

  fetchTopics: async (subjectId) => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get(`/topics/subject/${subjectId}`)
      set((state) => ({
        topicsBySubject: {
          ...state.topicsBySubject,
          [subjectId]: response.data
        },
        isLoading: false
      }))
    } catch (err) {
      set({ error: 'Failed to fetch topics', isLoading: false })
    }
  },

  bulkCreateTopics: async (subjectId, topics) => {
    set({ isLoading: true })
    try {
      const response = await apiClient.post(`/topics/bulk/${subjectId}`, topics)
      set((state) => ({
        topicsBySubject: {
          ...state.topicsBySubject,
          [subjectId]: [...(state.topicsBySubject[subjectId] || []), ...response.data]
        },
        isLoading: false
      }))
      return response.data
    } catch (err) {
      set({ error: 'Failed to bulk create topics', isLoading: false })
      throw err
    }
  },

  decomposeSubject: async (subjectId, context = '') => {
    set({ isDecomposing: true })
    try {
      const response = await apiClient.post(
        `/topics/decompose/${subjectId}`,
        null,
        { params: { context } }
      )
      set((state) => ({
        topicsBySubject: {
          ...state.topicsBySubject,
          [subjectId]: response.data
        },
        isDecomposing: false
      }))
      return response.data
    } catch (err) {
      set({ error: 'AI decomposition failed', isDecomposing: false })
      throw err
    }
  }
}))
