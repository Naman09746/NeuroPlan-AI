import { create } from 'zustand'
import apiClient from '../api/client'

export const useConfigStore = create((set) => ({
    aiHealth: { status: 'loading', message: 'Checking Neural Engine...' },
    isLoading: false,

    fetchAIHealth: async () => {
        set({ isLoading: true })
        try {
            const response = await apiClient.get('/health/ai')
            set({ aiHealth: response.data, isLoading: false })
        } catch (error) {
            set({ 
                aiHealth: { 
                    status: 'offline', 
                    message: 'Engine Offline',
                    error: 'Connection failed' 
                }, 
                isLoading: false 
            })
        }
    }
}))
