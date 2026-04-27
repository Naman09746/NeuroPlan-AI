import React, { useEffect, useState } from 'react'
import { CheckCircle2, Circle, Clock, Flame, Target, BookOpen, AlertCircle, Plus, ArrowRight, BookOpenCheck, Zap } from 'lucide-react'
import ProbeQuizModal from '@/components/ui/ProbeQuizModal'
import { useAuthStore } from '@/store/useAuthStore'
import { usePlanStore } from '@/store/usePlanStore'
import { useTaskStore } from '@/store/useTaskStore'
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
  const { activePlan, fetchPlans, isLoading: plansLoading } = usePlanStore()
  const { todayTasks, fetchTodayTasks, updateTaskStatus, isLoading: tasksLoading } = useTaskStore()
  const [isUpdating, setIsUpdating] = useState(null)
  const [probeTask, setProbeTask] = useState(null)

  useEffect(() => {
    fetchPlans()
  }, [])

  useEffect(() => {
    if (activePlan) {
      fetchTodayTasks(activePlan.id)
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
    return (
      <div className="p-10 max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[80vh] text-center animate-slide-up">
        <div className="w-24 h-24 bg-primary-50 rounded-3xl flex items-center justify-center mb-8">
          <BookOpen className="w-12 h-12 text-primary-600" />
        </div>
        <h2 className="text-4xl font-black text-surface-900 mb-4 tracking-tighter">Your Mind is a Blank Slate</h2>
        <p className="text-surface-500 text-lg mb-10 max-w-md font-medium">
          You haven't initialized a study plan yet. Ready to optimize your learning journey with AI-driven precision?
        </p>
        <Link to="/plan">
          <Button className="scale-110">
            Initialize New Plan <ArrowRight className="w-5 h-5" />
          </Button>
        </Link>
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
              <span className="text-3xl font-black text-surface-900 tabular-nums">12</span>
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
        <StatCard label="Phase Mastery" value={`${progress}%`} icon={Target} trend="+5%" delay="delay-1" />
        <StatCard label="Neural Load" value="4.2 hrs" icon={Clock} delay="delay-2" />
        <StatCard label="Tasks Logged" value={completedCount} icon={CheckCircle2} delay="delay-3" />
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
                  onClick={() => toast.promise(new Promise(r => setTimeout(r, 1000)), {
                    loading: 'Recalculating Neural Spacing...',
                    success: 'Schedule Optimized',
                    error: 'Optimization Failed'
                  })}
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

          <div className="glass-card p-8 bg-primary-600 text-white overflow-hidden relative">
             <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
             <h4 className="text-xl font-black mb-2 tracking-tight">Neural Insight</h4>
             <p className="text-primary-100 text-sm font-medium leading-relaxed mb-6">
               Your retention data is currently being synthesized. Complete tasks to reveal deep insights.
             </p>
             <button className="text-xs font-black uppercase tracking-widest text-white/80 hover:text-white transition-colors">
               Acknowledge Feedback
             </button>
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
