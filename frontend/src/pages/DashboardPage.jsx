import React, { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Clock, Flame, Target, BookOpen, AlertCircle, Plus, ArrowRight, BookOpenCheck, Zap } from 'lucide-react'
import ProbeQuizModal from '@/components/ui/ProbeQuizModal'
import { useAuthStore } from '@/store/useAuthStore'
import { usePlanStore } from '@/store/usePlanStore'
import { useTaskStore } from '@/store/useTaskStore'
import { useAnalyticsStore } from '@/store/useAnalyticsStore'
import { useSubjectStore } from '@/store/useSubjectStore'
import { useConfigStore } from '@/store/useConfigStore'
import { useCoachingStore } from '@/store/useCoachingStore'
import { Button } from '@/components/ui/Button'
import { Link, useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'

const StatCard = ({ label, value, icon: Icon, trend, delay = '' }) => (
  <div className={`glass-card p-6 animate-slide-up ${delay}`}>
    <div className="flex justify-between items-start mb-4">
      <div className="p-3 bg-primary-50 rounded-xl">
        <Icon className="w-6 h-6 text-primary-600" />
      </div>
      {trend && (
        <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-lg">
          {trend}
        </span>
      )}
    </div>
    <div className="text-3xl font-black text-surface-900 tracking-tight">{value}</div>
    <div className="text-sm font-bold text-surface-400 mt-1 uppercase tracking-wider">{label}</div>
  </div>
)

const DashboardPage = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { overview, fetchOverview } = useAnalyticsStore()
  const { activePlan, fetchPlans, reschedulePlan, isLoading: plansLoading } = usePlanStore()
  const { todayTasks, fetchTodayTasks, weekTasks, fetchWeekTasks, updateTaskStatus, isLoading: tasksLoading } = useTaskStore()
  const { subjects, fetchSubjects } = useSubjectStore()
  const { aiHealth, fetchAIHealth } = useConfigStore()
  const { notifications, fetchNotifications, markAsRead } = useCoachingStore()
  const [isUpdating, setIsUpdating] = useState(null)
  const [probeTask, setProbeTask] = useState(null)

  useEffect(() => {
    fetchPlans()
    fetchOverview()
    fetchSubjects()
    fetchAIHealth()
    fetchNotifications()
  }, [])

  useEffect(() => {
    if (activePlan) {
      fetchTodayTasks(activePlan.id)
      fetchWeekTasks(activePlan.id)
    }
  }, [activePlan])

  const handleToggleStatus = async (taskId, currentStatus, topicId) => {
    if (currentStatus !== 'done') {
      // Trigger probe quiz first
      setProbeTask({ taskId, topicId })
      return
    }
    
    // If already done, toggle back to pending (no probe needed)
    setIsUpdating(taskId)
    try {
      await updateTaskStatus(taskId, 'pending')
      toast.success('Task reset')
    } catch (err) {
      toast.error('Failed to update task')
    } finally {
      setIsUpdating(null)
    }
  }

  const completedCount = todayTasks.filter(t => t.status === 'done').length
  const progress = todayTasks.length > 0 ? Math.round((completedCount / todayTasks.length) * 100) : 0

  if (plansLoading && !activePlan) {
    return (
      <div className="p-10 flex flex-col items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
        <p className="text-surface-500 font-bold animate-pulse">Synchronizing Neural Pathways...</p>
      </div>
    )
  }

  if (!activePlan) {
    const hasSubjects = subjects.length > 0
    
    return (
      <div className="p-12 max-w-5xl mx-auto space-y-12 animate-slide-up">
        {/* AI Status Banner */}
        {aiHealth.status === 'offline' && (
          <div className="bg-red-50 border-2 border-red-100 p-4 rounded-2xl flex items-center gap-4 text-red-600">
            <AlertCircle className="w-6 h-6 shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-black uppercase tracking-wider">Neural Engine Offline</p>
              <p className="text-xs font-medium opacity-80">Local inference is disconnected. Ensure Ollama is running to generate plans.</p>
            </div>
            <Button variant="secondary" size="sm" onClick={fetchAIHealth} className="bg-white border-red-200 text-red-600 hover:bg-red-50">
              Retry Sync
            </Button>
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-12 items-center py-12">
          <div className="flex-1 space-y-8">
            <div>
              <h2 className="text-5xl font-black text-surface-900 tracking-tighter leading-tight">
                Design Your <span className="text-primary-600 underline decoration-primary-100">Neural Network</span>
              </h2>
              <p className="text-surface-500 text-xl mt-4 font-medium max-w-lg">
                Your cognitive profile is ready. Now, let's architect your knowledge base.
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 glass-card border-emerald-100 bg-emerald-50/30">
                <div className="w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center text-white">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-black text-emerald-900 uppercase tracking-widest">Step 1: Cognitive Sync</p>
                  <p className="text-xs text-emerald-600 font-bold">Profile initialized successfully.</p>
                </div>
              </div>

              <Link to="/subjects" className="block group">
                <div className={clsx(
                  "flex items-center gap-4 p-4 glass-card transition-all group-hover:scale-[1.02]",
                  hasSubjects ? "border-emerald-100 bg-emerald-50/30" : "border-primary-100 hover:border-primary-300"
                )}>
                  <div className={clsx(
                    "w-8 h-8 rounded-full flex items-center justify-center text-white",
                    hasSubjects ? "bg-emerald-500" : "bg-primary-500 animate-pulse"
                  )}>
                    {hasSubjects ? <CheckCircle2 className="w-5 h-5" /> : <Plus className="w-5 h-5" />}
                  </div>
                  <div className="flex-1">
                    <p className={clsx(
                      "text-sm font-black uppercase tracking-widest",
                      hasSubjects ? "text-emerald-900" : "text-primary-900"
                    )}>Step 2: Subject Ingestion</p>
                    <p className={clsx(
                      "text-xs font-bold",
                      hasSubjects ? "text-emerald-600" : "text-primary-500"
                    )}>
                      {hasSubjects ? `${subjects.length} nodes active.` : "Add your first learning subject."}
                    </p>
                  </div>
                  {!hasSubjects && <ArrowRight className="w-5 h-5 text-primary-400 group-hover:translate-x-1 transition-transform" />}
                </div>
              </Link>

              <Link to="/plan" className={clsx("block group", !hasSubjects && "opacity-50 pointer-events-none")}>
                <div className="flex items-center gap-4 p-4 glass-card border-surface-100 hover:border-primary-300 transition-all group-hover:scale-[1.02]">
                  <div className="w-8 h-8 bg-surface-200 rounded-full flex items-center justify-center text-white">
                    <Zap className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-black text-surface-900 uppercase tracking-widest">Step 3: Pulse Initialization</p>
                    <p className="text-xs text-surface-400 font-bold">Generate your AI study schedule.</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-surface-300 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            </div>
          </div>

          <div className="w-full md:w-[400px] aspect-square bg-gradient-to-br from-primary-50 to-indigo-50 rounded-[4rem] flex items-center justify-center relative overflow-hidden">
             <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
             <BookOpen className="w-32 h-32 text-primary-200 relative z-10 animate-float" />
             <div className="absolute bottom-12 left-12 right-12 glass-card p-6 bg-white/80">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-2 h-2 bg-primary-500 rounded-full animate-ping"></div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-primary-600">Neural status</span>
                </div>
                <p className="text-xs font-bold text-surface-900">Waiting for first ingestion signal...</p>
             </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-12 max-w-7xl mx-auto space-y-12 pb-20">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h2 className="text-4xl font-black text-surface-900 tracking-tight">
            Welcome back, {user?.name?.split(' ')[0]}! 👋
          </h2>
          <p className="text-surface-400 mt-2 font-medium italic flex items-center gap-2">
            <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
            "The secret of getting ahead is getting started."
          </p>
        </div>
        <div className="flex items-center gap-8 glass-card px-8 py-4">
          <div className="text-right">
            <div className="text-[10px] font-black text-surface-400 mb-1 uppercase tracking-[0.2em]">Current Streak</div>
            <div className="flex items-center gap-3 justify-end">
              <span className="text-3xl font-black text-surface-900 tabular-nums">{overview?.streak || 0}</span>
              <Flame className="w-8 h-8 text-orange-500 fill-orange-500 animate-bounce" />
            </div>
          </div>
          <div className="w-px h-10 bg-surface-100"></div>
          <div className="text-right">
            <div className="text-[10px] font-black text-surface-400 mb-1 uppercase tracking-[0.2em]">Efficiency</div>
            <div className="flex items-center gap-3 justify-end">
              <span className="text-3xl font-black text-primary-600 tabular-nums">{progress}%</span>
              <Target className="w-8 h-8 text-primary-500" />
            </div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard label="Phase Mastery" value={`${overview?.completion_rate || 0}%`} icon={Target} trend="+5%" delay="delay-1" />
        <StatCard label="Neural Load" value={`${overview?.total_hours || 0} hrs`} icon={Clock} delay="delay-2" />
        <StatCard label="Tasks Logged" value={overview?.completed_tasks || 0} icon={CheckCircle2} delay="delay-3" />
        <StatCard label="Active Nodes" value={todayTasks.length} icon={BookOpenCheck} delay="delay-4" />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* Today's Tasks (Wide Column) */}
        <div className="lg:col-span-2 space-y-8">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-black text-surface-900 tracking-tight">Circuit Flow: Today</h3>
            <div className="flex items-center gap-2 text-primary-600 bg-primary-50 px-4 py-2 rounded-2xl font-bold text-sm">
              <span className="w-2 h-2 bg-primary-500 rounded-full animate-ping"></span>
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </div>
          </div>

          <div className="space-y-4">
             {todayTasks.length > 0 ? (
               todayTasks.map((task, i) => (
                <div key={task.id} className="group glass-card p-6 flex items-center gap-8 hover:bg-white hover:scale-[1.01] transition-all duration-300">
                  <div className="text-center min-w-[70px]">
                    <div className="text-sm font-black text-surface-900 group-hover:text-primary-600 transition-colors uppercase tracking-widest">
                       {task.task_type}
                    </div>
                    <div className="text-xs font-bold text-surface-400 mt-1">{task.planned_minutes} min</div>
                  </div>
                  
                  <div className="w-1 h-12 rounded-full bg-surface-100 overflow-hidden">
                    <div className={clsx(
                      "w-full h-full rounded-full transition-all duration-700",
                      task.status === 'done' ? "bg-emerald-500" : "bg-primary-500"
                    )} />
                  </div>

                  <div className="flex-1">
                    <button 
                      onClick={() => navigate(`/study/session/${task.id}`)}
                      className="text-left group/title"
                    >
                      <h4 className={clsx(
                        "text-xl font-bold transition-all decoration-primary-500",
                        task.status === 'done' ? "text-surface-400 line-through decoration-2" : "group-hover/title:text-primary-600 group-hover/title:underline"
                      )}>
                        {task.topic_name}
                      </h4>
                    </button>
                    <p className="text-xs font-black text-primary-500 uppercase tracking-widest mt-1">
                      {task.status}
                    </p>
                  </div>

                  <button 
                    onClick={() => handleToggleStatus(task.id, task.status, task.topic_id)}
                    disabled={isUpdating === task.id}
                    className={clsx(
                      "w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 shadow-sm",
                      task.status === 'done' 
                        ? "bg-emerald-100 text-emerald-600 rotate-12" 
                        : "bg-surface-50 text-surface-300 group-hover:bg-primary-600 group-hover:text-white group-hover:rotate-6 group-hover:shadow-lg group-hover:shadow-primary-200"
                    )}
                  >
                    {isUpdating === task.id ? (
                      <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      task.status === 'done' ? <CheckCircle2 className="w-7 h-7" /> : <Circle className="w-7 h-7" />
                    )}
                  </button>
                </div>
               ))
             ) : (
                <div className="glass-card p-12 flex flex-col items-center text-center">
                  <div className="w-16 h-16 bg-surface-50 rounded-2xl flex items-center justify-center mb-6">
                    <AlertCircle className="w-8 h-8 text-surface-300" />
                  </div>
                  <h4 className="text-xl font-bold text-surface-900 mb-2">System Idle</h4>
                  <p className="text-surface-400 font-medium">No tasks detected for today. Enjoy the buffer!</p>
                </div>
             )}
          </div>
        </div>

        {/* Weekly Calendar (Mobile & Desktop) */}
        <div className="lg:col-span-3 space-y-8 animate-slide-up delay-2">
          <div className="flex items-center justify-between">
            <h3 className="text-2xl font-black text-surface-900 tracking-tight">Weekly Knowledge Circuit</h3>
            <div className="text-xs font-bold text-surface-400 uppercase tracking-widest">Next 7 Days</div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
             {Array.from({ length: 7 }).map((_, i) => {
               const date = new Date()
               date.setDate(date.getDate() + i)
               const dateStr = date.toISOString().split('T')[0]
               const dayTasks = weekTasks.filter(t => t.scheduled_date === dateStr)
               const isToday = i === 0
               
               return (
                 <div key={dateStr} className={clsx(
                   "glass-card p-4 flex flex-col items-center gap-4 transition-all hover:scale-[1.02]",
                   isToday ? "border-primary-200 bg-primary-50/20" : "opacity-80"
                 )}>
                   <div className="text-center">
                     <div className="text-[10px] font-black text-surface-400 uppercase tracking-widest">{date.toLocaleDateString('en-US', { weekday: 'short' })}</div>
                     <div className={clsx(
                       "text-lg font-black mt-1",
                       isToday ? "text-primary-600" : "text-surface-900"
                     )}>{date.getDate()}</div>
                   </div>
                   
                   <div className="w-full space-y-2">
                     {dayTasks.length > 0 ? (
                       dayTasks.map(t => (
                         <div key={t.id} className="group/task relative">
                           <div className={clsx(
                             "h-1.5 w-full rounded-full transition-all",
                             t.status === 'done' ? "bg-emerald-400" : "bg-primary-300"
                           )} title={t.topic_name} />
                           <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-surface-900 text-white text-[10px] rounded opacity-0 group-hover/task:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                             {t.topic_name}
                           </div>
                         </div>
                       ))
                     ) : (
                       <div className="h-1.5 w-full rounded-full bg-surface-100" />
                     )}
                   </div>
                 </div>
               )
             })}
          </div>
        </div>

        {/* Weekly Insights (Narrow Column) */}
        <div className="space-y-8 animate-slide-up delay-3">
          <h3 className="text-2xl font-black text-surface-900 tracking-tight">Neural Sync</h3>
          <div className="glass-card p-8 space-y-6">
             <div className="space-y-4">
                <Button 
                  onClick={() => {
                    if (todayTasks.length > 0) {
                      const randomTask = todayTasks[Math.floor(Math.random() * todayTasks.length)]
                      navigate(`/test/${randomTask.topic_id}`)
                    } else {
                      toast.error('No active study nodes detected for today')
                    }
                  }} 
                  className="w-full justify-between py-6 group"
                >
                  <span>Generate Deep Test</span>
                  <Zap className="w-5 h-5 group-hover:animate-pulse text-yellow-400" />
                </Button>
                <Button 
                  variant="secondary" 
                  onClick={() => {
                    toast.promise(reschedulePlan(activePlan.id), {
                      loading: 'Recalculating Neural Spacing...',
                      success: () => {
                        fetchTodayTasks(activePlan.id)
                        fetchOverview()
                        return 'Schedule Optimized'
                      },
                      error: 'Optimization Failed'
                    })
                  }}
                  className="w-full justify-between py-6 group bg-white/50"
                >
                  <span>Adaptive Reschedule</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Button>
             </div>

             <div className="pt-6 border-t border-surface-100">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm font-black text-surface-400 uppercase tracking-widest">Active Plan</span>
                  <span className="text-xs font-bold text-primary-600 bg-primary-50 px-2 py-1 rounded-lg">LIVE</span>
                </div>
                <div className="p-4 bg-surface-900 rounded-2xl text-white">
                  <h5 className="font-bold mb-1">{activePlan.title}</h5>
                  <p className="text-xs text-surface-400 font-medium tracking-tight">
                    Ends {new Date(activePlan.end_date).toLocaleDateString()}
                  </p>
                </div>
             </div>
          </div>

          {/* AI Coach Section */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xl font-black text-surface-900 tracking-tight flex items-center gap-2">
                <Zap className="w-5 h-5 text-primary-600" />
                AI Coach
              </h3>
              {notifications.some(n => !n.is_read) && (
                <span className="flex h-2 w-2 rounded-full bg-primary-600 animate-pulse"></span>
              )}
            </div>
            
            <div className="space-y-4">
              {notifications.length > 0 ? (
                notifications.map((note) => (
                  <div 
                    key={note.id} 
                    className={clsx(
                      "glass-card p-6 transition-all duration-300 relative overflow-hidden group border-l-4",
                      note.is_read ? "opacity-70 grayscale-[0.5] border-surface-200" : "border-primary-600 bg-primary-50/20"
                    )}
                  >
                    {!note.is_read && (
                      <div className="absolute top-4 right-4">
                        <button 
                          onClick={() => markAsRead(note.id)}
                          className="text-[10px] font-black uppercase tracking-widest text-primary-600 hover:text-primary-700"
                        >
                          Dismiss
                        </button>
                      </div>
                    )}
                    <h4 className="text-sm font-black text-surface-900 uppercase tracking-widest mb-2 flex items-center gap-2">
                      {note.trigger_type.replace('_', ' ')}
                    </h4>
                    <p className="text-sm font-medium text-surface-600 leading-relaxed mb-4">
                      {note.message}
                    </p>
                    {note.priority_topics?.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-4">
                        {note.priority_topics.map(topic => (
                          <span key={topic} className="text-[10px] font-bold bg-white border border-primary-100 text-primary-700 px-2 py-1 rounded-md">
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}
                    <div className="bg-white/50 rounded-xl p-3 border border-surface-100">
                      <p className="text-[10px] font-black text-surface-400 uppercase tracking-widest mb-1">Coach Note</p>
                      <p className="text-xs font-bold text-surface-900 italic">"{note.motivational_note}"</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="glass-card p-8 bg-primary-600 text-white overflow-hidden relative">
                   <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
                   <h4 className="text-xl font-black mb-2 tracking-tight">Neural Sync Active</h4>
                   <p className="text-primary-100 text-sm font-medium leading-relaxed">
                     Your retention data is being synthesized. Complete a test or skip a task to trigger adaptive coaching insights.
                   </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Neural Probe Quiz Modal */}
      {probeTask && (
        <ProbeQuizModal
          isOpen={!!probeTask}
          onClose={() => {
            setProbeTask(null)
            fetchTodayTasks(activePlan.id) // Refresh results
          }}
          taskId={probeTask.taskId}
          topicId={probeTask.topicId}
          topicName={todayTasks.find(t => t.id === probeTask.taskId)?.topic_name}
        />
      )}
    </div>
  )
}

export default DashboardPage
