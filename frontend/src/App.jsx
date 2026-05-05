import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import MainLayout from '@/components/layout/MainLayout'
import DashboardPage from '@/pages/DashboardPage'
import CurriculumPage from '@/pages/CurriculumPage'
import PlanPage from '@/pages/PlanPage'
import AnalyticsPage from '@/pages/AnalyticsPage'
import TestPage from '@/pages/TestPage'
import SettingsPage from '@/pages/SettingsPage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import StudySessionPage from '@/pages/StudySessionPage'
import OnboardingWizardPage from '@/pages/OnboardingWizardPage'
import { useAuthStore } from '@/store/useAuthStore'
import ErrorBoundary from '@/components/ui/ErrorBoundary'

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading, fetchMe } = useAuthStore()
  
  useEffect(() => {
    if (isAuthenticated) {
      fetchMe()
    }
  }, [])

  if (isLoading && !isAuthenticated) {
    return <div className="h-screen w-screen flex items-center justify-center bg-surface-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <div className="min-h-screen">
          <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route path="/study/session/:taskId" element={
            <ProtectedRoute>
              <StudySessionPage />
            </ProtectedRoute>
          } />

          <Route path="/test/:topicId" element={
            <ProtectedRoute>
              <TestPage />
            </ProtectedRoute>
          } />

          <Route path="/onboarding" element={
            <ProtectedRoute>
              <OnboardingWizardPage />
            </ProtectedRoute>
          } />
          
          <Route path="/*" element={
            <ProtectedRoute>
              <MainLayout>
                <Routes>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/subjects" element={<CurriculumPage />} />
                  <Route path="/plan" element={<PlanPage />} /> 
                  <Route path="/analytics" element={<AnalyticsPage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </MainLayout>
            </ProtectedRoute>
          } />
        </Routes>
        <Toaster position="bottom-right" toastOptions={{
          style: {
            borderRadius: '16px',
            background: '#fff',
            color: '#0f172a',
            fontWeight: '600',
            boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.07)',
          },
        }} />
        </div>
      </ErrorBoundary>
    </Router>
  )
}

export default App
