import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Brain, Clock, ChevronRight, CheckCircle2, XCircle, Award, ArrowRight, Zap } from 'lucide-react'
import { useTestStore } from '@/store/useTestStore'
import { Button } from '@/components/ui/Button'
import { clsx } from 'clsx'
import toast from 'react-hot-toast'

const TestPage = () => {
  const { topicId } = useParams()
  const navigate = useNavigate()
  const { activeTest, generateTest, submitTest, isLoading, isSubmitting, clearActiveTest } = useTestStore()
  
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState({})
  const [timeLeft, setTimeLeft] = useState(600) // 10 minutes default
  const [isFinished, setIsFinished] = useState(false)
  const [results, setResults] = useState(null)

  useEffect(() => {
    if (topicId) {
      generateTest(topicId)
    }
    return () => clearActiveTest()
  }, [topicId])

  useEffect(() => {
    if (activeTest && !isFinished) {
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timer)
            handleFinish()
            return 0
          }
          return prev - 1
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [activeTest, isFinished])

  const handleAnswerSelect = (index) => {
    setSelectedAnswers({ ...selectedAnswers, [currentQuestionIndex]: index })
  }

  const handleFinish = async () => {
    if (isFinished) return
    
    const questions = activeTest.questions
    let correctCount = 0
    const processedResults = questions.map((q, i) => {
      const isCorrect = selectedAnswers[i] === q.correct_index
      if (isCorrect) correctCount++
      return {
        question_id: q.id,
        selected_index: selectedAnswers[i],
        is_correct: isCorrect
      }
    })

    setIsFinished(true)
    
    try {
      const response = await submitTest({
        topic_id: topicId,
        correct_count: correctCount,
        total_count: questions.length,
        time_seconds: 600 - timeLeft,
        questions_data: processedResults
      })
      setResults({
        correctCount,
        totalCount: questions.length,
        score: response.score_percentage * 100,
        newMastery: response.new_mastery * 100
      })
      toast.success('Cognitive synchronization complete!')
    } catch (err) {
      toast.error('Failed to sync results')
    }
  }

  if (isLoading || !activeTest) {
    return (
      <div className="min-h-screen bg-surface-50 flex flex-col items-center justify-center p-10">
        <div className="w-20 h-20 bg-primary-50 rounded-3xl flex items-center justify-center mb-8 animate-bounce">
            <Brain className="w-10 h-10 text-primary-600" />
        </div>
        <h2 className="text-2xl font-black text-surface-900 tracking-tight mb-2">Extracting Neural Patterns...</h2>
        <p className="text-surface-400 font-bold uppercase tracking-widest text-xs animate-pulse">Initializing adaptive assessment</p>
      </div>
    )
  }

  if (isFinished && results) {
    return (
      <div className="min-h-screen bg-surface-50 p-12 flex items-center justify-center">
        <div className="max-w-xl w-full glass-card p-12 text-center space-y-8 animate-slide-up">
            <div className="inline-flex p-5 bg-emerald-50 rounded-full border-4 border-white shadow-lg">
                <Award className="w-16 h-16 text-emerald-600" />
            </div>
            
            <div>
                <h2 className="text-4xl font-black text-surface-900 tracking-tighter">Assessment Captured</h2>
                <p className="text-surface-400 font-medium mt-2">Topic: {activeTest.topic_name}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="bg-surface-50/80 p-6 rounded-3xl border border-white">
                    <div className="text-3xl font-black text-surface-900">{results.score.toFixed(0)}%</div>
                    <div className="text-[10px] font-black text-surface-400 uppercase tracking-widest mt-1">Accuracy</div>
                </div>
                <div className="bg-primary-50/50 p-6 rounded-3xl border border-primary-100">
                    <div className="text-3xl font-black text-primary-600">{results.newMastery.toFixed(0)}%</div>
                    <div className="text-[10px] font-black text-primary-400 uppercase tracking-widest mt-1">New Mastery</div>
                </div>
            </div>

            <p className="text-sm font-medium text-surface-500 italic max-w-sm mx-auto">
               "Mastery is not a destination, but a continuous curve of optimization."
            </p>

            <div className="pt-4 space-y-3">
                <Button onClick={() => navigate('/')} className="w-full py-4 text-base">Return to Dash Flow</Button>
                <Button variant="secondary" onClick={() => navigate('/analytics')} className="w-full py-4 text-base bg-white">View Neural Insights</Button>
            </div>
        </div>
      </div>
    )
  }

  const currentQuestion = activeTest.questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === activeTest.questions.length - 1

  return (
    <div className="min-h-screen bg-surface-50/50 flex flex-col">
      {/* Test Header */}
      <div className="glass-panel sticky top-0 z-10 px-12 py-6 border-none shadow-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-200">
                <Brain className="text-white w-6 h-6" />
            </div>
            <div>
                <h3 className="text-lg font-black text-surface-900 tracking-tight">{activeTest.topic_name}</h3>
                <p className="text-[9px] font-black text-primary-500 uppercase tracking-[0.2em]">{activeTest.difficulty} Protocol ACTIVE</p>
            </div>
        </div>

        <div className="flex items-center gap-8">
            <div className="flex items-center gap-3 bg-surface-900 px-6 py-2.5 rounded-2xl text-white shadow-xl">
                <Clock className="w-4 h-4 text-primary-400" />
                <span className="font-black tabular-nums text-sm">
                    {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
                </span>
            </div>
            <div className="w-px h-10 bg-surface-100"></div>
            <div className="text-right">
                <div className="text-[10px] font-black text-surface-400 uppercase tracking-widest mb-1">Concept Progression</div>
                <div className="flex gap-1.5 justify-end">
                    {activeTest.questions.map((_, i) => (
                        <div key={i} className={clsx(
                            "h-1.5 rounded-full transition-all duration-300",
                            i === currentQuestionIndex ? "w-8 bg-primary-600" : 
                            selectedAnswers[i] !== undefined ? "w-4 bg-emerald-400" : "w-4 bg-surface-200"
                        )} />
                    ))}
                </div>
            </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-12">
        <div className="max-w-4xl w-full space-y-12">
             <div className="space-y-4 animate-slide-up">
                 <span className="text-[10px] font-black text-primary-600 bg-primary-50 px-3 py-1 rounded-full uppercase tracking-widest">Question {currentQuestionIndex + 1} of {activeTest.questions.length}</span>
                 <h2 className="text-4xl font-black text-surface-900 tracking-tight leading-tight">
                    {currentQuestion.text}
                 </h2>
             </div>

             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-slide-up delay-1">
                {currentQuestion.options.map((option, i) => (
                    <button
                        key={i}
                        onClick={() => handleAnswerSelect(i)}
                        className={clsx(
                            "p-8 rounded-[32px] border-2 text-left transition-all duration-300 relative overflow-hidden group",
                            selectedAnswers[currentQuestionIndex] === i 
                                ? "bg-primary-600 border-primary-600 shadow-2xl shadow-primary-200" 
                                : "bg-white border-white hover:border-primary-100 hover:bg-primary-50/30"
                        )}
                    >
                        <div className="relative z-10 flex items-center gap-6">
                            <div className={clsx(
                                "w-12 h-12 rounded-2xl flex items-center justify-center font-black text-base border-2 transition-all",
                                selectedAnswers[currentQuestionIndex] === i 
                                    ? "bg-white text-primary-600 border-white shadow-lg" 
                                    : "bg-surface-50 text-surface-400 border-surface-100 group-hover:bg-white group-hover:text-primary-600"
                            )}>
                                {String.fromCharCode(65 + i)}
                            </div>
                            <span className={clsx(
                                "text-lg font-bold tracking-tight leading-snug",
                                selectedAnswers[currentQuestionIndex] === i ? "text-white" : "text-surface-700"
                            )}>{option}</span>
                        </div>
                        {selectedAnswers[currentQuestionIndex] === i && (
                            <Zap className="absolute -bottom-6 -right-6 w-24 h-24 text-white opacity-10" />
                        )}
                    </button>
                ))}
             </div>
        </div>
      </div>

      {/* Footer Nav */}
      <div className="p-12 flex justify-between items-center animate-slide-up delay-2">
            <button 
                onClick={() => setCurrentQuestionIndex(prev => Math.max(0, prev - 1))}
                disabled={currentQuestionIndex === 0}
                className={clsx(
                    "px-10 py-4 font-black text-[10px] uppercase tracking-widest text-surface-400 hover:text-surface-900 transition-all",
                    currentQuestionIndex === 0 && "opacity-0 invisible"
                )}
            >
                Previous Node
            </button>

            {isLastQuestion ? (
                <Button 
                    onClick={handleFinish} 
                    isLoading={isSubmitting}
                    disabled={selectedAnswers[currentQuestionIndex] === undefined}
                    className="px-16 py-5 text-base shadow-2xl shadow-primary-200 rounded-[28px]"
                >
                    Finalize Synchronization <Award className="w-6 h-6" />
                </Button>
            ) : (
                <Button 
                    onClick={() => setCurrentQuestionIndex(prev => prev + 1)}
                    disabled={selectedAnswers[currentQuestionIndex] === undefined}
                    className="px-16 py-5 text-base rounded-[28px] group"
                >
                    Continue Progression <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                </Button>
            )}
      </div>
    </div>
  )
}

export default TestPage
