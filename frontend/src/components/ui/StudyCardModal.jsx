import React, { useEffect } from 'react'
import { X, Brain, Zap, BookOpen, ExternalLink, RefreshCw, HelpCircle, Lightbulb } from 'lucide-react'
import { useStudyCardStore } from '@/store/useStudyCardStore'
import { Button } from '@/components/ui/Button'
import { clsx } from 'clsx'
import { motion, AnimatePresence } from 'framer-motion'

const StudyCardModal = ({ isOpen, onClose, topicId, topicName, subjectColor }) => {
  const { cards, fetchCard, regenerateCard, isLoading, isRegenerating } = useStudyCardStore()

  useEffect(() => {
    if (isOpen && topicId) {
      fetchCard(topicId)
    }
  }, [isOpen, topicId])

  if (!isOpen) return null

  const card = cards[topicId]

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10 pointer-events-none">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-surface-900/60 backdrop-blur-md pointer-events-auto"
        />
        
        <motion.div 
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-[40px] shadow-2xl overflow-hidden flex flex-col pointer-events-auto shadow-primary-200/20"
        >
          {/* Header */}
          <div className="p-8 flex items-center justify-between border-b border-surface-50">
            <div className="flex items-center gap-4">
              <div 
                className="w-12 h-12 rounded-2xl flex items-center justify-center shadow-lg"
                style={{ backgroundColor: subjectColor, color: 'white' }}
              >
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-2xl font-black text-surface-900 tracking-tight leading-none">{topicName}</h3>
                <p className="text-[10px] font-black text-surface-400 uppercase tracking-widest mt-2 flex items-center gap-2">
                  <Zap className="w-3 h-3 text-primary-500" />
                  AI-Optimized Knowledge Node
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                onClick={() => regenerateCard(topicId)}
                disabled={isRegenerating || isLoading}
                className="p-3 hover:bg-surface-50 rounded-2xl transition-all text-surface-400 hover:text-primary-600 group"
                title="Regenerate with fresh AI insights"
              >
                <RefreshCw className={clsx("w-5 h-5", isRegenerating && "animate-spin")} />
              </button>
              <button 
                onClick={onClose}
                className="p-3 hover:bg-surface-50 rounded-2xl transition-all text-surface-400 hover:text-surface-900"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar space-y-10">
            {isLoading && !card ? (
              <div className="py-20 flex flex-col items-center justify-center space-y-4 animate-pulse">
                <div className="w-16 h-16 bg-surface-50 rounded-full flex items-center justify-center">
                  <Brain className="w-8 h-8 text-surface-200" />
                </div>
                <div className="h-4 w-48 bg-surface-50 rounded-full"></div>
                <div className="h-3 w-32 bg-surface-50/50 rounded-full"></div>
              </div>
            ) : card ? (
              <>
                {/* Summary Section */}
                <div className="bg-primary-50/30 border-2 border-primary-50 p-8 rounded-[32px] relative overflow-hidden">
                  <div className="relative z-10">
                    <div className="flex items-center gap-2 text-[10px] font-black text-primary-600 uppercase tracking-widest mb-3">
                      <Lightbulb className="w-3 h-3" />
                      Neural Summary
                    </div>
                    <p className="text-lg font-bold text-surface-800 leading-relaxed italic">
                      "{card.summary}"
                    </p>
                  </div>
                  <Brain className="absolute -bottom-10 -right-10 w-40 h-40 text-primary-100/50 pointer-events-none" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  {/* Key Concepts */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-surface-900 rounded-lg flex items-center justify-center">
                        <BookOpen className="w-4 h-4 text-white" />
                      </div>
                      <h4 className="font-black text-surface-900 uppercase tracking-tight">Key Concepts</h4>
                    </div>
                    <ul className="space-y-4">
                      {card.key_concepts.map((concept, i) => (
                        <li key={i} className="flex gap-4 group">
                          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-surface-50 text-[10px] font-black flex items-center justify-center text-surface-400 group-hover:bg-primary-600 group-hover:text-white transition-all">
                            {i + 1}
                          </span>
                          <span className="text-sm font-semibold text-surface-700 leading-relaxed">{concept}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Formulas & Terms */}
                  <div className="space-y-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
                        <Zap className="w-4 h-4 text-white" />
                      </div>
                      <h4 className="font-black text-surface-900 uppercase tracking-tight">Formulas & Definitions</h4>
                    </div>
                    <div className="bg-surface-50 p-6 rounded-[28px] border-2 border-surface-100 font-mono text-xs text-surface-700 space-y-3">
                      {card.formulas.length > 0 ? card.formulas.map((formula, i) => (
                        <div key={i} className="py-2 border-b border-surface-100 last:border-0">
                          {formula}
                        </div>
                      )) : (
                        <div className="text-surface-400 italic">No formulas relevant for this topic.</div>
                      )}
                    </div>
                    
                    {/* Study Tips */}
                    <div className="pt-4 space-y-4">
                       <h4 className="text-[10px] font-black text-surface-400 uppercase tracking-widest pl-1">Strategic Tips</h4>
                       <div className="flex flex-wrap gap-2">
                          {card.study_tips.map((tip, i) => (
                            <div key={i} className="bg-emerald-50 text-emerald-700 px-4 py-2 rounded-xl text-xs font-black border border-emerald-100">
                               {tip}
                            </div>
                          ))}
                       </div>
                    </div>
                  </div>
                </div>

                {/* Resources */}
                <div className="space-y-6">
                   <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                        <ExternalLink className="w-4 h-4 text-white" />
                      </div>
                      <h4 className="font-black text-surface-900 uppercase tracking-tight">Recommended Resources</h4>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                       {card.resources.map((res, i) => (
                         <a 
                            key={i} 
                            href={res.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="p-5 bg-white border-2 border-surface-50 rounded-2xl flex items-center justify-between group hover:border-primary-100 hover:bg-primary-50/20 transition-all"
                          >
                           <div className="flex items-center gap-4">
                              <div className="w-10 h-10 bg-surface-50 rounded-xl flex items-center justify-center group-hover:bg-white">
                                 <BookOpen className="w-5 h-5 text-surface-400 group-hover:text-primary-600" />
                              </div>
                              <div>
                                 <div className="text-sm font-black text-surface-900">{res.title}</div>
                                 <div className="text-[9px] font-black text-primary-500 uppercase tracking-widest mt-0.5">{res.type}</div>
                              </div>
                           </div>
                           <ExternalLink className="w-4 h-4 text-surface-200 group-hover:text-primary-400" />
                         </a>
                       ))}
                    </div>
                </div>

                {/* Practice Section */}
                <div className="space-y-6 pb-10">
                   <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                        <HelpCircle className="w-4 h-4 text-white" />
                      </div>
                      <h4 className="font-black text-surface-900 uppercase tracking-tight">Active Retrieval Problems</h4>
                    </div>
                    <div className="space-y-3">
                       {card.practice_problems.map((prob, i) => (
                         <div key={i} className="p-6 bg-surface-50 rounded-[28px] border-2 border-transparent hover:border-indigo-100 hover:bg-white transition-all">
                            <p className="text-sm font-bold text-surface-700 leading-relaxed italic">
                              "{prob}"
                            </p>
                         </div>
                       ))}
                    </div>
                </div>
              </>
            ) : null}
          </div>

          {/* Footer */}
          <div className="p-8 bg-surface-50/50 flex justify-between items-center border-t border-surface-100">
            <p className="text-[10px] font-black text-surface-400 uppercase tracking-widest">
              Generated via NeuroPlan AI v2.0
            </p>
            <Button onClick={onClose} className="px-10 rounded-2xl">
              Knowledge Captured
            </Button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  )
}

export default StudyCardModal
