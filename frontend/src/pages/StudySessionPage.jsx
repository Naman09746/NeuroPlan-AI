import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Brain, Clock, ChevronRight, CheckCircle2, X, Zap, BookOpen, ExternalLink, HelpCircle, Play, Pause, RotateCcw } from 'lucide-react'
import { useStudyCardStore } from '@/store/useStudyCardStore'
import { useTaskStore } from '@/store/useTaskStore'
import { Button } from '@/components/ui/Button'
import ProbeQuizModal from '@/components/ui/ProbeQuizModal'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'
import apiClient from '@/api/client'

const StudySessionPage = () => {
  const { taskId } = useParams()
  const navigate = useNavigate()
  const { cards, fetchCard } = useStudyCardStore()
  const { todayTasks, updateTaskStatus } = useTaskStore()
  
  const [task, setTask] = useState(null)
  const [timeLeft, setTimeLeft] = useState(1500) // 25 minutes Pomodoro
  const [isActive, setIsActive] = useState(false)
  const [isProbeOpen, setIsProbeOpen] = useState(false)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    fetchTaskDetails()
  }, [taskId])

  const fetchTaskDetails = async () => {
    try {
      const response = await apiClient.get(`/tasks/${taskId}`)
      setTask(response.data)
      fetchCard(response.data.topic_id)
      setTimeLeft(response.data.planned_minutes * 60)
    } catch (err) {
      toast.error('Failed to load session')
      navigate('/')
    }
  }

  useEffect(() => {
    let interval = null
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => prev - 1)
      }, 1000)
    } else if (timeLeft === 0) {
      setIsActive(false)
      toast.success('Focus session complete!')
    }
    return () => clearInterval(interval)
  }, [isActive, timeLeft])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const handleComplete = () => {
    setIsProbeOpen(true)
  }

  if (!task) return null

  const card = cards[task.topic_id]

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-white flex flex-col">
      {/* Immersive Header */}
      <div className="p-8 flex items-center justify-between border-b border-white/5 bg-white/5 backdrop-blur-3xl sticky top-0 z-10">
        <div className="flex items-center gap-6">
          <button onClick={() => navigate('/')} className="p-3 hover:bg-white/10 rounded-2xl transition-all">
            <X className="w-6 h-6" />
          </button>
          <div className="h-10 w-px bg-white/10 hidden md:block" />
          <div>
            <h1 className="text-xl font-black tracking-tight">{task.topic_name}</h1>
            <p className="text-[10px] font-black text-primary-400 uppercase tracking-widest mt-1">
              Active Neural Encoding Protocol
            </p>
          </div>
        </div>

        <div className="flex items-center gap-10">
            <div className="hidden lg:flex flex-col items-end">
                <span className="text-[10px] font-black text-white/40 uppercase tracking-widest mb-1">Session Progress</span>
                <div className="flex gap-1">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className={clsx(
                            "h-1 rounded-full transition-all duration-500",
                            i <= (1.0 - timeLeft/(task.planned_minutes*60)) * 4 ? "w-8 bg-primary-500" : "w-4 bg-white/10"
                        )} />
                    ))}
                </div>
            </div>

            <div className="flex items-center gap-6 bg-white/5 border border-white/10 px-6 py-3 rounded-[24px]">
                <div className="text-3xl font-black tabular-nums tracking-tighter w-24">
                    {formatTime(timeLeft)}
                </div>
                <div className="flex gap-2">
                    <button 
                        onClick={() => setIsActive(!isActive)}
                        className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center hover:bg-primary-500 transition-all shadow-lg shadow-primary-500/20"
                    >
                        {isActive ? <Pause className="w-5 h-5 fill-white" /> : <Play className="w-5 h-5 fill-white ml-1" />}
                    </button>
                    <button 
                        onClick={() => setTimeLeft(task.planned_minutes * 60)}
                        className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center hover:bg-white/20 transition-all"
                    >
                        <RotateCcw className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
      </div>

      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Main Content: Study Material */}
        <div className="flex-1 overflow-y-auto p-8 lg:p-16 custom-scrollbar">
          <div className="max-w-3xl mx-auto space-y-16">
            {card ? (
              <>
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-primary-600/20 rounded-lg flex items-center justify-center">
                      <Zap className="w-4 h-4 text-primary-500" />
                    </div>
                    <h3 className="text-sm font-black uppercase tracking-widest text-white/60">The Core Essence</h3>
                  </div>
                  <p className="text-3xl font-bold leading-tight tracking-tight">
                    {card.summary}
                  </p>
                </motion.div>

                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="space-y-8"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-emerald-600/20 rounded-lg flex items-center justify-center">
                      <BookOpen className="w-4 h-4 text-emerald-500" />
                    </div>
                    <h3 className="text-sm font-black uppercase tracking-widest text-white/60">Neural Pathways (Concepts)</h3>
                  </div>
                  <div className="grid gap-10">
                    {card.key_concepts.map((concept, i) => (
                      <div key={i} className="flex gap-8 group">
                        <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center font-black text-lg group-hover:bg-primary-600 group-hover:border-primary-600 transition-all">
                          {i + 1}
                        </div>
                        <p className="text-xl font-medium text-white/80 leading-relaxed group-hover:text-white transition-colors">
                          {concept}
                        </p>
                      </div>
                    ))}
                  </div>
                </motion.div>

                {card.formulas.length > 0 && (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="space-y-8"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-amber-600/20 rounded-lg flex items-center justify-center">
                        <Zap className="w-4 h-4 text-amber-500" />
                      </div>
                      <h3 className="text-sm font-black uppercase tracking-widest text-white/60">Logical Structures</h3>
                    </div>
                    <div className="bg-white/5 rounded-[40px] border border-white/10 p-10 font-mono text-xl text-primary-400">
                      {card.formulas.map((f, i) => <div key={i} className="mb-4 last:mb-0">{f}</div>)}
                    </div>
                  </motion.div>
                )}
              </>
            ) : (
              <div className="py-20 flex flex-col items-center justify-center gap-6">
                <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center animate-pulse">
                   <Brain className="w-10 h-10 text-white/20" />
                </div>
                <p className="text-white/40 font-black uppercase tracking-widest text-xs">Extracting Study Patterns...</p>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar: Resources & Practice */}
        <div className="w-full lg:w-[400px] border-l border-white/5 bg-white/2 p-8 lg:p-12 overflow-y-auto custom-scrollbar">
          <div className="space-y-12">
            <div className="space-y-6">
              <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/40">Knowledge Sources</h4>
              <div className="grid gap-3">
                {card?.resources.map((res, i) => (
                  <a 
                    key={i} 
                    href={res.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="p-5 rounded-3xl bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/20 transition-all flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 bg-white/5 rounded-xl flex items-center justify-center text-white/40 group-hover:text-primary-500">
                            <ExternalLink className="w-5 h-5" />
                        </div>
                        <div>
                            <div className="text-sm font-bold text-white/80 group-hover:text-white">{res.title}</div>
                            <div className="text-[9px] font-black text-primary-500 uppercase tracking-widest mt-1">{res.type}</div>
                        </div>
                    </div>
                  </a>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <h4 className="text-[10px] font-black uppercase tracking-[0.3em] text-white/40">Active Probing Preview</h4>
              <div className="space-y-4">
                {card?.practice_problems.map((prob, i) => (
                  <div key={i} className="p-6 rounded-3xl bg-primary-600/5 border border-primary-600/10 italic text-white/60 text-sm leading-relaxed">
                    "{prob}"
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-8 text-center space-y-4">
                <p className="text-[10px] font-black text-white/20 uppercase tracking-[0.4em]">Ready for Verification?</p>
                <Button 
                    onClick={handleComplete}
                    className="w-full py-6 rounded-[28px] text-lg bg-primary-600 hover:bg-primary-500 shadow-2xl shadow-primary-600/20 group"
                >
                    Complete Study Session <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Completion Probe */}
      {isProbeOpen && (
        <ProbeQuizModal 
          isOpen={isProbeOpen}
          onClose={() => navigate('/')}
          taskId={taskId}
          topicId={task.topic_id}
          topicName={task.topic_name}
        />
      )}
    </div>
  )
}

export default StudySessionPage
