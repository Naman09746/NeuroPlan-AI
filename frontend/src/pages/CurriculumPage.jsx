import React, { useState, useEffect } from 'react'
import { Plus, Trash2, ListPlus, ChevronRight, BookOpen, AlertCircle, LayoutGrid, Layers, Brain, Sparkles } from 'lucide-react'
import StudyCardModal from '@/components/ui/StudyCardModal'
import QuickSetupModal from '@/components/ui/QuickSetupModal'
import { useSubjectStore } from '@/store/useSubjectStore'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const SubjectCard = ({ subject, active, onClick, topicCount = 0 }) => (
  <button 
    onClick={onClick}
    className={clsx(
      "w-full p-6 text-left group transition-all duration-300 animate-slide-up",
      active 
        ? "glass-card ring-2 ring-primary-500/50 translate-x-1" 
        : "bg-white/40 border border-white hover:bg-white/60 hover:border-primary-100 hover:shadow-sm"
    )}
  >
    <div className="flex justify-between items-center">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center shadow-sm border border-white" style={{ backgroundColor: `${subject.color}15` }}>
          <div className="w-3 h-3 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.1)]" style={{ backgroundColor: subject.color }} />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h4 className={clsx(
               "font-black tracking-tight uppercase text-sm group-hover:text-primary-600 transition-colors",
               active ? "text-primary-600" : "text-surface-900"
            )}>
                {subject.name}
            </h4>
            <span className="text-[8px] font-black uppercase tracking-widest px-1.5 py-0.5 rounded-md bg-surface-100 text-surface-500 border border-surface-200">
              {subject.target_level}
            </span>
          </div>
          <p className="text-[10px] font-black text-surface-400 mt-1 uppercase tracking-widest">{topicCount} Neural Nodes</p>
        </div>
      </div>
      <ChevronRight className={clsx("w-5 h-5 transition-transform duration-300", active ? "text-primary-600 translate-x-1" : "text-surface-300")} />
    </div>
  </button>
)

const CurriculumPage = () => {
    const { subjects, fetchSubjects, createSubject, deleteSubject, topicsBySubject, fetchTopics, bulkCreateTopics, isLoading, decomposeSubject, isDecomposing } = useSubjectStore()
    const [selectedSubject, setSelectedSubject] = useState(null)
    const [selectedTopic, setSelectedTopic] = useState(null)
    const [isAddingSubject, setIsAddingSubject] = useState(false)
    const [isQuickSetupOpen, setIsQuickSetupOpen] = useState(false)
    const [newSubjectName, setNewSubjectName] = useState('')
    const [newSubjectColor, setNewSubjectColor] = useState('#6366f1')
    const [targetLevel, setTargetLevel] = useState('intermediate')
    const [bulkTopicsText, setBulkTopicsText] = useState('')
    const [decomposeContext, setDecomposeContext] = useState('')
    const [isImporting, setIsImporting] = useState(false)

    useEffect(() => {
        fetchSubjects()
    }, [])

    useEffect(() => {
        if (selectedSubject) {
            fetchTopics(selectedSubject.id)
        }
    }, [selectedSubject])

    const handleCreateSubject = async (e) => {
        e.preventDefault()
        try {
            const subject = await createSubject(newSubjectName, newSubjectColor, targetLevel)
            setNewSubjectName('')
            setTargetLevel('intermediate')
            setIsAddingSubject(false)
            setSelectedSubject(subject)
            toast.success('Subject initialized')
        } catch (err) {
            toast.error('Initialization failed')
        }
    }

    const handleImportTopics = async () => {
        if (!bulkTopicsText.trim()) return
        const topicNames = bulkTopicsText.split('\n').filter(t => t.trim() !== '')
        const topics = topicNames.map(name => ({
            name: name.trim(),
            difficulty: 'medium',
            estimated_hours: 2.0
        }))

        setIsImporting(true)
        try {
            await bulkCreateTopics(selectedSubject.id, topics)
            setBulkTopicsText('')
            toast.success(`${topics.length} topics added to neural network`)
        } catch (err) {
            toast.error('Import failed')
        } finally {
            setIsImporting(false)
        }
    }

    const handleDecompose = async () => {
        try {
            const topics = await decomposeSubject(selectedSubject.id, decomposeContext)
            setDecomposeContext('')
            toast.success(`🧠 ${topics.length} subtopics auto-generated!`)
        } catch (err) {
            toast.error('AI decomposition failed. Check API key.')
        }
    }

    const handleDeleteSubject = async (id) => {
        if (window.confirm('Are you sure? This will purge all associated topic data.')) {
            try {
                await deleteSubject(id)
                setSelectedSubject(null)
                toast.success('Subject purged')
            } catch (err) {
                toast.error('Purge failed')
            }
        }
    }

    return (
        <div className="p-12 max-w-7xl mx-auto space-y-12 pb-20">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h2 className="text-4xl font-black text-surface-900 tracking-tight">Curriculum Management</h2>
                    <p className="text-surface-400 mt-2 font-medium italic flex items-center gap-2">
                        <span className="w-2 h-2 bg-primary-500 rounded-full"></span>
                        Design the architecture of your knowledge base.
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button variant="secondary" onClick={() => setIsQuickSetupOpen(true)} className="group bg-white">
                        <Sparkles className="w-5 h-5 group-hover:rotate-12 transition-transform text-primary-600" />
                        AI Quick Setup
                    </Button>
                    {!isAddingSubject && (
                      <Button onClick={() => setIsAddingSubject(true)} className="group">
                          <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                          Add Subject Node
                      </Button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                {/* Subjects Sidebar */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="flex items-center gap-2 text-[10px] font-black text-surface-400 uppercase tracking-[0.2em] px-1">
                        <LayoutGrid className="w-3 h-3" />
                        Active Nodes
                    </div>
                    
                    {isAddingSubject && (
                        <form onSubmit={handleCreateSubject} className="glass-card p-6 space-y-4 animate-slide-up">
                            <Input 
                                label="Node Name" 
                                placeholder="e.g. Quantum Physics" 
                                value={newSubjectName}
                                onChange={e => setNewSubjectName(e.target.value)}
                                required
                                autoFocus
                            />
                            
                            <div className="space-y-1.5">
                                <label className="text-sm font-bold text-surface-700 ml-1">Expertise Goal</label>
                                <select 
                                    className="w-full bg-white/50 border-2 border-surface-100 rounded-2xl p-3 text-sm font-bold focus:border-primary-500 outline-none transition-all cursor-pointer"
                                    value={targetLevel}
                                    onChange={e => setTargetLevel(e.target.value)}
                                >
                                    <option value="beginner">Beginner (Fundamentals)</option>
                                    <option value="intermediate">Intermediate (Standard)</option>
                                    <option value="advanced">Advanced (Deep Dive)</option>
                                    <option value="expert">Expert (Research Level)</option>
                                </select>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-sm font-bold text-surface-700 ml-1">Color Marker</label>
                                <div className="flex gap-2">
                                    {['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#06b6d4', '#8b5cf6'].map(color => (
                                        <button 
                                            key={color}
                                            type="button"
                                            onClick={() => setNewSubjectColor(color)}
                                            className={clsx(
                                                "w-8 h-8 rounded-lg transition-all",
                                                newSubjectColor === color ? "scale-110 ring-2 ring-offset-2 ring-primary-500 shadow-lg" : "scale-100 opacity-60 hover:opacity-100"
                                            )}
                                            style={{ backgroundColor: color }}
                                        />
                                    ))}
                                </div>
                            </div>
                            <div className="flex gap-2 pt-2">
                                <Button type="submit" className="flex-1 py-2 text-sm">Create</Button>
                                <Button variant="secondary" onClick={() => setIsAddingSubject(false)} className="flex-1 py-2 text-sm">Cancel</Button>
                            </div>
                        </form>
                    )}

                    <div className="space-y-3">
                        {subjects.map(s => (
                            <SubjectCard 
                                key={s.id} 
                                subject={s} 
                                active={selectedSubject?.id === s.id}
                                topicCount={s.topic_count || (topicsBySubject[s.id]?.length || 0)}
                                onClick={() => setSelectedSubject(s)} 
                            />
                        ))}
                        {subjects.length === 0 && !isAddingSubject && (
                            <div className="text-center p-12 glass-card border-dashed">
                                <p className="text-sm font-bold text-surface-400 uppercase tracking-widest leading-loose">
                                    No nodes active.<br/>Initialize one now.
                                </p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Topics Detail View */}
                <div className="lg:col-span-8 space-y-8 animate-slide-up">
                    {!selectedSubject ? (
                        <div className="h-[500px] glass-card flex flex-col items-center justify-center text-center p-12 border-dashed border-2">
                            <div className="w-20 h-20 bg-surface-50 rounded-3xl flex items-center justify-center mb-8">
                                <Layers className="w-10 h-10 text-surface-200" />
                            </div>
                            <h3 className="text-2xl font-black text-surface-900 mb-2">Select a Neural Node</h3>
                            <p className="text-surface-400 font-medium max-w-xs">
                                Choose a subject from the left to manage its topics and ingestion parameters.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-8">
                            <div className="glass-card p-10 space-y-10">
                                <div className="flex justify-between items-start">
                                    <div className="flex items-center gap-6">
                                        <div className="w-16 h-16 rounded-3xl flex items-center justify-center shadow-lg border-2 border-white" style={{ backgroundColor: `${selectedSubject.color}20` }}>
                                             <div className="w-5 h-5 rounded-full" style={{ backgroundColor: selectedSubject.color }} />
                                        </div>
                                        <div>
                                            <h3 className="text-3xl font-black text-surface-900 tracking-tight">{selectedSubject.name}</h3>
                                            <p className="text-sm font-bold text-primary-600 uppercase tracking-[0.2em] mt-1 italic">ACTIVE CORE NODE</p>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={() => handleDeleteSubject(selectedSubject.id)}
                                        className="p-3 bg-red-50 text-red-400 hover:text-red-700 hover:bg-red-100 rounded-2xl transition-all group shadow-sm shadow-red-50"
                                    >
                                        <Trash2 className="w-6 h-6 group-hover:rotate-12" />
                                    </button>
                                </div>

                                {/* AI Decomposition Section */}
                                <div className="p-8 bg-gradient-to-br from-primary-50 to-indigo-50 rounded-3xl border-2 border-primary-100 space-y-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-200">
                                                <Brain className="w-5 h-5 text-white" />
                                            </div>
                                            <div>
                                                <div className="font-black uppercase tracking-tight text-surface-900 text-sm">
                                                    AI Curriculum Architect
                                                </div>
                                                <p className="text-[10px] font-bold text-primary-500 uppercase tracking-widest mt-0.5">
                                                    Auto-generate subtopics with AI
                                                </p>
                                            </div>
                                        </div>
                                        <span className="text-[10px] font-black text-primary-400 bg-white px-3 py-1 rounded-full uppercase tracking-widest border border-primary-100">
                                            Powered by AI
                                        </span>
                                    </div>
                                    
                                    <p className="text-sm text-surface-600 font-medium leading-relaxed">
                                        Let our AI analyze <strong>"{selectedSubject.name}"</strong> and automatically generate 
                                        all subtopics in the correct learning order — with difficulty ratings and time estimates.
                                    </p>
                                    
                                    <textarea 
                                        className="w-full bg-white border-2 border-primary-100 rounded-2xl p-4 text-sm font-medium focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 outline-none min-h-[80px] transition-all"
                                        placeholder="Optional context: e.g. 'VTU 5th Semester syllabus' or 'Beginner level, focus on practical applications'"
                                        value={decomposeContext}
                                        onChange={e => setDecomposeContext(e.target.value)}
                                    />
                                    
                                    <Button 
                                        onClick={handleDecompose} 
                                        className="w-full py-4 text-base bg-primary-600 shadow-lg shadow-primary-200" 
                                        isLoading={isDecomposing}
                                    >
                                        <Brain className="w-5 h-5" />
                                        {isDecomposing ? 'Extracting Curriculum Architecture...' : 'AI Decompose Subject'}
                                    </Button>
                                </div>

                                {/* Bulk Add Topics */}
                                <div className="p-8 bg-surface-50/50 rounded-3xl border border-surface-100 space-y-6">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-3 text-surface-900 font-black uppercase tracking-tighter">
                                            <ListPlus className="w-6 h-6 text-primary-600" />
                                            Bulk Concept Ingester
                                        </div>
                                        <span className="text-[10px] font-black text-surface-400 uppercase tracking-widest">Efficiency: 100%</span>
                                    </div>
                                    <textarea 
                                        className="w-full bg-white border-2 border-surface-100 rounded-3xl p-6 text-base font-medium focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 outline-none min-h-[160px] transition-all"
                                        placeholder="Paste your concepts here. One concept per line..."
                                        value={bulkTopicsText}
                                        onChange={e => setBulkTopicsText(e.target.value)}
                                    />
                                    <Button onClick={handleImportTopics} className="w-full py-4 text-base" isLoading={isImporting}>
                                        Ingest Concepts into Node
                                    </Button>
                                </div>

                                {/* Topics List */}
                                <div className="space-y-6">
                                    <div className="flex items-center justify-between px-2">
                                        <h4 className="text-xs font-black text-surface-400 uppercase tracking-[0.3em]">Managed Concepts</h4>
                                        <span className="text-[10px] font-black text-primary-600 bg-primary-100 px-2 py-0.5 rounded-full">{topicsBySubject[selectedSubject.id]?.length || 0} TOTAL</span>
                                    </div>
                                    <div className="grid grid-cols-1 gap-4">
                                        {(topicsBySubject[selectedSubject.id] || []).map(topic => (
                                            <div 
                                                key={topic.id} 
                                                className="group bg-white p-6 rounded-[32px] border-2 border-surface-50 hover:border-primary-100 hover:shadow-2xl hover:shadow-primary-100/20 transition-all relative overflow-hidden"
                                            >
                                                <div className="flex items-center justify-between relative z-10 cursor-pointer" onClick={() => setSelectedTopic(topic)}>
                                                    <div className="flex items-center gap-4">
                                                        <div 
                                                            className="w-10 h-10 rounded-2xl flex items-center justify-center text-white shrink-0"
                                                            style={{ backgroundColor: selectedSubject.color }}
                                                        >
                                                            <BookOpen className="w-5 h-5" />
                                                        </div>
                                                        <div>
                                                            <h4 className="font-bold text-surface-900 group-hover:text-primary-600 transition-colors">{topic.name}</h4>
                                                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                                                                <span className={clsx(
                                                                    "text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full border",
                                                                    topic.difficulty === 'hard' ? "bg-red-50 text-red-500 border-red-100" :
                                                                    topic.difficulty === 'medium' ? "bg-amber-50 text-amber-500 border-amber-100" :
                                                                    "bg-emerald-50 text-emerald-500 border-emerald-100"
                                                                )}>
                                                                    {topic.difficulty}
                                                                </span>
                                                                <span className="text-[9px] font-black text-surface-400 uppercase tracking-widest">
                                                                    {topic.estimated_hours}h EST
                                                                </span>
                                                                {topic.prerequisites?.length > 0 && (
                                                                  <span className="text-[9px] font-black text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-100 flex items-center gap-1">
                                                                     <Layers className="w-2 h-2" />
                                                                     {topic.prerequisites.length} Prereqs
                                                                  </span>
                                                                )}
                                                                {topic.key_concepts?.length > 0 && (
                                                                  <span className="text-[9px] font-black text-primary-600 bg-primary-50 px-2 py-0.5 rounded-full border border-primary-100">
                                                                     {topic.key_concepts.length} Subtopics
                                                                  </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <ChevronRight className="w-5 h-5 text-surface-200 group-hover:text-primary-400 group-hover:translate-x-1 transition-all shrink-0" />
                                                </div>
                                                
                                                {/* Subtopics / Key Concepts */}
                                                {topic.key_concepts?.length > 0 && (
                                                  <div className="mt-4 ml-14 space-y-1.5">
                                                    {topic.key_concepts.map((concept, i) => (
                                                      <div key={i} className="flex items-start gap-2 text-sm text-surface-600">
                                                        <span className="text-primary-400 mt-0.5 shrink-0">›</span>
                                                        <span className="leading-snug">{concept}</span>
                                                      </div>
                                                    ))}
                                                  </div>
                                                )}

                                                {/* Progress Bar Mini */}
                                                <div className="mt-4 h-1.5 w-full bg-surface-50 rounded-full overflow-hidden">
                                                    <div 
                                                        className="h-full bg-primary-500 transition-all duration-500"
                                                        style={{ width: `${topic.knowledge_level * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    {(!topicsBySubject[selectedSubject.id] || topicsBySubject[selectedSubject.id]?.length === 0) && (
                                        <div className="py-20 flex flex-col items-center opacity-30 text-center">
                                            <AlertCircle className="w-12 h-12 mb-4" />
                                            <p className="font-black uppercase text-xs tracking-[0.2em]">Node contains no concept data</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* AI Quick Setup Modal */}
            <QuickSetupModal 
                isOpen={isQuickSetupOpen} 
                onClose={() => setIsQuickSetupOpen(false)}
                onSuccess={() => fetchSubjects()}
            />

            {/* Knowledge Node Modal */}
            <StudyCardModal 
                isOpen={!!selectedTopic}
                onClose={() => setSelectedTopic(null)}
                topicId={selectedTopic?.id}
                topicName={selectedTopic?.name}
                subjectColor={selectedSubject?.color}
            />
        </div>
    )
}

export default CurriculumPage
