import React, { useEffect } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar } from 'recharts'
import { TrendingUp, Activity, Award, Clock, Target, Brain, Sparkles, AlertCircle } from 'lucide-react'
import { useAnalyticsStore } from '@/store/useAnalyticsStore'
import { clsx } from 'clsx'

const StatCard = ({ label, value, icon: Icon, colorClass, delay = '' }) => (
  <div className={clsx("glass-card p-8 animate-slide-up", delay)}>
    <div className="flex justify-between items-start mb-4">
      <div className={clsx("p-4 rounded-2xl", colorClass)}>
        <Icon className="w-6 h-6" />
      </div>
    </div>
    <div className="text-4xl font-black text-surface-900 tracking-tighter">{value}</div>
    <div className="text-[10px] font-black text-surface-400 mt-2 uppercase tracking-[0.2em]">{label}</div>
  </div>
)

const AnalyticsPage = () => {
    const { overview, trends, distribution, mastery, fetchAll, isLoading } = useAnalyticsStore()

    useEffect(() => {
        fetchAll()
    }, [])

    if (isLoading && !overview) {
        return (
            <div className="p-10 flex flex-col items-center justify-center min-h-[60vh]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
                <p className="text-surface-500 font-black uppercase tracking-widest animate-pulse">Synthesizing Neural Metrics...</p>
            </div>
        )
    }

    return (
        <div className="p-12 max-w-7xl mx-auto space-y-12 pb-20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
                <div>
                   <h2 className="text-4xl font-black text-surface-900 tracking-tight">Neuro-Efficiency Analytics</h2>
                   <p className="text-surface-400 mt-2 font-medium italic flex items-center gap-2">
                     <span className="w-2 h-2 bg-primary-500 rounded-full animate-ping"></span>
                     Data-driven insights for cognitive optimization.
                   </p>
                </div>
                <div className="flex items-center gap-2 bg-primary-50 px-4 py-2 rounded-2xl font-black text-[10px] text-primary-600 uppercase tracking-widest border border-primary-100">
                    <Sparkles className="w-3 h-3" />
                    AI Insights Active
                </div>
            </div>

            {/* Overview Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                <StatCard label="Phase Mastery" value={`${overview?.completion_rate || 0}%`} icon={Target} colorClass="bg-primary-50 text-primary-600" delay="delay-1" />
                <StatCard label="Neural Streak" value={`${overview?.streak || 0}d`} icon={TrendingUp} colorClass="bg-orange-50 text-orange-600" delay="delay-2" />
                <StatCard label="Node Density" value={overview?.total_tasks || 0} icon={Brain} colorClass="bg-cyan-50 text-cyan-600" delay="delay-3" />
                <StatCard label="Total Load" value={`${overview?.total_hours || 0}h`} icon={Clock} colorClass="bg-purple-50 text-purple-600" delay="delay-4" />
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Efficiency Trend Chart */}
                <div className="lg:col-span-8 glass-card p-10 space-y-8 animate-slide-up delay-1">
                    <div className="flex justify-between items-center">
                        <div>
                            <h3 className="text-xl font-black text-surface-900 tracking-tight">Neural Efficiency Curve</h3>
                            <p className="text-[10px] font-black text-surface-400 uppercase tracking-widest mt-1">Completion rate vs. Planned load</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                                <span className="text-[10px] font-black text-surface-400 uppercase">Trend</span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="h-[300px] w-full mt-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trends}>
                                <defs>
                                    <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.1}/>
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis 
                                    dataKey="date" 
                                    axisLine={false} 
                                    tickLine={false} 
                                    tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 700}} 
                                    tickFormatter={(str) => new Date(str).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 700}} />
                                <Tooltip 
                                    contentStyle={{backgroundColor: 'white', borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                                    itemStyle={{fontSize: '12px', fontWeight: 'bold'}}
                                />
                                <Area 
                                    type="monotone" 
                                    dataKey="completion_rate" 
                                    stroke="#6366f1" 
                                    strokeWidth={4} 
                                    fillOpacity={1} 
                                    fill="url(#colorTrend)" 
                                    animationDuration={2000}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Score Summary Card replacement */}
                <div className="lg:col-span-4 glass-card p-10 bg-surface-900 text-white flex flex-col justify-between overflow-hidden relative animate-slide-up delay-2">
                    <div className="absolute -top-20 -right-20 w-48 h-48 bg-primary-500 rounded-full blur-[80px] opacity-30"></div>
                    <div className="relative z-10">
                        <div className="flex items-center gap-2 mb-8">
                            <Award className="w-5 h-5 text-primary-400" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-primary-400">Mastery Badge</span>
                        </div>
                        <h4 className="text-3xl font-black mb-4 leading-tight">Elite Efficiency Level Detected</h4>
                        <p className="text-surface-400 text-sm leading-relaxed mb-6">
                            Your retention velocity is <span className="text-primary-400 font-bold">12% above</span> average. 
                            The engine predicts milestone completion 3 days early if current intensity is maintained.
                        </p>
                    </div>
                    <button className="relative z-10 w-full py-4 bg-primary-600 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-primary-500 transition-all shadow-lg shadow-primary-900/40">
                        View Optimization Plan
                    </button>
                </div>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Cognitive Distribution (Pie) */}
                <div className="lg:col-span-5 glass-card p-10 animate-slide-up delay-3">
                    <h3 className="text-xl font-black text-surface-900 tracking-tight mb-8">Cognitive Load Distribution</h3>
                    <div className="h-64 flex flex-col md:flex-row items-center gap-8">
                        <div className="w-full h-full lg:w-3/5">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie 
                                        data={distribution} 
                                        innerRadius={60} 
                                        outerRadius={85} 
                                        paddingAngle={8} 
                                        dataKey="minutes"
                                        nameKey="subject"
                                    >
                                        {distribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="w-full lg:w-2/5 space-y-4">
                            {distribution.map(s => (
                                <div key={s.subject} className="flex items-center justify-between gap-3">
                                    <div className="flex items-center gap-2 overflow-hidden">
                                        <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{backgroundColor: s.color}} />
                                        <span className="text-[10px] font-bold text-surface-600 truncate uppercase tracking-tight">{s.subject}</span>
                                    </div>
                                    <span className="text-[10px] font-black text-surface-900">{s.percentage}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Node Mastery (Bar) */}
                <div className="lg:col-span-7 glass-card p-10 animate-slide-up delay-4">
                    <div className="flex justify-between items-center mb-10">
                        <h3 className="text-xl font-black text-surface-900 tracking-tight">Active Node Mastery</h3>
                        <span className="text-[10px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg">VERIFIED DATA</span>
                    </div>
                    <div className="h-[250px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={mastery}>
                                <XAxis 
                                    dataKey="subject" 
                                    axisLine={false} 
                                    tickLine={false} 
                                    tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 700}} 
                                />
                                <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 10, fontWeight: 700}} domain={[0, 100]} />
                                <Tooltip 
                                    cursor={{fill: '#f8fafc'}}
                                    contentStyle={{backgroundColor: 'white', borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)'}}
                                />
                                <Bar 
                                    dataKey="mastery" 
                                    radius={[8, 8, 8, 8]} 
                                    barSize={40}
                                >
                                    {mastery.map((entry, index) => (
                                        <Cell 
                                            key={`cell-${index}`} 
                                            fill={distribution.find(d => d.subject === entry.subject)?.color || '#6366f1'} 
                                            fillOpacity={0.8}
                                        />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
            
            {/* Optimization Insights Banner */}
            <div className="glass-card p-10 bg-primary-600 text-white flex flex-col md:flex-row items-center justify-between gap-8 overflow-hidden relative animate-slide-up delay-5">
                 <div className="absolute -left-10 -bottom-10 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
                 <div className="flex items-center gap-6 relative z-10">
                     <div className="w-16 h-16 bg-white/20 rounded-3xl flex items-center justify-center backdrop-blur-md border border-white/20">
                         <Activity className="w-8 h-8 text-white" />
                     </div>
                     <div>
                         <h4 className="text-2xl font-black tracking-tight">System Performance: Optimal</h4>
                         <p className="text-primary-100 font-medium opacity-80 mt-1 uppercase text-[10px] tracking-widest">Calculated across {overview?.total_tasks || 0} study nodes</p>
                     </div>
                 </div>
                 <div className="text-right flex flex-col items-center md:items-end gap-2 relative z-10">
                     <p className="text-xs font-bold text-white/70 italic max-w-xs leading-relaxed">
                        "Your cognitive flow is peaking. The AI recommends increasing study intensity for the next 48 hours."
                     </p>
                     <div className="flex gap-4 mt-2">
                        <button className="text-[10px] font-black uppercase tracking-widest border-b-2 border-white/40 hover:border-white transition-all pb-1">Ignore Suggestion</button>
                        <button className="text-[10px] font-black uppercase tracking-widest bg-white text-primary-600 px-4 py-1.5 rounded-lg hover:scale-105 transition-all">Enable Turbo Mode</button>
                     </div>
                 </div>
            </div>
        </div>
    )
}

export default AnalyticsPage
