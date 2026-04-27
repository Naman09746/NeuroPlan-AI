import { create } from 'zustand'
import apiClient from '../api/client'

export const useAuthStore = create((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      
      const userResponse = await apiClient.get('/auth/me')
      set({ user: userResponse.data, isAuthenticated: true, isLoading: false })
    } catch (err) {
      set({ 
        error: err.response?.data?.detail || 'Login failed', 
        isLoading: false,
        isAuthenticated: false 
      })
      throw err
    }
  },

  register: async (name, email, password) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.post('/auth/register', { name, email, password })
      // Auto login
      await useAuthStore.getState().login(email, password)
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Registration failed', isLoading: false })
      throw err
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, isAuthenticated: false })
    window.location.href = '/login'
  },

  fetchMe: async () => {
    if (!localStorage.getItem('token')) return
    set({ isLoading: true })
    try {
      const response = await apiClient.get('/auth/me')
      set({ user: response.data, isAuthenticated: true, isLoading: false })
    } catch (err) {
      set({ user: null, isAuthenticated: false, isLoading: false })
      localStorage.removeItem('token')
    }
  }
}))
