import React, { useState } from 'react'
import { Brain, Zap, X, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import apiClient from '@/api/client'
import toast from 'react-hot-toast'
import { motion, AnimatePresence } from 'framer-motion'

const QuickSetupModal = ({ isOpen, onClose, onSuccess }) => {
  const [subjectName, setSubjectName] = useState('')
  const [context, setContext] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleQuickSetup = async (e) => {
    e.preventDefault()
    if (!subjectName) return

    setIsLoading(true)
    try {
      const response = await apiClient.post('/onboarding/quick-setup', {
        subject_name: subjectName,
        context: context,
        color: '#6366f1' // Default indigo
      })
      toast.success(response.data.message)
      onSuccess()
      onClose()
    } catch (err) {
      toast.error('Quick setup failed')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-[60] flex items-center justify-center p-6">
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-surface-900/60 backdrop-blur-md"
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative w-full max-w-md bg-white rounded-[40px] shadow-2xl overflow-hidden p-10"
        >
          <div className="flex justify-between items-start mb-8">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-primary-100">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-2xl font-black text-surface-900 tracking-tight leading-none">Quick Protocol</h3>
                <p className="text-[10px] font-black text-primary-500 uppercase tracking-widest mt-2">AI-Powered Node Ingestion</p>
              </div>
            </div>
            <button onClick={onClose} className="p-2 hover:bg-surface-50 rounded-xl">
              <X className="w-6 h-6 text-surface-400" />
            </button>
          </div>

          <form onSubmit={handleQuickSetup} className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest ml-1">Subject Name</label>
              <Input 
                autoFocus
                placeholder="e.g. Quantum Computing" 
                value={subjectName}
                onChange={e => setSubjectName(e.target.value)}
                className="rounded-2xl py-4 border-2"
              />
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-black text-surface-400 uppercase tracking-widest ml-1">Context (Optional)</label>
              <textarea 
                placeholder="e.g. MIT OpenCourseWare, focus on hardware" 
                value={context}
                onChange={e => setContext(e.target.value)}
                className="w-full bg-surface-50 border-2 border-surface-100 rounded-2xl p-4 text-sm font-medium focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 outline-none min-h-[100px] transition-all"
              />
            </div>

            <Button 
                type="submit" 
                className="w-full py-4 rounded-2xl text-base bg-primary-600 shadow-xl shadow-primary-100" 
                isLoading={isLoading}
                disabled={!subjectName}
            >
              <Brain className="w-5 h-5 mr-1" />
              Initialize Neural Architecture
            </Button>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

export default QuickSetupModal
