import React, { useEffect, useState } from 'react'
import { Calendar as CalendarIcon, Clock, Wand2, ArrowRight, ArrowLeft, Check, Brain, Target, Sparkles, AlertCircle } from 'lucide-react'
import { useSubjectStore } from '@/store/useSubjectStore'
import { usePlanStore } from '@/store/usePlanStore'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useNavigate, Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const StepIndicator = ({ step, label, currentStep }) => (
  <div className={clsx(
    "flex items-center gap-3 transition-all duration-500 px-4 py-2 rounded-2xl",
    step === currentStep ? "bg-primary-50 text-primary-600 scale-105" : "text-surface-300"
  )}>
    <div className={clsx(
      "w-10 h-10 rounded-2xl border-2 flex items-center justify-center font-black text-sm transition-all duration-300 shadow-sm",
      step < currentStep ? "bg-primary-600 border-primary-600 text-white" : 
      step === currentStep ? "border-primary-600 text-primary-600 bg-white" : "border-surface-100 text-surface-200 bg-white"
    )}>
      {step < currentStep ? <Check className="w-6 h-6" /> : `0${step}`}
    </div>
    <span className="font-black text-[10px] uppercase tracking-[0.2em]">{label}</span>
  </div>
)

const PlanPage = () => {
    const navigate = useNavigate()
    const { subjects, fetchSubjects, topicsBySubject, fetchTopics } = useSubjectStore()
    const { generatePlan, isLoading: isGenerating } = usePlanStore()
    
    const [step, setStep] = useState(1)
    const [formData, setFormData] = useState({
        title: '',
        subject_ids: [],
        start_date: new Date().toISOString().split('T')[0],
        end_date: '',
        daily_hours: 4,
        config: {
            revision_frequency: 'standard',
            difficulty_order: 'mixed'
        }
    })

    useEffect(() => {
        fetchSubjects()
    }, [])

    const toggleSubject = (id) => {
        if (formData.subject_ids.includes(id)) {
            setFormData(prev => ({ ...prev, subject_ids: prev.subject_ids.filter(sid => sid !== id) }))
        } else {
            setFormData(prev => ({ ...prev, subject_ids: [...prev.subject_ids, id] }))
            if (!topicsBySubject[id]) fetchTopics(id)
        }
    }

    const handleGenerate = async () => {
        if (!formData.title || !formData.end_date || formData.subject_ids.length === 0) {
            toast.error('Please complete all fields')
            return
        }

        try {
            await generatePlan(formData)
            toast.success('Neural pathways optimized!')
            navigate('/')
        } catch (err) {
            toast.error('Generation failed')
        }
    }

    const nextStep = () => {
        if (step === 1 && formData.subject_ids.length === 0) {
            toast.error('Select at least one subject node')
            return
        }
        setStep(s => Math.min(s + 1, 3))
    }
    const prevStep = () => setStep(s => Math.max(s - 1, 1))

    return (
        <div className="p-12 max-w-5xl mx-auto space-y-12 pb-20">
            <div className="text-center space-y-4">
                <div className="inline-flex p-3 bg-primary-50 rounded-2xl mb-2">
                    <Brain className="w-10 h-10 text-primary-600" />
                </div>
                <h2 className="text-5xl font-black text-surface-900 tracking-tighter">Plan Initialization Wizard</h2>
                <p className="text-surface-400 font-medium text-lg italic italic max-w-lg mx-auto">
                    Transforming your academic goals into a high-performance execution strategy.
                </p>
            </div>

            {/* Stepper Header */}
            <div className="flex justify-center items-center gap-4 glass-card py-6 px-10">
                <StepIndicator step={1} label="Selection" currentStep={step} />
                <div className="w-12 h-0.5 bg-surface-50" />
                <StepIndicator step={2} label="Config" currentStep={step} />
                <div className="w-12 h-0.5 bg-surface-50" />
                <StepIndicator step={3} label="Synthesis" currentStep={step} />
            </div>

            {/* Step Content */}
            <div className="glass-card p-12 min-h-[500px] flex flex-col relative overflow-hidden">
                <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary-100 rounded-full blur-3xl opacity-20"></div>
                
                {step === 1 && (
                    <div className="space-y-10 animate-slide-up relative z-10">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-200">
                                <Sparkles className="text-white w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-black text-surface-900 tracking-tight">Node Selection</h3>
                                <p className="text-[10px] font-black text-primary-500 uppercase tracking-widest mt-0.5">Which concepts are we conquering?</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {subjects.length > 0 ? (
                                subjects.map((s) => (
                                    <button 
                                        key={s.id} 
                                        onClick={() => toggleSubject(s.id)}
                                        className={clsx(
                                            "p-6 rounded-3xl border-2 text-left transition-all duration-300 group",
                                            formData.subject_ids.includes(s.id)
                                                ? "bg-primary-600 border-primary-600 shadow-lg shadow-primary-200"
                                                : "bg-surface-50/50 border-white hover:border-primary-100 hover:bg-white"
                                        )}
                                    >
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center gap-3">
                                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.color }} />
                                                <span className={clsx(
                                                    "font-black uppercase tracking-tight text-sm",
                                                    formData.subject_ids.includes(s.id) ? "text-white" : "text-surface-900"
                                                )}>{s.name}</span>
                                            </div>
                                            {formData.subject_ids.includes(s.id) && <Check className="w-5 h-5 text-white" />}
                                        </div>
                                        <p className={clsx(
                                            "text-[10px] font-bold mt-2 uppercase tracking-widest",
                                            formData.subject_ids.includes(s.id) ? "text-primary-100" : "text-surface-400"
                                        )}>
                                            {topicsBySubject[s.id]?.length || 0} Topics Identified
                                        </p>
                                    </button>
                                ))
                            ) : (
                                <div className="col-span-2 py-20 flex flex-col items-center text-center opacity-40">
                                    <AlertCircle className="w-12 h-12 mb-4" />
                                    <h4 className="font-black uppercase text-xs tracking-[0.2em] mb-4">No Curriculum Detected</h4>
                                    <Link to="/subjects">
                                        <Button variant="secondary" className="px-8 text-xs">Define Curriculum First</Button>
                                    </Link>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {step === 2 && (
                    <div className="space-y-12 animate-slide-up relative z-10">
                        <div className="flex items-center gap-4">
                            <div className="w-12 h-12 bg-primary-600 rounded-2xl flex items-center justify-center shadow-lg shadow-primary-200">
                                <Clock className="text-white w-6 h-6" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-black text-surface-900 tracking-tight">Parametric Configuration</h3>
                                <p className="text-[10px] font-black text-primary-500 uppercase tracking-widest mt-0.5">Optimizing load distribution.</p>
                            </div>
                        </div>

                        <div className="space-y-8">
                            <Input 
                                label="Protocol Title"
                                placeholder="e.g. Finals Sprint 2024"
                                value={formData.title}
                                onChange={e => setFormData(prev => ({ ...prev, title: e.target.value }))}
                            />

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-12 pt-4">
                                <div className="space-y-4">
                                    <label className="text-[10px] font-black text-surface-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                        <CalendarIcon className="w-4 h-4 text-primary-600" /> Objective Deadline
                                    </label>
                                    <input 
                                        type="date" 
                                        className="w-full p-4 bg-surface-50 rounded-2xl border-2 border-white focus:border-primary-500 outline-none font-bold text-surface-900 transition-all cursor-pointer"
                                        value={formData.end_date}
                                        onChange={e => setFormData(prev => ({ ...prev, end_date: e.target.value }))}
                                        min={formData.start_date}
                                    />
                                </div>
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <label className="text-[10px] font-black text-surface-400 uppercase tracking-[0.2em] flex items-center gap-2">
                                            <Clock className="w-4 h-4 text-primary-600" /> Daily Bandwidth
                                        </label>
                                        <span className="text-xl font-black text-primary-600 tabular-nums">{formData.daily_hours}h</span>
                                    </div>
                                    <div className="pt-2 px-1">
                                        <input 
                                            type="range" 
                                            min="1" 
                                            max="12" 
                                            step="0.5" 
                                            className="w-full h-2 bg-surface-50 rounded-lg appearance-none cursor-pointer accent-primary-600 ring-4 ring-primary-50"
                                            value={formData.daily_hours}
                                            onChange={e => setFormData(prev => ({ ...prev, daily_hours: parseFloat(e.target.value) }))}
                                        />
                                        <div className="flex justify-between mt-4 text-[10px] font-black text-surface-300 uppercase tracking-widest leading-none">
                                            <span>Sustainable (2h)</span>
                                            <span>Critical (8h+)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {step === 3 && (
                   <div className="space-y-10 text-center py-10 animate-slide-up relative z-10">
                        <div className="w-24 h-24 bg-emerald-50 rounded-full flex items-center justify-center mx-auto mb-6 shadow-sm border border-emerald-100">
                            <Target className="w-12 h-12 text-emerald-600 animate-pulse" />
                        </div>
                        <div className="max-w-md mx-auto">
                            <h3 className="text-3xl font-black text-surface-900 tracking-tight">Path Extraction Ready</h3>
                            <p className="text-surface-500 font-medium mt-3 leading-relaxed">
                                Our neural engine has calculated the optimal distribution for your selected nodes. 
                                We've applied **1-3-7 spacing** to maximize retention during the {Math.round((new Date(formData.end_date) - new Date(formData.start_date))/(1000*60*60*24))} day period.
                            </p>
                        </div>

                        <div className="p-8 glass-card bg-surface-50/50 text-left border-dashed border-2 max-w-sm mx-auto space-y-6">
                            <div className="flex items-center justify-between">
                                <h4 className="text-[10px] font-black text-surface-400 uppercase tracking-[0.3em]">Protocol Summary</h4>
                                <Sparkles className="w-4 h-4 text-primary-500" />
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center gap-3">
                                     <div className="w-2 h-2 rounded-full bg-primary-600" />
                                     <span className="text-sm font-bold text-surface-900">{formData.title}</span>
                                </div>
                                <div className="flex items-center gap-3">
                                     <div className="w-2 h-2 rounded-full bg-emerald-600" />
                                     <span className="text-sm font-bold text-surface-900">{formData.subject_ids.length} Active Nodes</span>
                                </div>
                                <div className="flex items-center gap-3">
                                     <div className="w-2 h-2 rounded-full bg-blue-600" />
                                     <span className="text-sm font-bold text-surface-900">{formData.daily_hours}h Peak Load</span>
                                </div>
                            </div>
                        </div>
                   </div>
                )}

                {/* Footer Controls */}
                <div className="mt-auto pt-16 flex justify-between items-center relative z-10">
                    <button 
                        onClick={prevStep}
                        disabled={step === 1 || isGenerating}
                        className={clsx(
                        "px-8 py-3 rounded-2xl font-black text-[10px] uppercase tracking-widest text-surface-400 hover:text-surface-900 hover:bg-white flex items-center gap-3 transition-all",
                        step === 1 && "invisible"
                    )}>
                        <ArrowLeft className="w-4 h-4" /> Access Backlog
                    </button>
                    {step < 3 ? (
                         <Button onClick={nextStep} className="px-10 py-4 text-sm group">
                             Proceed to Sync <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                         </Button>
                    ) : (
                        <Button onClick={handleGenerate} className="px-12 py-5 text-base shadow-2xl shadow-primary-200" isLoading={isGenerating}>
                             Initialize Synthesis <Wand2 className="w-6 h-6 animate-pulse" />
                        </Button>
                    )}
                </div>
            </div>
        </div>
    )
}

export default PlanPage
