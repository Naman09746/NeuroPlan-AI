import { create } from 'zustand'
import apiClient from '../api/client'

export const usePlanStore = create((set, get) => ({
  plans: [],
  activePlan: null,
  isLoading: false,
  error: null,

  fetchPlans: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/plans/')
      set({ plans: response.data, isLoading: false })
      
      // Auto-select active plan if none selected
      if (!get().activePlan && response.data.length > 0) {
        set({ activePlan: response.data[0] })
      }
    } catch (err) {
      set({ error: 'Failed to fetch plans', isLoading: false })
    }
  },

  generatePlan: async (planData) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post('/plans/generate', planData)
      set((state) => ({ 
        plans: [response.data, ...state.plans],
        activePlan: response.data,
        isLoading: false 
      }))
      return response.data
    } catch (err) {
      set({ 
        error: err.response?.data?.detail || 'Plan generation failed', 
        isLoading: false 
      })
      throw err
    }
  },

  setActivePlan: (plan) => set({ activePlan: plan }),

  reschedulePlan: async (planId) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.post(`/reschedule/${planId}/reschedule`)
      set({ isLoading: false })
      return response.data
    } catch (err) {
      set({ 
        error: err.response?.data?.detail || 'Rescheduling failed', 
        isLoading: false 
      })
      throw err
    }
  }
}))
