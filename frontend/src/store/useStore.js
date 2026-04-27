import { create } from 'zustand'

export const useStore = create((set) => ({
  subjects: [],
  topics: [],
  activePlan: null,
  
  setSubjects: (subjects) => set({ subjects }),
  setTopics: (topics) => set({ topics }),
  setActivePlan: (activePlan) => set({ activePlan }),
  
  // Placeholder for API integration
  fetchSubjects: async () => {
    // API call would go here
  }
}))
