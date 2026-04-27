import React, { useState, useEffect } from 'react'
import { Brain, Clock, ChevronRight, CheckCircle2, XCircle, Award, Zap } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'
import apiClient from '@/api/client'
import toast from 'react-hot-toast'

const ProbeQuizModal = ({ isOpen, onClose, taskId, topicId, topicName }) => {
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState(null)
  const [timeLeft, setTimeLeft] = useState(15)

  useEffect(() => {
    if (isOpen && topicId) {
      fetchProbe()
    } else {
        resetState()
    }
  }, [isOpen, topicId])

  useEffect(() => {
    if (questions.length > 0 && !result && timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000)
      return () => clearTimeout(timer)
    } else if (timeLeft === 0 && !result) {
      handleNext()
    }
  }, [timeLeft, questions, result])

  const fetchProbe = async () => {
    setIsLoading(true)
    try {
      const response = await apiClient.get(`/probe/${topicId}`)
      setQuestions(response.data.questions)
      setIsLoading(false)
    } catch (err) {
      toast.error('Failed to generate neural probe')
      onClose()
    }
  }

  const resetState = () => {
      setQuestions([])
      setCurrentIndex(0)
      setAnswers({})
      setResult(null)
      setTimeLeft(15)
  }

  const handleAnswer = (index) => {
    setAnswers({ ...answers, [currentIndex]: index })
    setTimeout(handleNext, 500)
  }

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1)
      setTimeLeft(15)
    } else {
      submitResults()
    }
  }

  const submitResults = async () => {
    setIsSubmitting(true)
    let correct = 0
    questions.forEach((q, i) => {
      if (answers[i] === q.correct_index) correct++
    })

    try {
      const response = await apiClient.post('/probe/result', {
        task_id: taskId,
        correct_count: correct,
        total_count: questions.length
      })
      setResult(response.data)
    } catch (err) {
      toast.error('Sync failed')
    } finally {
      setIsSubmitting(false)
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
          className="absolute inset-0 bg-surface-900/80 backdrop-blur-xl"
        />

        <motion.div 
          initial={{ opacity: 0, scale: 0.9, y: 40 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 40 }}
          className="relative w-full max-w-lg bg-white rounded-[40px] shadow-2xl overflow-hidden p-10"
        >
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center text-center space-y-6">
              <div className="w-20 h-20 bg-primary-50 rounded-full flex items-center justify-center animate-bounce">
                <Brain className="w-10 h-10 text-primary-600" />
              </div>
              <div>
                <h3 className="text-xl font-black text-surface-900 tracking-tight">Initializing Knowledge Probe</h3>
                <p className="text-xs font-bold text-surface-400 uppercase tracking-widest mt-2">Connecting to neural matrix of {topicName}</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-8 text-center py-6">
              <div className={clsx(
                "w-24 h-24 mx-auto rounded-full flex items-center justify-center shadow-2xl",
                result.verdict === 'passed' ? "bg-emerald-50 text-emerald-600 shadow-emerald-100" : "bg-red-50 text-red-600 shadow-red-100"
              )}>
                {result.verdict === 'passed' ? <Award className="w-12 h-12" /> : <XCircle className="w-12 h-12" />}
              </div>
              
              <div>
                <h2 className="text-3xl font-black text-surface-900 tracking-tighter">
                  {result.verdict === 'passed' ? 'Synchronization Successful' : 'Neural Inconsistency Detected'}
                </h2>
                <p className="text-surface-500 font-medium mt-3 px-4 leading-relaxed">
                  {result.message}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                 <div className="p-6 bg-surface-50 rounded-3xl">
                    <div className="text-2xl font-black text-surface-900">{result.score}%</div>
                    <div className="text-[10px] font-black text-surface-400 uppercase tracking-widest mt-1">Probe Score</div>
                 </div>
                 <div className="p-6 bg-primary-50 rounded-3xl">
                    <div className="text-2xl font-black text-primary-600">{result.new_mastery}%</div>
                    <div className="text-[10px] font-black text-primary-400 uppercase tracking-widest mt-1">Updated Mastery</div>
                 </div>
              </div>

              <Button onClick={onClose} className="w-full py-4 rounded-2xl text-base">Accept Alignment</Button>
            </div>
          ) : (
            <div className="space-y-10">
              <div className="flex items-center justify-between">
                <div className="flex gap-1">
                  {questions.map((_, i) => (
                    <div 
                      key={i} 
                      className={clsx(
                        "h-1.5 rounded-full transition-all duration-300",
                        i === currentIndex ? "w-8 bg-primary-600" : 
                        answers[i] !== undefined ? "w-4 bg-emerald-400" : "w-4 bg-surface-100"
                      )}
                    />
                  ))}
                </div>
                <div className="flex items-center gap-2 bg-surface-900 text-white px-4 py-1.5 rounded-xl text-xs font-black tabular-nums shadow-lg">
                  <Clock className="w-3 h-3 text-primary-400" />
                  {timeLeft}s
                </div>
              </div>

              <div className="space-y-4">
                <span className="text-[10px] font-black text-primary-600 uppercase tracking-[0.2em]">Verification Probe {currentIndex + 1}/{questions.length}</span>
                <h3 className="text-2xl font-black text-surface-900 tracking-tight leading-tight">
                  {questions[currentIndex]?.question}
                </h3>
              </div>

              <div className="grid gap-3">
                {questions[currentIndex]?.options.map((opt, i) => (
                  <button 
                    key={i}
                    onClick={() => handleAnswer(i)}
                    className={clsx(
                      "w-full p-6 text-left rounded-3xl border-2 transition-all font-bold text-sm",
                      answers[currentIndex] === i 
                        ? "bg-primary-600 border-primary-600 text-white shadow-xl shadow-primary-200" 
                        : "bg-white border-surface-50 hover:border-primary-100 hover:bg-primary-50/20 text-surface-700"
                    )}
                  >
                    <div className="flex items-center gap-4">
                      <div className={clsx(
                         "w-8 h-8 rounded-xl flex items-center justify-center border-2 text-[10px] font-black transition-all",
                         answers[currentIndex] === i ? "bg-white text-primary-600 border-white" : "bg-surface-50 text-surface-400 border-surface-100"
                      )}>
                        {String.fromCharCode(65 + i)}
                      </div>
                      {opt}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

export default ProbeQuizModal
