import { create } from 'zustand'
import apiClient from '../api/client'

export const useCoachingStore = create((set) => ({
  notifications: [],
  isLoading: false,
  error: null,

  fetchNotifications: async () => {
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/coaching/notifications')
      set({ notifications: response.data, isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  markAsRead: async (eventId) => {
    try {
      await apiClient.post(`/coaching/notifications/${eventId}/read`)
      set((state) => ({
        notifications: state.notifications.map((n) =>
          n.id === eventId ? { ...n, is_read: true } : n
        ),
      }))
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  },
}))
