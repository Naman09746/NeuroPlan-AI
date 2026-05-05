import { create } from 'zustand'
import apiClient from '../api/client'

export const useTaskStore = create((set, get) => ({
  todayTasks: [],
  weekTasks: [],
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

  fetchWeekTasks: async (planId) => {
    if (!planId) return
    set({ isLoading: true })
    try {
      const response = await apiClient.get(`/tasks/week/${planId}`)
      set({ weekTasks: response.data, isLoading: false })
    } catch (err) {
      set({ error: 'Failed to fetch weekly schedule', isLoading: false })
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
  },

  updateHeartbeat: async (taskId, minutes) => {
    try {
      await apiClient.patch(`/tasks/${taskId}/heartbeat`, null, {
        params: { actual_minutes: minutes }
      })
    } catch (err) {
      console.error('Failed to sync heartbeat')
    }
  },

  updateNotes: async (taskId, notes) => {
    try {
      const response = await apiClient.patch(`/tasks/${taskId}/notes`, null, {
        params: { notes }
      })
      return response.data
    } catch (err) {
      set({ error: 'Failed to update notes' })
      throw err
    }
  }
}))
