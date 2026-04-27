import { create } from 'zustand'
import apiClient from '../api/client'

export const useTaskStore = create((set, get) => ({
  todayTasks: [],
  isLoading: false,
  error: null,

  fetchTodayTasks: async (planId) => {
    if (!planId) return
    set({ isLoading: true })
    try {
      const response = await apiClient.get(`/tasks/today/${planId}`)
      set({ todayTasks: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch tasks', isLoading: false })
    }
  },

  updateTaskStatus: async (taskId, status, actualMinutes) => {
    try {
      const response = await apiClient.put(`/tasks/${taskId}/progress`, {
        status,
        actual_minutes: actualMinutes
      })
      
      // Optimistic update
      set((state) => ({
        todayTasks: state.todayTasks.map((t) => 
          t.id === taskId ? response.data : t
        )
      }))

      return response.data
    } catch (err) {
      set({ error: 'Failed to update task' })
      throw err
    }
  }
}))
