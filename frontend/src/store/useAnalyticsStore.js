import { create } from 'zustand'
import apiClient from '../api/client'

export const useAnalyticsStore = create((set) => ({
  overview: null,
  trends: [],
  distribution: [],
  mastery: [],
  isLoading: false,
  error: null,

  fetchOverview: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/analytics/overview')
      set({ overview: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch analytics overview', isLoading: false })
    }
  },

  fetchTrends: async (days = 30) => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get(`/analytics/trends?days=${days}`)
      set({ trends: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch efficiency trends', isLoading: false })
    }
  },

  fetchDistribution: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/analytics/distribution')
      set({ distribution: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch subject distribution', isLoading: false })
    }
  },

  fetchMastery: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/analytics/mastery')
      set({ mastery: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch knowledge mastery', isLoading: false })
    }
  },

  fetchAll: async () => {
    set({ isLoading: true })
    try {
      const [overview, trends, distribution, mastery] = await Promise.all([
        apiClient.get('/analytics/overview'),
        apiClient.get('/analytics/trends'),
        apiClient.get('/analytics/distribution'),
        apiClient.get('/analytics/mastery')
      ])
      set({ 
        overview: overview.data, 
        trends: trends.data, 
        distribution: distribution.data, 
        mastery: mastery.data,
        isLoading: false 
      })
    } catch (err) {
      set({ error: 'Failed to fetch full analytics data', isLoading: false })
    }
  }
}))
